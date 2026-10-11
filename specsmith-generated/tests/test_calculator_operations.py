import os
import subprocess
import sys
import time
import urllib.parse
import urllib.request
import unittest


class CalculatorOperationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.port = 8125
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

    def test_addition_updates_result_label(self):
        html = self.post_form("5", "3", "somar")
        self.assert_result(html, "8")

    def test_subtraction_updates_result_label(self):
        html = self.post_form("5", "3", "subtrair")
        self.assert_result(html, "2")

    def test_multiplication_updates_result_label(self):
        html = self.post_form("5", "3", "multiplicar")
        self.assert_result(html, "15")

    def test_division_updates_result_label(self):
        html = self.post_form("9", "3", "dividir")
        self.assert_result(html, "3")

    def test_power_updates_result_label(self):
        html = self.post_form("2", "3", "potencia")
        self.assert_result(html, "8")

    def test_square_root_uses_first_input(self):
        html = self.post_form("9", "123", "raizq")
        self.assert_result(html, "3")

    def test_invalid_numeric_input_preserves_page_and_reports_error(self):
        html = self.post_form("abc", "3", "somar")
        self.assert_result(html, "Resultado")
        self.assertIn('id="error">Invalid numeric input</p>', html)

    def test_division_by_zero_returns_infinity_like_float_behavior(self):
        html = self.post_form("5", "0", "dividir")
        self.assert_result(html, "Infinity")

    def test_negative_square_root_reports_calculation_error(self):
        html = self.post_form("-9", "0", "raizq")
        self.assert_result(html, "Resultado")
        self.assertIn('id="error">Calculation error: math domain error</p>', html)


if __name__ == "__main__":
    unittest.main()
