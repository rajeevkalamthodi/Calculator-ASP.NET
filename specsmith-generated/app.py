from flask import Flask, render_template, request
from math import sqrt

app = Flask(__name__)


def parse_number(raw_value: str) -> float:
    return float(raw_value)


def render_number(value: float) -> str:
    return str(value)


OPERATIONS = {
    "add": lambda a, b: a + b,
    "subtract": lambda a, b: a - b,
    "multiply": lambda a, b: a * b,
    "divide": lambda a, b: a / b,
    "power": lambda a, b: a ** b,
    "sqrt": lambda a, _b: sqrt(a),
}


@app.get("/health")
def health():
    return {"status": "ok"}, 200


@app.route("/", methods=["GET", "POST"])
def index():
    values = {"n1": "", "n2": ""}
    result = ""
    error = ""

    if request.method == "POST":
        values["n1"] = request.form.get("n1", "")
        values["n2"] = request.form.get("n2", "")
        operation = request.form.get("operation", "")

        try:
            first = parse_number(values["n1"])
            second = parse_number(values["n2"]) if operation != "sqrt" else 0.0
            if operation not in OPERATIONS:
                raise KeyError(operation)
            result = render_number(OPERATIONS[operation](first, second))
        except Exception as exc:  # preserve failure visibility on page
            error = f"{type(exc).__name__}: {exc}"

    return render_template("index.html", values=values, result=result, error=error)


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000)
