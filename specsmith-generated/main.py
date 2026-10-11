from html import escape
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs
import math
import os

PAGE_TITLE = "CalculadoraWebForms"


def ignore_event_context(*_args: object) -> None:
    return


def parse_float(raw: str) -> float:
    value = raw.strip()
    if value == "":
        raise ValueError("could not convert string to float: ''")
    return float(value)


def parse_strict_float(raw: str) -> float:
    value = parse_float(raw)
    if math.isinf(value) or math.isnan(value):
        raise ValueError("non-finite float")
    return value


def format_number(value: float) -> str:
    if isinstance(value, float) and math.isnan(value):
        return "NaN"
    if isinstance(value, float) and math.isinf(value):
        return "Infinity" if value > 0 else "-Infinity"
    return format(value, "g")


def calculate_result(operation: str, txt_nro1: str, txt_nro2: str) -> str:
    if operation == "somar":
        return format_number(parse_strict_float(txt_nro1) + parse_strict_float(txt_nro2))
    if operation == "subtrair":
        return format_number(parse_strict_float(txt_nro1) - parse_strict_float(txt_nro2))
    if operation == "multiplicar":
        return format_number(parse_strict_float(txt_nro1) * parse_strict_float(txt_nro2))
    if operation == "dividir":
        numerator = parse_strict_float(txt_nro1)
        denominator = parse_strict_float(txt_nro2)
        if denominator == 0:
            return "Infinity" if numerator >= 0 else "-Infinity"
        return format_number(numerator / denominator)
    if operation == "potencia":
        return format_number(math.pow(parse_strict_float(txt_nro1), parse_strict_float(txt_nro2)))
    if operation == "raizq":
        value = parse_strict_float(txt_nro1)
        return format_number(math.sqrt(value))
    raise KeyError(operation)


def render_home(
    txt_nro1: str = "",
    txt_nro2: str = "",
    result_text: str = "Resultado",
    error_text: str = "",
) -> bytes:
    error_html = (
        f'<p class="error" id="error">{escape(error_text)}</p>' if error_text else ""
    )
    html = f"""<!DOCTYPE html>
<html lang=\"en\">
<head>
  <meta charset=\"utf-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
  <title>{PAGE_TITLE}</title>
  <style>
    body {{ font-family: Arial, sans-serif; margin: 2rem; background: #f5f5f5; color: #222; }}
    main {{ max-width: 32rem; margin: 0 auto; background: white; padding: 1.5rem; border-radius: 0.75rem; box-shadow: 0 2px 12px rgba(0,0,0,0.08); }}
    h1 {{ margin-top: 0; }}
    form {{ display: grid; gap: 0.75rem; }}
    .row {{ display: grid; gap: 0.5rem; }}
    input {{ padding: 0.5rem; font-size: 1rem; }}
    .buttons {{ display: flex; flex-wrap: wrap; gap: 0.5rem; }}
    button {{ padding: 0.55rem 0.9rem; font-size: 0.95rem; cursor: pointer; }}
    .result {{ margin-top: 1rem; font-weight: bold; }}
    .error {{ margin-top: 0.5rem; color: #b00020; font-weight: bold; }}
  </style>
</head>
<body>
  <main>
    <h1>Calculadora</h1>
    <p>Calculator interface loaded through the main web entry point.</p>
    <form method=\"post\">
      <div class=\"row\">
        <label for=\"txtNro1\">Número 1</label>
        <input id=\"txtNro1\" name=\"txtNro1\" type=\"text\" value=\"{escape(txt_nro1, quote=True)}\" />
      </div>
      <div class=\"row\">
        <label for=\"txtNro2\">Número 2</label>
        <input id=\"txtNro2\" name=\"txtNro2\" type=\"text\" value=\"{escape(txt_nro2, quote=True)}\" />
      </div>
      <div class=\"buttons\">
        <button type=\"submit\" name=\"operation\" value=\"somar\">Somar</button>
        <button type=\"submit\" name=\"operation\" value=\"subtrair\">Subtrair</button>
        <button type=\"submit\" name=\"operation\" value=\"multiplicar\">Multiplicar</button>
        <button type=\"submit\" name=\"operation\" value=\"dividir\">Dividir</button>
        <button type=\"submit\" name=\"operation\" value=\"potencia\">Potência</button>
        <button type=\"submit\" name=\"operation\" value=\"raizq\">Raiz Quadrada</button>
      </div>
    </form>
    <div class=\"result\" id=\"lbResultado\">{escape(result_text)}</div>
    {error_html}
  </main>
</body>
</html>"""
    return html.encode("utf-8")


class AppHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        ignore_event_context(self.command, self.path)
        if self.path == "/health":
            body = b"ok"
            self.send_response(200)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return

        if self.path == "/":
            self.respond_html(render_home())
            return

        message = escape(self.path)
        body = f"Not Found: {message}".encode("utf-8")
        self.send_response(404)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self) -> None:
        ignore_event_context(self.command, self.path)
        if self.path != "/":
            self.send_error(404)
            return

        content_length = int(self.headers.get("Content-Length", "0"))
        raw_body = self.rfile.read(content_length).decode("utf-8")
        form = parse_qs(raw_body, keep_blank_values=True)
        txt_nro1 = form.get("txtNro1", [""])[0]
        txt_nro2 = form.get("txtNro2", [""])[0]
        operation = form.get("operation", [""])[0]

        result_text = "Resultado"
        error_text = ""

        try:
            result_text = calculate_result(operation, txt_nro1, txt_nro2)
        except ValueError as exc:
            if str(exc) == "math domain error":
                error_text = f"Calculation error: {exc}"
            else:
                error_text = "Invalid numeric input"
        except OverflowError:
            error_text = "Numeric overflow"
        except KeyError:
            error_text = "Unknown operation"
        except ZeroDivisionError as exc:
            error_text = f"Calculation error: {exc}"
        except ArithmeticError as exc:
            error_text = f"Calculation error: {exc}"
        except Exception as exc:
            error_text = f"Calculation error: {exc}"

        self.respond_html(render_home(txt_nro1, txt_nro2, result_text, error_text))

    def respond_html(self, body: bytes) -> None:
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format: str, *args) -> None:
        return


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "8000"))
    server = ThreadingHTTPServer(("127.0.0.1", port), AppHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
