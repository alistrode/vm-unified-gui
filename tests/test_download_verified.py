import hashlib
import importlib.util
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location('download_verified', Path(__file__).parents[1] / 'source/download_verified.py')
app = importlib.util.module_from_spec(spec)
spec.loader.exec_module(app)


class Response:
    def __init__(self, blocks):
        self.blocks = iter(blocks)

    def __enter__(self):
        return self

    def __exit__(self, *args):
        pass

    def read1(self, size):
        return next(self.blocks, b'')


class DownloadChecks(unittest.TestCase):
    def test_slow_source_switches_to_verified_mirror(self):
        payload = b'complete verified package'
        sha = hashlib.sha256(payload).hexdigest()
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / 'package.zip'
            with patch.object(app, 'urlopen', side_effect=[Response([b'x']), Response([payload])]) as network:
                with patch.object(app.time, 'monotonic', side_effect=[0, 9, 10, 10.01, 10.02]):
                    app.download(['https://slow.example/package', 'https://fast.example/package'], target, sha)
            self.assertEqual(target.read_bytes(), payload)
            self.assertEqual(network.call_count, 2)
            self.assertFalse(list(Path(directory).glob('*.part')))

    def test_hash_mismatch_preserves_existing_destination(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / 'package.zip'
            target.write_bytes(b'existing package')
            with patch.object(app, 'urlopen', return_value=Response([b'wrong bytes'])):
                with self.assertRaises(OSError):
                    app.download(['https://mirror.example/package'], target, '0' * 64)
            self.assertEqual(target.read_bytes(), b'existing package')

    def test_valid_cache_never_downloads(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / 'package.zip'
            target.write_bytes(b'cached')
            with patch.object(app, 'urlopen') as network:
                app.download(['https://mirror.example/package'], target, hashlib.sha256(b'cached').hexdigest())
                network.assert_not_called()


if __name__ == '__main__':
    unittest.main()
