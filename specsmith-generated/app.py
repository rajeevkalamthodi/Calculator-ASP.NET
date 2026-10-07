from __future__ import annotations

import json
import math
import os
from dataclasses import dataclass
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs

CONFIG_PATH = Path(__file__).with_name("app_config.json")


@dataclass(frozen=True)
class AppConfig:
    runtime_host: str
    runtime_port: int
    title: str
    heading: str
    label_number1: str
    label_number2: str
    result_label: str
    button_add: str
    button_subtract: str
    button_multiply: str
    button_divide: str
    button_power: str
    button_sqrt: str


class FloatOverflowError(OverflowError):
    pass


def load_config(config_path: Path | None = None) -> AppConfig:
    path = config_path or CONFIG_PATH
    with path.open("r", encoding="utf-8") as config_file:
        raw = json.load(config_file)

    runtime = raw["runtime"]
    ui = raw["ui"]
    labels = ui["labels"]
    buttons = ui["buttons"]

    return AppConfig(
        runtime_host=str(runtime["host"]),
        runtime_port=int(runtime["port"]),
        title=str(ui["title"]),
        heading=str(ui["heading"]),
        label_number1=str(labels["number1"]),
        label_number2=str(labels["number2"]),
        result_label=str(labels["result"]),
        button_add=str(buttons["add"]),
        button_subtract=str(buttons["subtract"]),
        button_multiply=str(buttons["multiply"]),
        button_divide=str(buttons["divide"]),
        button_power=str(buttons["power"]),
        button_sqrt=str(buttons["sqrt"]),
    )


APP_CONFIG = load_config()

HTML_TEMPLATE = """<!doctype html>
<html lang=\"en\">
<head>
  <meta charset=\"utf-8\">
  <title>{title}</title>
  <style>
    body {{ font-family: Arial, sans-serif; margin: 2rem; }}
    form {{ display: grid; gap: 0.75rem; max-width: 28rem; }}
    .row {{ display: flex; gap: 0.5rem; align-items: center; flex-wrap: wrap; }}
    label {{ min-width: 5rem; }}
    input[type=text] {{ padding: 0.35rem; width: 12rem; }}
    .actions {{ display: flex; gap: 0.5rem; flex-wrap: wrap; }}
    .result {{ font-weight: bold; }}
    .config {{ margin-top: 1rem; color: #444; font-size: 0.95rem; }}
  </style>
</head>
<body>
  <h1>{heading}</h1>
  <form method=\"post\" action=\"/\">
    <div class=\"row\">
      <label for=\"txtNro1\">{label_number1}</label>
      <input id=\"txtNro1\" name=\"txtNro1\" type=\"text\" value=\"{value1}\">
    </div>
    <div class=\"row\">
      <label for=\"txtNro2\">{label_number2}</label>
      <input id=\"txtNro2\" name=\"txtNro2\" type=\"text\" value=\"{value2}\">
    </div>
    <div class=\"actions\">
      <button type=\"submit\" name=\"operation\" value=\"add\">{button_add}</button>
      <button type=\"submit\" name=\"operation\" value=\"subtract\">{button_subtract}</button>
      <button type=\"submit\" name=\"operation\" value=\"multiply\">{button_multiply}</button>
      <button type=\"submit\" name=\"operation\" value=\"divide\">{button_divide}</button>
      <button type=\"submit\" name=\"operation\" value=\"power\">{button_power}</button>
      <button type=\"submit\" name=\"operation\" value=\"sqrt\">{button_sqrt}</button>
    </div>
    <div class=\"result\">{result_label}: <span id=\"lbResultado\">{result}</span></div>
  </form>
  <div class=\"config\">Runtime default: <span id=\"configRuntimeHost\">{runtime_host}</span>:<span id=\"configRuntimePort\">{runtime_port}</span></div>
</body>
</html>
"""


def parse_float(value: str | None) -> float:
    if value is None:
        raise TypeError("ArgumentNullException")
    if value == "":
        raise ValueError("FormatException")

    parsed = float(value)
    if math.isinf(parsed):
        raise FloatOverflowError("OverflowException")
    return parsed


def parse_nonnegative_float(value: str | None) -> float:
    parsed = parse_float(value)
    if parsed < 0:
        raise ValueError("Negative square root")
    return parsed


def format_number(value: float) -> str:
    if math.isnan(value):
        return "NaN"
    if math.isinf(value):
        return "Infinity" if value > 0 else "-Infinity"
    if value.is_integer():
        return str(int(value))
    return repr(value)


def calculate(operation: str, value1: str, value2: str) -> str:
    if operation == "add":
        return format_number(parse_float(value1) + parse_float(value2))
    if operation == "subtract":
        return format_number(parse_float(value1) - parse_float(value2))
    if operation == "multiply":
        return format_number(parse_float(value1) * parse_float(value2))
    if operation == "divide":
        return format_number(parse_float(value1) / parse_float(value2))
    if operation == "power":
        return format_number(parse_float(value1) ** parse_float(value2))
    if operation == "sqrt":
        return format_number(math.sqrt(parse_nonnegative_float(value1)))
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
        raw_body = self.rfile.read(length).decode("utf-8")
        data = parse_qs(raw_body, keep_blank_values=True)

        value1 = data.get("txtNro1", [""])[0]
        value2 = data.get("txtNro2", [""])[0]
        operation = data.get("operation", [""])[0]
        try:
            result = calculate(operation, value1, value2)
        except Exception:
            self.respond(500, "text/plain; charset=utf-8", b"Internal Server Error")
            return
        self.render_page(value1, value2, result)

    def render_page(self, value1: str, value2: str, result: str) -> None:
        page = HTML_TEMPLATE.format(
            title=escape_html(APP_CONFIG.title),
            heading=escape_html(APP_CONFIG.heading),
            label_number1=escape_html(APP_CONFIG.label_number1),
            label_number2=escape_html(APP_CONFIG.label_number2),
            result_label=escape_html(APP_CONFIG.result_label),
            button_add=escape_html(APP_CONFIG.button_add),
            button_subtract=escape_html(APP_CONFIG.button_subtract),
            button_multiply=escape_html(APP_CONFIG.button_multiply),
            button_divide=escape_html(APP_CONFIG.button_divide),
            button_power=escape_html(APP_CONFIG.button_power),
            button_sqrt=escape_html(APP_CONFIG.button_sqrt),
            runtime_host=escape_html(APP_CONFIG.runtime_host),
            runtime_port=escape_html(str(APP_CONFIG.runtime_port)),
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


def get_runtime_bind() -> tuple[str, int]:
    host = os.environ.get("HOST", APP_CONFIG.runtime_host)
    port_value = os.environ.get("PORT", str(APP_CONFIG.runtime_port))
    return host, int(port_value)


if __name__ == "__main__":
    host, port = get_runtime_bind()
    server = create_server(host, port)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
