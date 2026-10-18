import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).parents[1] / 'source'))
spec = importlib.util.spec_from_file_location('publish_python', Path(__file__).parents[1] / 'source/publish_python.py')
app = importlib.util.module_from_spec(spec)
spec.loader.exec_module(app)


class PublicationChecks(unittest.TestCase):
    def inputs(self, directory):
        root = Path(directory)
        target = root / 'python'
        target.mkdir()
        (target / 'old.py').write_text('old environment')
        lock = root / 'requirements.txt'
        lock.write_text('example==1.0 --hash=sha256:' + '0' * 64)
        manifest = root / 'wheels.json'
        manifest.write_text(json.dumps([{'file': 'example-1.0-py3-none-any.whl', 'sha256': '0' * 64, 'urls': ['https://mirror.example/wheel']}]))
        argv = ['publish_python.py', '--root', str(target), '--lock', str(lock), '--wheel-manifest', str(manifest),
                '--cache', str(root / 'cache'), '--image', 'sha256:' + '0' * 64, '--import-module', 'example']
        return root, target, argv

    def test_failed_container_import_never_publishes(self):
        with tempfile.TemporaryDirectory() as directory:
            root, target, argv = self.inputs(directory)
            def execute(command, **kwargs):
                if command[0] == 'docker':
                    raise subprocess.CalledProcessError(1, command)
                stage = Path(command[command.index('--target') + 1])
                (stage / 'new.py').write_text('new environment')
            with patch.object(sys, 'argv', argv), patch.object(app, 'download'), patch.object(app, 'run', side_effect=execute):
                with self.assertRaises(subprocess.CalledProcessError):
                    app.main()
            self.assertEqual((target / 'old.py').read_text(), 'old environment')
            self.assertFalse(list(root.glob('.python-stage-*')))
            self.assertFalse(list(root.glob('python.previous.*')))

    def test_verified_publication_keeps_previous_environment(self):
        with tempfile.TemporaryDirectory() as directory:
            root, target, argv = self.inputs(directory)
            calls = []
            def execute(command, **kwargs):
                calls.append(command)
                if command[0] != 'docker':
                    stage = Path(command[command.index('--target') + 1])
                    (stage / 'new.py').write_text('new environment')
            with patch.object(sys, 'argv', argv), patch.object(app, 'download'), patch.object(app, 'run', side_effect=execute):
                app.main()
            self.assertTrue((target / 'new.py').is_file())
            previous = list(root.glob('python.previous.*'))
            self.assertEqual(len(previous), 1)
            self.assertTrue((previous[0] / 'old.py').is_file())
            self.assertIn('--read-only', calls[-1])
            self.assertIn('none', calls[-1])

    def test_unpinned_dependency_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            lock = Path(directory) / 'requirements.txt'
            lock.write_text('example>=1.0')
            with self.assertRaises(ValueError):
                app.verify_lock(lock)


if __name__ == '__main__':
    unittest.main()
