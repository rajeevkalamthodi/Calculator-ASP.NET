from html import escape
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import os

PAGE_TITLE = "CalculadoraWebForms"


def render_home() -> bytes:
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
  </style>
</head>
<body>
  <main>
    <h1>Calculadora</h1>
    <p>Calculator interface loaded through the main web entry point.</p>
    <form>
      <div class=\"row\">
        <label for=\"txtNro1\">Número 1</label>
        <input id=\"txtNro1\" name=\"txtNro1\" type=\"text\" />
      </div>
      <div class=\"row\">
        <label for=\"txtNro2\">Número 2</label>
        <input id=\"txtNro2\" name=\"txtNro2\" type=\"text\" />
      </div>
      <div class=\"buttons\">
        <button type=\"button\">Somar</button>
        <button type=\"button\">Subtrair</button>
        <button type=\"button\">Multiplicar</button>
        <button type=\"button\">Dividir</button>
        <button type=\"button\">Potência</button>
        <button type=\"button\">Raiz Quadrada</button>
      </div>
    </form>
    <div class=\"result\" id=\"lbResultado\">Resultado</div>
  </main>
</body>
</html>"""
    return html.encode("utf-8")


class AppHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        if self.path == "/health":
            body = b"ok"
            self.send_response(200)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return

        if self.path == "/":
            body = render_home()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return

        message = escape(self.path)
        body = f"Not Found: {message}".encode("utf-8")
        self.send_response(404)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
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
