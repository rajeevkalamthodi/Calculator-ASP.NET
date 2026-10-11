import os
import subprocess
import sys
import time
import urllib.request
import unittest


class EntryPointTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.port = 8123
        env = os.environ.copy()
        env["PORT"] = str(cls.port)
        cls.server = subprocess.Popen(
            [sys.executable, "main.py"],
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        deadline = time.time() + 10
        last_error = None
        while time.time() < deadline:
            try:
                with urllib.request.urlopen(f"http://127.0.0.1:{cls.port}/health", timeout=1) as response:
                    if response.status == 200:
                        return
            except Exception as exc:
                last_error = exc
                time.sleep(0.1)

        cls.tearDownClass()
        raise AssertionError(f"Server did not become ready: {last_error}")

    @classmethod
    def tearDownClass(cls):
        server = getattr(cls, "server", None)
        if server is not None and server.poll() is None:
            server.terminate()
            try:
                server.wait(timeout=5)
            except subprocess.TimeoutExpired:
                server.kill()
                server.wait(timeout=5)

    def test_health_endpoint_returns_ok(self):
        with urllib.request.urlopen(f"http://127.0.0.1:{self.port}/health", timeout=2) as response:
            body = response.read().decode("utf-8")
        self.assertEqual(response.status, 200)
        self.assertEqual(body, "ok")

    def test_root_entry_point_loads_calculator_page(self):
        with urllib.request.urlopen(f"http://127.0.0.1:{self.port}/", timeout=2) as response:
            body = response.read().decode("utf-8")
        self.assertEqual(response.status, 200)
        self.assertIn("<h1>Calculadora</h1>", body)
        self.assertIn("txtNro1", body)
        self.assertIn("txtNro2", body)
        self.assertIn("Somar", body)
        self.assertIn("Resultado", body)


if __name__ == "__main__":
    unittest.main()
