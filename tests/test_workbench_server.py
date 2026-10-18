import importlib.util
import json
from pathlib import Path
import threading
import unittest
from unittest.mock import patch
from urllib.error import HTTPError
from urllib.request import Request, urlopen

spec = importlib.util.spec_from_file_location('workbench', Path(__file__).parents[1] / 'source/workbench_server.py')
app = importlib.util.module_from_spec(spec)
spec.loader.exec_module(app)


class CommandSafety(unittest.TestCase):
    def test_unknown_targets_never_reach_docker(self):
        with patch.object(app, 'run') as run:
            for cid, command in [('A;id', 'editor'), ('A', 'bash'), ('../../A', 'files'), ('A', None)]:
                with self.assertRaises(ValueError):
                    app.launch(cid, command)
            run.assert_not_called()

    def test_fixed_argv_and_container_running(self):
        with patch.object(app, 'run', side_effect=['{"Running":true}', '']) as run:
            app.launch('B', 'terminal')
            self.assertEqual(run.call_args_list[1].args[0],
                             ['docker', 'exec', '-d', 'unified-b', 'python3', '/app/demo.py', '--app', 'terminal'])
        with patch.object(app, 'run', return_value='{"Running":false}'):
            with self.assertRaises(RuntimeError):
                app.launch('B', 'terminal')

    def test_invalid_metrics_remain_unknown(self):
        self.assertIsNone(app.percent('nan'))
        self.assertIsNone(app.percent(None))
        self.assertEqual(app.percent('12.5%'), 12.5)


class HTTPContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = app.ThreadingHTTPServer(('127.0.0.1', 0), app.Handler)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.url = 'http://127.0.0.1:' + str(cls.server.server_port)

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join()

    def test_health_and_html(self):
        with urlopen(self.url + '/health') as response:
            self.assertTrue(json.load(response)['ok'])
        with urlopen(self.url + '/') as response:
            self.assertIn('容器工作台', response.read().decode())

    def test_cross_origin_write_rejected_before_launch(self):
        request = Request(self.url + '/api/apps/launch', data=b'{"container":"A","app":"editor"}',
                          headers={'Origin': 'http://untrusted.example', 'Content-Type': 'application/json'})
        with patch.object(app, 'launch') as launch:
            with self.assertRaises(HTTPError) as result:
                urlopen(request)
            self.assertEqual(result.exception.code, 403)
            launch.assert_not_called()

    def test_accepted_request_executes_once(self):
        request = Request(self.url + '/api/apps/launch', data=b'{"container":"C","app":"files"}',
                          headers={'Content-Type': 'application/json'})
        with patch.object(app, 'launch') as launch:
            with urlopen(request) as response:
                self.assertEqual(response.status, 202)
            launch.assert_called_once_with('C', 'files')


if __name__ == '__main__':
    unittest.main()
