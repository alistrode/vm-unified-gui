"""Loopback API for the multi-container workbench. Python standard library only."""
from __future__ import annotations

import argparse
import datetime as dt
import json
import math
import os
from pathlib import Path
import shutil
import socket
import subprocess
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlsplit

IDS = ('A', 'B', 'C')
ROOT = Path(os.environ.get('UNIFIED_ROOT', '/srv/unified'))
COMMANDS = {
    'editor': ['python3', '/app/demo.py', '--app', 'editor'],
    'terminal': ['python3', '/app/demo.py', '--app', 'terminal'],
    'files': ['python3', '/app/demo.py', '--app', 'files'],
}
SNAPSHOT: dict = {}
LOCK = threading.Lock()
ACTIONS = threading.BoundedSemaphore(2)


def run(argv: list[str], timeout: int = 8) -> str:
    return subprocess.run(argv, stdin=subprocess.DEVNULL, capture_output=True,
                          text=True, timeout=timeout, check=True).stdout.strip()


def percent(value) -> float | None:
    try:
        result = float(str(value).rstrip('%'))
        return round(max(0, min(100, result)), 1) if math.isfinite(result) else None
    except (ValueError, TypeError):
        return None


def cpu_ticks() -> tuple[int, int]:
    fields = [int(v) for v in Path('/proc/stat').read_text().splitlines()[0].split()[1:9]]
    return sum(fields), fields[3] + fields[4]


def memory_usage() -> tuple[float, int, int]:
    fields = {}
    for line in Path('/proc/meminfo').read_text().splitlines():
        key, value = line.split(':', 1)
        fields[key] = int(value.strip().split()[0]) * 1024
    total, free = fields['MemTotal'], fields['MemAvailable']
    return round((total - free) * 100 / total, 1), total, free


def containers() -> tuple[list[dict], str | None]:
    result = {cid: {'id': cid, 'running': False, 'cpu_percent': None,
                    'memory': None, 'state': 'unknown'} for cid in IDS}
    try:
        names = ['unified-' + cid.lower() for cid in IDS]
        raw = run(['docker', 'inspect', '--format', '{{json .}}', *names])
        for line in raw.splitlines():
            data = json.loads(line)
            name = data.get('Name', '').lstrip('/')
            cid = name.removeprefix('unified-').upper()
            if cid in result:
                result[cid].update(running=bool(data['State']['Running']),
                                   state=data['State']['Status'],
                                   hostname=data['Config']['Hostname'],
                                   image=data['Image'])
        active = ['unified-' + cid.lower() for cid in IDS if result[cid]['running']]
        if active:
            raw = run(['docker', 'stats', '--no-stream', '--format', '{{json .}}', *active])
            for line in raw.splitlines():
                row = json.loads(line)
                cid = row['Name'].removeprefix('unified-').upper()
                if cid in result:
                    result[cid].update(cpu_percent=percent(row['CPUPerc']),
                                       memory=row.get('MemUsage'),
                                       memory_percent=percent(row.get('MemPerc')))
        return list(result.values()), None
    except (OSError, subprocess.SubprocessError, ValueError, KeyError) as error:
        return list(result.values()), type(error).__name__


def display_ready(port: int) -> bool:
    try:
        with socket.create_connection(('127.0.0.1', port), timeout=1):
            return True
    except OSError:
        return False


def sample_loop(stop: threading.Event, display_port: int):
    previous = None
    while not stop.is_set():
        begin = time.monotonic()
        try:
            ticks = cpu_ticks()
            cpu = None
            if previous and ticks[0] > previous[0]:
                cpu = round(100 * (1 - (ticks[1] - previous[1]) / (ticks[0] - previous[0])), 1)
            previous = ticks
            memory, total, free = memory_usage()
            disk = shutil.disk_usage(ROOT if ROOT.exists() else '/')
            rows, error = containers()
            ready = display_ready(display_port)
            state = {
                'sampled_at': dt.datetime.now(dt.timezone.utc).isoformat(),
                'host': {'cpu_percent': percent(cpu), 'memory_percent': memory,
                         'memory_total_bytes': total, 'memory_available_bytes': free,
                         'disk_percent': round(disk.used * 100 / disk.total, 1),
                         'disk_free_bytes': disk.free, 'load_average': os.getloadavg()},
                'containers': rows, 'display_ready': ready,
                'shared_environment': '只读共享环境' if (ROOT / 'shared').exists() else '共享目录待检查',
                'message': ('容器状态采样失败：' + error) if error else
                           f"{sum(c['running'] for c in rows)} 个容器运行中 · 显示服务{'就绪' if ready else '准备中'}",
                'sampling_seconds': round(time.monotonic() - begin, 2),
            }
            with LOCK:
                SNAPSHOT.clear()
                SNAPSHOT.update(state)
        except (OSError, ValueError, KeyError) as error:
            with LOCK:
                SNAPSHOT.update(sampled_at=dt.datetime.now(dt.timezone.utc).isoformat(),
                                display_ready=False, message='硬件采样失败：' + type(error).__name__)
        stop.wait(max(1, 5 - (time.monotonic() - begin)))


def launch(cid: str, app: str):
    if cid not in IDS or app not in COMMANDS:
        raise ValueError('Unknown container or application')
    if not ACTIONS.acquire(blocking=False):
        raise RuntimeError('已有启动请求正在处理，请稍后重试')
    try:
        name = 'unified-' + cid.lower()
        state = json.loads(run(['docker', 'inspect', '--format', '{{json .State}}', name]))
        if not state.get('Running'):
            raise RuntimeError('容器尚未运行')
        run(['docker', 'exec', '-d', name, *COMMANDS[app]])
    finally:
        ACTIONS.release()


class Handler(BaseHTTPRequestHandler):
    server_version = 'UnifiedWorkbench/1.0'

    def reply(self, code: int, payload: dict):
        body = json.dumps(payload, ensure_ascii=False, allow_nan=False).encode()
        self.send_response(code)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(body)))
        self.send_header('Cache-Control', 'no-store')
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        route = urlsplit(self.path).path
        if route in ('/api/workbench/status', '/api/status'):
            with LOCK:
                state = dict(SNAPSHOT)
            self.reply(200 if state else 503, state or {'error': '正在进行首次采样'})
        elif route == '/health':
            self.reply(200, {'ok': True, 'service': 'unified-workbench'})
        elif route == '/assets/display-bridge.js':
            body = Path(__file__).with_name('display-bridge.js').read_bytes()
            self.send_response(200)
            self.send_header('Content-Type', 'application/javascript; charset=utf-8')
            self.send_header('Content-Length', str(len(body)))
            self.send_header('Cache-Control', 'no-cache')
            self.end_headers()
            self.wfile.write(body)
        elif route in ('/', '/workbench.html'):
            body = Path(__file__).with_name('workbench.html').read_bytes()
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.send_header('Content-Length', str(len(body)))
            self.send_header('Cache-Control', 'no-cache')
            self.end_headers()
            self.wfile.write(body)
        else:
            self.reply(404, {'error': '接口不存在'})

    def do_POST(self):
        if urlsplit(self.path).path not in ('/api/apps/launch', '/api/launch'):
            self.reply(404, {'error': '接口不存在'})
            return
        origin = self.headers.get('Origin')
        if origin and urlsplit(origin).netloc != self.headers.get('Host'):
            self.reply(403, {'error': '来源校验失败'})
            return
        if self.headers.get('Content-Type', '').split(';', 1)[0] != 'application/json':
            self.reply(415, {'error': '请求必须为 JSON'})
            return
        try:
            size = int(self.headers.get('Content-Length', '0'))
            if not 0 < size <= 2048:
                raise ValueError('Invalid payload size')
            payload = json.loads(self.rfile.read(size))
            if not isinstance(payload, dict):
                raise ValueError('Invalid payload')
            launch(payload.get('container'), payload.get('app'))
            self.reply(202, {'launched': True})
        except (ValueError, TypeError, json.JSONDecodeError) as error:
            self.reply(400, {'error': str(error)})
        except (OSError, RuntimeError, subprocess.SubprocessError):
            self.reply(503, {'error': '应用未能启动；请检查容器状态，没有自动重放请求'})


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int, default=8090)
    parser.add_argument('--display-port', type=int, default=14500)
    args = parser.parse_args()
    stop = threading.Event()
    sampler = threading.Thread(target=sample_loop, args=(stop, args.display_port), daemon=True)
    sampler.start()
    server = ThreadingHTTPServer(('127.0.0.1', args.port), Handler)
    server.daemon_threads = True
    try:
        server.serve_forever()
    finally:
        stop.set()
        server.server_close()


if __name__ == '__main__':
    main()
