"""Flask application for CalculadoraWebForms.

Serves the React single-page calculator and exposes a JSON endpoint that
performs the arithmetic operations originally implemented in the ASP.NET
Web Forms code-behind (index.aspx.cs).
"""

import os

from flask import Flask, jsonify, request, send_from_directory

from calculator import (
    OPERATIONS,
    CalculationError,
    FormatError,
    calculate,
)

STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")


def create_app():
    app = Flask(__name__, static_folder=STATIC_DIR, static_url_path="")

    @app.route("/health")
    def health():
        return jsonify({"status": "ok"})

    @app.route("/api/calculate", methods=["POST"])
    def api_calculate():
        data = request.get_json(silent=True) or {}
        operation = data.get("operation")
        nro1 = data.get("nro1")
        nro2 = data.get("nro2")

        if operation not in OPERATIONS:
            return jsonify({"error": "Unknown operation."}), 400

        try:
            result = calculate(operation, nro1, nro2)
        except FormatError as exc:
            return jsonify({"error": str(exc)}), 400
        except CalculationError as exc:
            return jsonify({"error": str(exc)}), 400
        except ValueError as exc:
            return jsonify({"error": str(exc)}), 400

        return jsonify({"result": result})

    @app.route("/")
    def index():
        index_path = os.path.join(STATIC_DIR, "index.html")
        if os.path.exists(index_path):
            return send_from_directory(STATIC_DIR, "index.html")
        return jsonify({"status": "ok", "message": "CalculadoraWebForms API"})

    @app.errorhandler(404)
    def not_found(_e):
        # SPA fallback for client-side routes.
        index_path = os.path.join(STATIC_DIR, "index.html")
        if os.path.exists(index_path):
            return send_from_directory(STATIC_DIR, "index.html")
        return jsonify({"error": "Not found"}), 404

    return app


app = create_app()


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "5000"))
    app.run(host="127.0.0.1", port=port)
