import os
import subprocess
import sys
import time
import urllib.parse
import urllib.request
import unittest


class CalculatorInvariantTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.port = 8126
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

    def test_page_load_keeps_default_result_text(self):
        with urllib.request.urlopen(f"http://127.0.0.1:{self.port}/", timeout=2) as response:
            html = response.read().decode("utf-8")
        self.assertEqual(response.status, 200)
        self.assertNotIn('id="error"', html)
        self.assert_result(html, "Resultado")

    def test_division_by_zero_uses_current_textbox_values_in_the_result_label(self):
        html = self.post_form("5", "0", "dividir")
        self.assert_result(html, "Infinity")
        self.assertNotIn('id="error"', html)

    def test_negative_square_root_reports_error_and_leaves_default_result(self):
        html = self.post_form("-9", "7", "raizq")
        self.assert_result(html, "Resultado")
        self.assertIn('id="error">Calculation error: math domain error</p>', html)

    def test_power_result_comes_from_base_and_exponent_fields(self):
        html = self.post_form("2", "4", "potencia")
        self.assert_result(html, "16")

    def test_subtraction_uses_both_fields_as_operands(self):
        html = self.post_form("8", "3", "subtrair")
        self.assert_result(html, "5")


if __name__ == "__main__":
    unittest.main()
