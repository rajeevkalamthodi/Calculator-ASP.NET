import html
import math
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs


TITLE = "CalculadoraWebForms"


class OverflowException(OverflowError):
    pass


class ArgumentNullException(TypeError):
    pass


def parse_float(value: str | None) -> float:
    if value is None:
        raise ArgumentNullException("Value cannot be null")

    lowered = value.strip().lower()
    if lowered in {"inf", "+inf", "infinity", "+infinity", "-inf", "-infinity", "nan"}:
        raise OverflowException("Value was either too large or too small for a Single.")

    parsed = float(value)
    if math.isinf(parsed):
        raise OverflowException("Value was either too large or too small for a Single.")
    return parsed


def format_result(value: float) -> str:
    return str(value)


def calculate(operation: str, nro1_text: str | None, nro2_text: str | None) -> str:
    if operation == "somar":
        return format_result(parse_float(nro1_text) + parse_float(nro2_text))
    if operation == "subtrair":
        return format_result(parse_float(nro1_text) - parse_float(nro2_text))
    if operation == "multiplicar":
        return format_result(parse_float(nro1_text) * parse_float(nro2_text))
    if operation == "dividir":
        return format_result(parse_float(nro1_text) / parse_float(nro2_text))
    if operation == "potencia":
        return format_result(math.pow(parse_float(nro1_text), parse_float(nro2_text)))
    if operation == "raizq":
        return format_result(math.sqrt(parse_float(nro1_text)))
    raise ValueError("Operação inválida")


def render_page(nro1_text: str = "", nro2_text: str = "", result_text: str = "") -> str:
    escaped_nro1 = html.escape(nro1_text, quote=True)
    escaped_nro2 = html.escape(nro2_text, quote=True)
    escaped_result = html.escape(result_text)
    return f"""<!DOCTYPE html>
<html lang=\"pt-BR\">
<head>
  <meta charset=\"utf-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
  <title>{TITLE}</title>
  <style>
    body {{ font-family: Arial, sans-serif; margin: 2rem; }}
    form {{ max-width: 24rem; display: grid; gap: 0.75rem; }}
    .row {{ display: flex; gap: 0.5rem; flex-wrap: wrap; }}
    input[type=text] {{ padding: 0.5rem; font-size: 1rem; }}
    button {{ padding: 0.5rem 0.75rem; font-size: 1rem; }}
    .resultado {{ font-weight: bold; min-height: 1.5rem; }}
  </style>
</head>
<body>
  <h1>{TITLE}</h1>
  <form method=\"post\" action=\"/calculate\">
    <label for=\"txtNro1\">Número 1</label>
    <input id=\"txtNro1\" name=\"txtNro1\" type=\"text\" value=\"{escaped_nro1}\" />
    <label for=\"txtNro2\">Número 2</label>
    <input id=\"txtNro2\" name=\"txtNro2\" type=\"text\" value=\"{escaped_nro2}\" />
    <div class=\"row\">
      <button type=\"submit\" name=\"operation\" value=\"somar\">Somar</button>
      <button type=\"submit\" name=\"operation\" value=\"subtrair\">Subtrair</button>
      <button type=\"submit\" name=\"operation\" value=\"multiplicar\">Multiplicar</button>
      <button type=\"submit\" name=\"operation\" value=\"dividir\">Dividir</button>
      <button type=\"submit\" name=\"operation\" value=\"potencia\">Potência</button>
      <button type=\"submit\" name=\"operation\" value=\"raizq\">RaizQ</button>
    </div>
    <div>
      <span>Resultado:</span>
      <span id=\"lbResultado\" class=\"resultado\">{escaped_result}</span>
    </div>
  </form>
</body>
</html>
"""


class CalculatorHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        if self.path == "/health":
            self.send_response(200)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.end_headers()
            self.wfile.write(b"ok")
            return

        if self.path == "/" or self.path.startswith("/?"):
            body = render_page().encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return

        self.send_response(404)
        self.end_headers()

    def do_POST(self) -> None:
        if self.path != "/calculate":
            self.send_response(404)
            self.end_headers()
            return

        content_length = int(self.headers.get("Content-Length", "0"))
        payload = self.rfile.read(content_length).decode("utf-8")
        form = parse_qs(payload, keep_blank_values=True)
        nro1_text = form.get("txtNro1", [""])[0]
        nro2_text = form.get("txtNro2", [""])[0]
        operation = form.get("operation", [""])[0]
        result_text = calculate(operation, nro1_text, nro2_text)
        body = render_page(nro1_text, nro2_text, result_text).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format: str, *args) -> None:
        return


def run_server() -> None:
    port = int(os.environ.get("PORT", "8000"))
    server = ThreadingHTTPServer(("127.0.0.1", port), CalculatorHandler)
    server.serve_forever()
