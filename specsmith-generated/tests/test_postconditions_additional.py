import os
import subprocess
import sys
import time
import urllib.parse
import urllib.request
import unittest


class CalculatorPostconditionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.port = 8127
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

    def post_form(self, txt_nro1: str, txt_nro2: str, operation: str) -> str:
        body = urllib.parse.urlencode(
            {"txtNro1": txt_nro1, "txtNro2": txt_nro2, "operation": operation}
        ).encode("utf-8")
        request = urllib.request.Request(
            f"http://127.0.0.1:{self.port}/",
            data=body,
            method="POST",
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        with urllib.request.urlopen(request, timeout=2) as response:
            html = response.read().decode("utf-8")
        self.assertEqual(response.status, 200)
        return html

    def assert_result(self, html: str, expected: str) -> None:
        self.assertIn(f'<div class="result" id="lbResultado">{expected}</div>', html)

    def test_division_by_zero_reports_calculation_error_and_keeps_default_result(self):
        html = self.post_form("5", "0", "dividir")
        self.assert_result(html, "Resultado")
        self.assertIn('id="error">Calculation error: float division by zero</p>', html)

    def test_negative_square_root_reports_arithmetic_error_message(self):
        html = self.post_form("-9", "0", "raizq")
        self.assert_result(html, "Resultado")
        self.assertIn(
            'id="error">Calculation error: Function does not accept negative values</p>',
            html,
        )


if __name__ == "__main__":
    unittest.main()
