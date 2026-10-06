"""Regression tests for the server compute-and-return workflow.

Covers req-a6d4ac51fae89d759c4231b5: the server receives operands and an
operation, computes the arithmetic result (mirroring the ASP.NET index.aspx.cs
handlers), and returns it as a JSON payload. These tests exercise the HTTP
surface (POST /api/calculate) for all six operations plus representative
non-integer, negative and error-producing results. They are additive and do
not modify the existing accepted suite.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

import pytest  # noqa: E402

from app import create_app  # noqa: E402


@pytest.fixture()
def client():
    app = create_app()
    app.config.update(TESTING=True)
    with app.test_client() as c:
        yield c


def compute(client, operation, nro1=None, nro2=None):
    return client.post(
        "/api/calculate",
        json={"operation": operation, "nro1": nro1, "nro2": nro2},
    )


def test_server_returns_sum(client):
    r = compute(client, "somar", "2", "3")
    assert r.status_code == 200
    assert r.get_json() == {"result": "5"}


def test_server_returns_negative_difference(client):
    r = compute(client, "subtrair", "4", "10")
    assert r.status_code == 200
    assert r.get_json()["result"] == "-6"


def test_server_returns_product(client):
    r = compute(client, "multiplicar", "-3", "7")
    assert r.status_code == 200
    assert r.get_json()["result"] == "-21"


def test_server_returns_fractional_quotient(client):
    r = compute(client, "dividir", "7", "2")
    assert r.status_code == 200
    assert r.get_json()["result"] == "3.5"


def test_server_returns_power(client):
    r = compute(client, "potencia", "3", "3")
    assert r.status_code == 200
    assert r.get_json()["result"] == "27"


def test_server_returns_square_root(client):
    r = compute(client, "raizq", "16", None)
    assert r.status_code == 200
    assert r.get_json()["result"] == "4"


def test_server_rejects_divide_by_zero(client):
    r = compute(client, "dividir", "5", "0")
    assert r.status_code == 400
    assert "divide by zero" in r.get_json()["error"].lower()


def test_server_rejects_non_numeric(client):
    r = compute(client, "multiplicar", "x", "2")
    assert r.status_code == 400
    assert "correct format" in r.get_json()["error"].lower()


def test_server_rejects_unknown_operation(client):
    r = compute(client, "modulo", "5", "2")
    assert r.status_code == 400
    assert r.get_json()["error"]


def test_server_returns_json_content_type(client):
    r = compute(client, "somar", "1", "1")
    assert r.headers.get("Content-Type") == "application/json"
