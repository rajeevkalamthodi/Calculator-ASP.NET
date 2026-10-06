"""Standard-library web application for CalculadoraWebForms.

The isolated verification environment does not install third-party Python
packages, so this backend is implemented using only the Python standard
library (wsgiref / http). It serves the React single-page calculator and
exposes a JSON endpoint that performs the arithmetic operations originally
implemented in the ASP.NET Web Forms code-behind (index.aspx.cs).

A small Flask-compatible surface (``create_app()`` returning an app object
with ``.config``, ``.test_client()`` and route handling) is provided so the
regression tests and WSGI runtime share one implementation.
"""

import json
import os
from wsgiref.simple_server import make_server

from calculator import (
    OPERATIONS,
    CalculationError,
    FormatError,
    calculate,
)

STATIC_DIR = os.environ.get(
    "FRONTEND_DIST",
    os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "frontend", "dist")
    ),
)

_CONTENT_TYPES = {
    ".html": "text/html; charset=utf-8",
    ".js": "text/javascript; charset=utf-8",
    ".css": "text/css; charset=utf-8",
    ".json": "application/json",
    ".svg": "image/svg+xml",
    ".ico": "image/x-icon",
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".map": "application/json",
    ".woff": "font/woff",
    ".woff2": "font/woff2",
    ".txt": "text/plain; charset=utf-8",
}


class _Response:
    """Minimal response object mimicking the slice of Flask's Response used here."""

    def __init__(self, status_code, headers, body):
        self.status_code = status_code
        self.headers = headers
        # body is always bytes
        self.data = body if isinstance(body, bytes) else str(body).encode("utf-8")

    def get_json(self):
        try:
            return json.loads(self.data.decode("utf-8"))
        except (ValueError, UnicodeDecodeError):
            return None

    def get_data(self, as_text=False):
        if as_text:
            return self.data.decode("utf-8")
        return self.data


def _json_response(payload, status_code=200):
    body = json.dumps(payload).encode("utf-8")
    headers = {"Content-Type": "application/json"}
    return status_code, headers, body


def _safe_static_path(path):
    """Resolve a URL path to a file inside STATIC_DIR, preventing traversal."""
    rel = path.lstrip("/")
    if not rel:
        rel = "index.html"
    candidate = os.path.abspath(os.path.join(STATIC_DIR, rel))
    static_root = os.path.abspath(STATIC_DIR)
    if candidate != static_root and not candidate.startswith(
        static_root + os.sep
    ):
        return None
    return candidate


def _serve_static(path):
    candidate = _safe_static_path(path)
    if candidate and os.path.isfile(candidate):
        with open(candidate, "rb") as fh:
            body = fh.read()
        ext = os.path.splitext(candidate)[1].lower()
        ctype = _CONTENT_TYPES.get(ext, "application/octet-stream")
        return 200, {"Content-Type": ctype}, body
    return None


def _serve_index():
    index_path = os.path.join(STATIC_DIR, "index.html")
    if os.path.isfile(index_path):
        with open(index_path, "rb") as fh:
            body = fh.read()
        return 200, {"Content-Type": "text/html; charset=utf-8"}, body
    return None


def _handle_calculate(body_bytes):
    try:
        data = json.loads(body_bytes.decode("utf-8")) if body_bytes else {}
    except (ValueError, UnicodeDecodeError):
        data = {}
    if not isinstance(data, dict):
        data = {}

    operation = data.get("operation")
    nro1 = data.get("nro1")
    nro2 = data.get("nro2")

    if operation not in OPERATIONS:
        return _json_response({"error": "Unknown operation."}, 400)

    try:
        result = calculate(operation, nro1, nro2)
    except FormatError as exc:
        return _json_response({"error": str(exc)}, 400)
    except CalculationError as exc:
        return _json_response({"error": str(exc)}, 400)
    except ValueError as exc:
        return _json_response({"error": str(exc)}, 400)

    return _json_response({"result": result})


def _route(method, path, body_bytes):
    """Core request router shared by the WSGI app and the test client."""
    if path == "/health" and method == "GET":
        return _json_response({"status": "ok"})

    if path == "/api/calculate" and method == "POST":
        return _handle_calculate(body_bytes)

    if method == "GET":
        served = _serve_static(path)
        if served is not None:
            return served
        # SPA fallback: serve index.html for unknown GET routes.
        index = _serve_index()
        if index is not None:
            return index
        return _json_response(
            {"status": "ok", "message": "CalculadoraWebForms API"}
        )

    return _json_response({"error": "Not found"}, 404)


class _TestResponseClient:
    """A tiny test client compatible with the subset of Flask used in tests."""

    def post(self, path, json=None, data=None, **kwargs):
        if json is not None:
            body = _json_module_dumps(json)
        elif data is not None:
            body = data if isinstance(data, bytes) else str(data).encode("utf-8")
        else:
            body = b""
        status, headers, out = _route("POST", path, body)
        return _Response(status, headers, out)

    def get(self, path, **kwargs):
        status, headers, out = _route("GET", path, b"")
        return _Response(status, headers, out)

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False


def _json_module_dumps(obj):
    return json.dumps(obj).encode("utf-8")


class _App:
    """WSGI application object with a minimal Flask-compatible surface."""

    def __init__(self):
        self.config = {}

    def test_client(self):
        return _TestResponseClient()

    def __call__(self, environ, start_response):
        method = environ.get("REQUEST_METHOD", "GET")
        path = environ.get("PATH_INFO", "/") or "/"

        body_bytes = b""
        if method in ("POST", "PUT", "PATCH"):
            try:
                length = int(environ.get("CONTENT_LENGTH") or 0)
            except (TypeError, ValueError):
                length = 0
            if length > 0:
                body_bytes = environ["wsgi.input"].read(length)

        status_code, headers, body = _route(method, path, body_bytes)
        status_line = "%d %s" % (status_code, _status_text(status_code))
        response_headers = list(headers.items())
        response_headers.append(("Content-Length", str(len(body))))
        start_response(status_line, response_headers)
        return [body]


_STATUS_TEXT = {
    200: "OK",
    400: "Bad Request",
    404: "Not Found",
    500: "Internal Server Error",
}


def _status_text(code):
    return _STATUS_TEXT.get(code, "OK")


def create_app():
    """Build and return the WSGI application object."""
    return _App()


app = create_app()


if __name__ == "__main__":
    import sys

    port = None
    for arg in sys.argv[1:]:
        if arg.isdigit():
            port = int(arg)
            break
        if arg.startswith("--port="):
            port = int(arg.split("=", 1)[1])
            break
    if port is None:
        port = int(os.environ.get("PORT", "5000"))
    httpd = make_server("127.0.0.1", port, app)
    print("CalculadoraWebForms serving on http://127.0.0.1:%d" % port)
    httpd.serve_forever()
