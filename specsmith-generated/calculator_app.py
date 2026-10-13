import html
import math
import os
from decimal import Decimal, InvalidOperation
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs


TITLE = "CalculadoraWebForms"


def parse_number(raw_value: str) -> Decimal:
    if raw_value is None:
        raise TypeError("None is not a valid number")
    try:
        return Decimal(raw_value)
    except InvalidOperation as exc:
        raise ValueError(f"Invalid numeric input: {raw_value}") from exc


def decimal_to_result_text(value: Decimal) -> str:
    normalized = value.normalize()
    if normalized == normalized.to_integral():
        normalized = normalized.quantize(Decimal("1"))
    return format(normalized, "f")


def render_page(values: dict[str, str], result: str = "", error: str = "") -> str:
    first = html.escape(values.get("txtNro1", ""))
    second = html.escape(values.get("txtNro2", ""))
    result_text = html.escape(result)
    error_text = html.escape(error)
    return f"""<!DOCTYPE html>
<html lang=\"en\">
<head>
  <meta charset=\"utf-8\" />
  <title>{TITLE}</title>
</head>
<body>
  <h1>{TITLE}</h1>
  <form method=\"post\" action=\"/calculate\">
    <label for=\"txtNro1\">Número 1</label>
    <input id=\"txtNro1\" name=\"txtNro1\" value=\"{first}\" />
    <label for=\"txtNro2\">Número 2</label>
    <input id=\"txtNro2\" name=\"txtNro2\" value=\"{second}\" />
    <div>
      <button type=\"submit\" name=\"operation\" value=\"somar\">Somar</button>
      <button type=\"submit\" name=\"operation\" value=\"subtrair\">Subtrair</button>
      <button type=\"submit\" name=\"operation\" value=\"multiplicar\">Multiplicar</button>
      <button type=\"submit\" name=\"operation\" value=\"dividir\">Dividir</button>
      <button type=\"submit\" name=\"operation\" value=\"potencia\">Potência</button>
      <button type=\"submit\" name=\"operation\" value=\"raizq\">Raiz Quadrada</button>
    </div>
    <p id=\"lbResultado\">{result_text}</p>
    <p id=\"error\">{error_text}</p>
  </form>
</body>
</html>
"""


def calculate(operation: str, first_raw: str, second_raw: str) -> str:
    first = parse_number(first_raw)
    second = parse_number(second_raw) if operation != "raizq" else None

    if operation == "somar":
        return decimal_to_result_text(first + second)
    if operation == "subtrair":
        return decimal_to_result_text(first - second)
    if operation == "multiplicar":
        return decimal_to_result_text(first * second)
    if operation == "dividir":
        return decimal_to_result_text(first / second)
    if operation == "potencia":
        power = Decimal(str(math.pow(float(first), float(second))))
        return decimal_to_result_text(power)
    if operation == "raizq":
        root = Decimal(str(math.sqrt(float(first))))
        return decimal_to_result_text(root)
    raise ValueError(f"Unknown operation: {operation}")


class CalculatorHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/health":
            self.send_response(200)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.end_headers()
            self.wfile.write(b"ok")
            return
        if self.path == "/":
            page = render_page({})
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(page.encode("utf-8"))
            return
        self.send_response(404)
        self.end_headers()

    def do_POST(self):
        if self.path != "/calculate":
            self.send_response(404)
            self.end_headers()
            return

        length = int(self.headers.get("Content-Length", "0"))
        body = self.rfile.read(length).decode("utf-8")
        form = parse_qs(body, keep_blank_values=True)
        values = {
            "txtNro1": form.get("txtNro1", [""])[0],
            "txtNro2": form.get("txtNro2", [""])[0],
        }
        operation = form.get("operation", [""])[0]

        try:
            result = calculate(operation, values["txtNro1"], values["txtNro2"])
            page = render_page(values, result=result)
            self.send_response(200)
        except Exception as exc:
            page = render_page(values, error=f"{exc.__class__.__name__}: {exc}")
            self.send_response(400)

        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(page.encode("utf-8"))


def run():
    port = int(os.environ.get("PORT", "8000"))
    server = ThreadingHTTPServer(("127.0.0.1", port), CalculatorHandler)
    server.serve_forever()
