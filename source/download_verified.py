"""Download from verified mirrors; abandon a sustained slow source and verify SHA-256."""
import argparse
import hashlib
import os
from pathlib import Path
import tempfile
import time
from urllib.parse import urlsplit
from urllib.request import Request, urlopen


class SlowSource(OSError):
    pass


def checksum(path):
    digest = hashlib.sha256()
    with open(path, 'rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(block)
    return digest.hexdigest()


def download(urls, destination, expected, minimum_kib=800, window_seconds=8, timeout=15):
    destination = Path(destination)
    if destination.is_file() and checksum(destination) == expected:
        print('Verified cache hit:', destination.name, flush=True)
        return destination
    destination.parent.mkdir(parents=True, exist_ok=True)
    errors = []
    for url in urls:
        host = urlsplit(url).hostname
        if urlsplit(url).scheme != 'https':
            errors.append(str(host) + ': HTTPS is required')
            continue
        fd, temp = tempfile.mkstemp(prefix=destination.name + '.', suffix='.part', dir=destination.parent)
        begin = time.monotonic()
        mark, window_bytes, total = begin, 0, 0
        digest = hashlib.sha256()
        try:
            print('Trying source:', host, flush=True)
            with os.fdopen(fd, 'wb') as output, urlopen(Request(url, headers={'User-Agent': 'UnifiedWorkbench/1.0'}), timeout=timeout) as response:
                while True:
                    block = response.read1(64 * 1024)
                    if not block:
                        break
                    output.write(block)
                    digest.update(block)
                    total += len(block)
                    window_bytes += len(block)
                    elapsed = time.monotonic() - mark
                    if elapsed >= window_seconds:
                        speed = window_bytes / elapsed / 1024
                        print(f'{host}: {speed:.0f} KiB/s, {total / 1048576:.1f} MiB received', flush=True)
                        if speed < minimum_kib:
                            raise SlowSource(f'{speed:.0f} KiB/s below {minimum_kib} KiB/s; switching source')
                        mark, window_bytes = time.monotonic(), 0
            if digest.hexdigest() != expected:
                raise ValueError('SHA-256 does not match the pinned manifest')
            os.replace(temp, destination)
            duration = max(0.001, time.monotonic() - begin)
            print(f'Verified {destination.name}: {total / duration / 1024:.0f} KiB/s average', flush=True)
            return destination
        except (OSError, ValueError) as error:
            errors.append(f'{host}: {type(error).__name__}: {error}')
            print('Source rejected:', errors[-1], flush=True)
        finally:
            Path(temp).unlink(missing_ok=True)
    raise OSError('No source completed verification: ' + '; '.join(errors))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--sha256', required=True)
    parser.add_argument('--output', required=True)
    parser.add_argument('--min-kib', type=int, default=800)
    parser.add_argument('urls', nargs='+')
    args = parser.parse_args()
    if len(args.sha256) != 64 or any(c not in '0123456789abcdef' for c in args.sha256):
        parser.error('SHA-256 must be 64 lowercase hexadecimal characters')
    if args.min_kib < 1:
        parser.error('minimum speed must be positive')
    download(args.urls, args.output, args.sha256, args.min_kib)
