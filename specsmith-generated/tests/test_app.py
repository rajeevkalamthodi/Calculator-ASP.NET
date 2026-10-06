import threading
import time
import unittest
from html.parser import HTMLParser
from http.client import RemoteDisconnected
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from app import create_server


class ResultParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.capture = False
        self.result = ""

    def handle_starttag(self, tag, attrs):
        if tag == "span" and dict(attrs).get("id") == "lbResultado":
            self.capture = True

    def handle_endtag(self, tag):
        if tag == "span" and self.capture:
            self.capture = False

    def handle_data(self, data):
        if self.capture:
            self.result += data


class CalculatorAppTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = create_server("127.0.0.1", 0)
        cls.port = cls.server.server_address[1]
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        time.sleep(0.05)

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(timeout=2)

    def url(self, path="/"):
        return f"http://127.0.0.1:{self.port}{path}"

    def post(self, data):
        encoded = urlencode(data).encode("utf-8")
        request = Request(self.url("/"), data=encoded, method="POST")
        with urlopen(request) as response:
            return response.status, response.read().decode("utf-8")

    def post_error(self, data):
        encoded = urlencode(data).encode("utf-8")
        request = Request(self.url("/"), data=encoded, method="POST")
        with self.assertRaises((HTTPError, RemoteDisconnected)) as error:
            urlopen(request)
        return error.exception

    def extract_result(self, html):
        parser = ResultParser()
        parser.feed(html)
        return parser.result

    def test_health_endpoint(self):
        with urlopen(self.url("/health")) as response:
            self.assertEqual(response.status, 200)
            self.assertEqual(response.read().decode("utf-8"), "ok")

    def test_page_load_renders_without_result(self):
        with urlopen(self.url("/")) as response:
            html = response.read().decode("utf-8")
            status = response.status
        self.assertEqual(status, 200)
        self.assertIn("Calculator", html)
        self.assertEqual(self.extract_result(html), "")

    def test_addition(self):
        status, html = self.post({"txtNro1": "3", "txtNro2": "4", "operation": "add"})
        self.assertEqual(status, 200)
        self.assertEqual(self.extract_result(html), "7")

    def test_addition_uses_float32_style_result_text(self):
        status, html = self.post({"txtNro1": "0.1", "txtNro2": "0.2", "operation": "add"})
        self.assertEqual(status, 200)
        self.assertEqual(self.extract_result(html), "0.300000012")

    def test_subtraction(self):
        status, html = self.post({"txtNro1": "7", "txtNro2": "4", "operation": "subtract"})
        self.assertEqual(status, 200)
        self.assertEqual(self.extract_result(html), "3")

    def test_multiplication(self):
        status, html = self.post({"txtNro1": "7", "txtNro2": "4", "operation": "multiply"})
        self.assertEqual(status, 200)
        self.assertEqual(self.extract_result(html), "28")

    def test_division(self):
        status, html = self.post({"txtNro1": "8", "txtNro2": "4", "operation": "divide"})
        self.assertEqual(status, 200)
        self.assertEqual(self.extract_result(html), "2")

    def test_division_by_zero_returns_infinity_result(self):
        status, html = self.post({"txtNro1": "1", "txtNro2": "0", "operation": "divide"})
        self.assertEqual(status, 200)
        self.assertEqual(self.extract_result(html), "Infinity")

    def test_zero_divided_by_zero_returns_nan_result(self):
        status, html = self.post({"txtNro1": "0", "txtNro2": "0", "operation": "divide"})
        self.assertEqual(status, 200)
        self.assertEqual(self.extract_result(html), "NaN")

    def test_power(self):
        status, html = self.post({"txtNro1": "2", "txtNro2": "3", "operation": "power"})
        self.assertEqual(status, 200)
        self.assertEqual(self.extract_result(html), "8")

    def test_square_root(self):
        status, html = self.post({"txtNro1": "9", "txtNro2": "0", "operation": "sqrt"})
        self.assertEqual(status, 200)
        self.assertEqual(self.extract_result(html), "3")

    def test_negative_square_root_returns_nan_result(self):
        status, html = self.post({"txtNro1": "-1", "txtNro2": "0", "operation": "sqrt"})
        self.assertEqual(status, 200)
        self.assertEqual(self.extract_result(html), "NaN")

    def test_non_numeric_input_returns_server_error(self):
        error = self.post_error({"txtNro1": "abc", "txtNro2": "1", "operation": "divide"})
        self.assertEqual(getattr(error, "code", 500), 500)

    def test_blank_input_returns_server_error(self):
        error = self.post_error({"txtNro1": "", "txtNro2": "1", "operation": "add"})
        self.assertEqual(getattr(error, "code", 500), 500)

    def test_overflowing_single_precision_input_returns_server_error(self):
        error = self.post_error({"txtNro1": "1e39", "txtNro2": "1", "operation": "multiply"})
        self.assertEqual(getattr(error, "code", 500), 500)


if __name__ == "__main__":
    unittest.main()
