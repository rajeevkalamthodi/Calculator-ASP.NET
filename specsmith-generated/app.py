from __future__ import annotations

import math
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs

HTML_TEMPLATE = """<!doctype html>
<html lang=\"en\">
<head>
  <meta charset=\"utf-8\">
  <title>Calculadora Web Forms</title>
  <style>
    body { font-family: Arial, sans-serif; margin: 2rem; }
    form { display: grid; gap: 0.75rem; max-width: 28rem; }
    .row { display: flex; gap: 0.5rem; align-items: center; flex-wrap: wrap; }
    label { min-width: 5rem; }
    input[type=text] { padding: 0.35rem; width: 12rem; }
    .actions { display: flex; gap: 0.5rem; flex-wrap: wrap; }
    .result { font-weight: bold; }
  </style>
</head>
<body>
  <h1>Calculator</h1>
  <form method=\"post\" action=\"/\">
    <div class=\"row\">
      <label for=\"txtNro1\">Number 1</label>
      <input id=\"txtNro1\" name=\"txtNro1\" type=\"text\" value=\"{value1}\">
    </div>
    <div class=\"row\">
      <label for=\"txtNro2\">Number 2</label>
      <input id=\"txtNro2\" name=\"txtNro2\" type=\"text\" value=\"{value2}\">
    </div>
    <div class=\"actions\">
      <button type=\"submit\" name=\"operation\" value=\"add\">Somar</button>
      <button type=\"submit\" name=\"operation\" value=\"subtract\">Subtrair</button>
      <button type=\"submit\" name=\"operation\" value=\"multiply\">Multiplicar</button>
      <button type=\"submit\" name=\"operation\" value=\"divide\">Dividir</button>
      <button type=\"submit\" name=\"operation\" value=\"power\">Potência</button>
      <button type=\"submit\" name=\"operation\" value=\"sqrt\">RaizQ</button>
    </div>
    <div class=\"result\">Resultado: <span id=\"lbResultado\">{result}</span></div>
  </form>
</body>
</html>
"""


def parse_float(value: str) -> float:
    return float(value)


def format_number(value: float) -> str:
    if math.isnan(value):
        return "nan"
    if math.isinf(value):
        return "inf" if value > 0 else "-inf"
    return str(value)


def calculate(operation: str, value1: str, value2: str) -> str:
    if operation == "add":
        return format_number(parse_float(value1) + parse_float(value2))
    if operation == "subtract":
        return format_number(parse_float(value1) - parse_float(value2))
    if operation == "multiply":
        return format_number(parse_float(value1) * parse_float(value2))
    if operation == "divide":
        divisor = parse_float(value2)
        dividend = parse_float(value1)
        if divisor == 0.0:
            if dividend == 0.0:
                return format_number(float("nan"))
            return format_number(float("inf") if dividend > 0 else float("-inf"))
        return format_number(dividend / divisor)
    if operation == "power":
        return format_number(parse_float(value1) ** parse_float(value2))
    if operation == "sqrt":
        return format_number(math.sqrt(parse_float(value1)))
    return ""


class CalculatorHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        if self.path == "/health":
            self.respond(200, "text/plain; charset=utf-8", b"ok")
            return
        if self.path != "/":
            self.respond(404, "text/plain; charset=utf-8", b"Not Found")
            return
        self.render_page("", "", "")

    def do_POST(self) -> None:
        if self.path != "/":
            self.respond(404, "text/plain; charset=utf-8", b"Not Found")
            return

        length = int(self.headers.get("Content-Length", "0"))
        body = self.rfile.read(length).decode("utf-8")
        form = parse_qs(body, keep_blank_values=True)
        value1 = form.get("txtNro1", [""])[0]
        value2 = form.get("txtNro2", [""])[0]
        operation = form.get("operation", [""])[0]

        try:
            result = calculate(operation, value1, value2)
            self.render_page(value1, value2, result)
        except Exception as exc:  # preserve failure surface as server error for invalid inputs
            self.respond(500, "text/plain; charset=utf-8", str(exc).encode("utf-8", errors="replace"))

    def render_page(self, value1: str, value2: str, result: str) -> None:
        page = HTML_TEMPLATE.format(
            value1=escape_html(value1),
            value2=escape_html(value2),
            result=escape_html(result),
        ).encode("utf-8")
        self.respond(200, "text/html; charset=utf-8", page)

    def respond(self, status: int, content_type: str, body: bytes) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format: str, *args) -> None:
        return


def escape_html(value: str) -> str:
    return (
        value.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def create_server(host: str = "127.0.0.1", port: int = 8000) -> ThreadingHTTPServer:
    return ThreadingHTTPServer((host, port), CalculatorHandler)


if __name__ == "__main__":
    server = create_server()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
