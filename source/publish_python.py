"""Publish a complete, hash-locked shared Python environment after container import checks."""
import argparse
import datetime as dt
import fcntl
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile

from download_verified import download


def run(argv, **kwargs):
    return subprocess.run(argv, check=True, stdin=subprocess.DEVNULL, **kwargs)


def verify_lock(path):
    lines = path.read_text().splitlines()
    records, pending = [], ''
    for line in lines:
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        pending += ' ' + line.rstrip('\\').strip()
        if line.endswith('\\'):
            continue
        records.append(pending.strip())
        pending = ''
    if pending or not records:
        raise ValueError('Requirements must contain complete pinned records')
    for record in records:
        if not re.match(r'^[A-Za-z0-9_.-]+==[^\s;]+\s+', record):
            raise ValueError('Every dependency must use an exact version')
        if not re.search(r'--hash=sha256:[0-9a-f]{64}(?:\s|$)', record):
            raise ValueError('Every dependency must include a SHA-256 hash')
    return records


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--root', type=Path, default=Path('/srv/unified/shared/user/python'))
    parser.add_argument('--lock', type=Path, required=True)
    parser.add_argument('--wheel-manifest', type=Path, required=True)
    parser.add_argument('--cache', type=Path, default=Path('/srv/unified/shared/cache/wheels'))
    parser.add_argument('--image', required=True, help='Pinned shared OCI image ID, sha256:...')
    parser.add_argument('--import-module', action='append', required=True)
    args = parser.parse_args()
    if not re.fullmatch(r'sha256:[a-f0-9]{64}', args.image):
        parser.error('Use the exact shared image SHA-256, not a mutable tag')
    if any(not re.fullmatch(r'[A-Za-z_]\w*(?:\.[A-Za-z_]\w*)*', name) for name in args.import_module):
        parser.error('Import names must be dotted Python module identifiers')
    verify_lock(args.lock)
    target = args.root.absolute()
    if target.is_symlink():
        parser.error('Refusing to replace a symlinked environment root')
    target.parent.mkdir(parents=True, exist_ok=True)
    args.cache.mkdir(parents=True, exist_ok=True)
    with (target.parent / '.python-publish.lock').open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        wheels = json.loads(args.wheel_manifest.read_text())
        if not isinstance(wheels, list) or not wheels:
            raise ValueError('Wheel manifest must be a nonempty list')
        for wheel in wheels:
            name, sha = wheel['file'], wheel['sha256']
            if Path(name).name != name or not name.endswith('.whl') or not re.fullmatch('[a-f0-9]{64}', sha):
                raise ValueError('Invalid pinned wheel entry')
            download(wheel['urls'], args.cache / name, sha, minimum_kib=800)
        stage = Path(tempfile.mkdtemp(prefix='.python-stage-', dir=target.parent))
        previous = target.parent / ('python.previous.' + dt.datetime.now(dt.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ'))
        swapped = False
        try:
            run([sys.executable, '-m', 'pip', 'install', '--no-input', '--disable-pip-version-check',
                 '--no-index', '--find-links', str(args.cache), '--require-hashes', '--only-binary=:all:',
                 '--no-compile', '--target', str(stage), '-r', str(args.lock)])
            # Keep this project's existing shared helper separate from third-party dependency resolution.
            helper = target / 'sharedkit'
            if helper.is_dir() and not helper.is_symlink():
                shutil.copytree(helper, stage / 'sharedkit', dirs_exist_ok=True, ignore=shutil.ignore_patterns('__pycache__'))
            stage.chmod(0o755)
            code = 'import importlib,json,sys; [importlib.import_module(n) for n in json.loads(sys.argv[1])]; print("Shared imports verified")'
            run(['docker', 'run', '--rm', '--network', 'none', '--read-only', '--cap-drop', 'ALL',
                 '--security-opt', 'no-new-privileges', '--user', '1000:1000', '--pids-limit', '64',
                 '--memory', '256m', '--cpus', '0.25', '--tmpfs', '/tmp:rw,size=16m',
                 '-v', str(stage) + ':/opt/shared-user/python:ro', '-e', 'PYTHONPATH=/opt/shared-user/python',
                 args.image, 'python3', '-c', code, json.dumps(args.import_module)], timeout=120)
            # Both paths are siblings on one filesystem. Running containers retain their old read-only mount.
            if target.exists():
                os.rename(target, previous)
            try:
                os.rename(stage, target)
                swapped = True
            except BaseException:
                if previous.exists() and not target.exists():
                    os.rename(previous, target)
                raise
            print(json.dumps({'published': True, 'root': str(target),
                              'previous': str(previous) if previous.exists() else None,
                              'imports_verified': args.import_module,
                              'application_restart_required': True}, ensure_ascii=False))
        finally:
            if not swapped and stage.exists():
                shutil.rmtree(stage)


if __name__ == '__main__':
    main()
