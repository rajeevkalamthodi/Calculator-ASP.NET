"""Regression tests for the calculator backend (mirrors index.aspx.cs)."""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

import pytest  # noqa: E402

from app import create_app  # noqa: E402
import calculator  # noqa: E402


@pytest.fixture()
def client():
    app = create_app()
    app.config.update(TESTING=True)
    with app.test_client() as c:
        yield c


def post(client, operation, nro1=None, nro2=None):
    return client.post(
        "/api/calculate",
        json={"operation": operation, "nro1": nro1, "nro2": nro2},
    )


def test_somar(client):
    r = post(client, "somar", "2", "3")
    assert r.status_code == 200
    assert r.get_json()["result"] == "5"


def test_subtrair(client):
    r = post(client, "subtrair", "10", "4")
    assert r.get_json()["result"] == "6"


def test_multiplicar(client):
    r = post(client, "multiplicar", "6", "7")
    assert r.get_json()["result"] == "42"


def test_dividir(client):
    r = post(client, "dividir", "6", "3")
    assert r.get_json()["result"] == "2"


def test_dividir_by_zero(client):
    r = post(client, "dividir", "6", "0")
    assert r.status_code == 400
    assert "divide by zero" in r.get_json()["error"].lower()


def test_potencia(client):
    r = post(client, "potencia", "2", "10")
    assert r.get_json()["result"] == "1024"


def test_raizq(client):
    r = post(client, "raizq", "9", None)
    assert r.get_json()["result"] == "3"


def test_non_numeric_raises_format_error(client):
    r = post(client, "somar", "abc", "3")
    assert r.status_code == 400
    assert "correct format" in r.get_json()["error"].lower()


def test_unknown_operation(client):
    r = post(client, "bogus", "1", "2")
    assert r.status_code == 400


def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.get_json()["status"] == "ok"


def test_parse_number_rejects_empty():
    with pytest.raises(calculator.FormatError):
        calculator.parse_number("")
