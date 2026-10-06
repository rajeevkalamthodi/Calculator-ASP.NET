"""Postcondition regression tests: error_type distinction per index.aspx.cs.

The ASP.NET code-behind raises a FormatException on non-numeric input for every
handler (btSomar/btSubtrair/btMultiplicar/btDividir/btPotencia/btRaizq) and an
arithmetic error on divide-by-zero (btDividir only). The JSON API must expose
that distinction via the ``error_type`` field.
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


def post(client, operation, nro1=None, nro2=None):
    return client.post(
        "/api/calculate",
        json={"operation": operation, "nro1": nro1, "nro2": nro2},
    )


BINARY_OPS = ["somar", "subtrair", "multiplicar", "dividir", "potencia"]


@pytest.mark.parametrize("operation", BINARY_OPS)
def test_non_numeric_first_operand_is_format_exception(client, operation):
    r = post(client, operation, "abc", "3")
    assert r.status_code == 400
    assert r.get_json()["error_type"] == "FormatException"


@pytest.mark.parametrize("operation", BINARY_OPS)
def test_non_numeric_second_operand_is_format_exception(client, operation):
    r = post(client, operation, "3", "xyz")
    assert r.status_code == 400
    assert r.get_json()["error_type"] == "FormatException"


def test_raizq_non_numeric_is_format_exception(client):
    r = post(client, "raizq", "abc", None)
    assert r.status_code == 400
    assert r.get_json()["error_type"] == "FormatException"


def test_dividir_by_zero_is_arithmetic(client):
    r = post(client, "dividir", "6", "0")
    assert r.status_code == 400
    assert r.get_json()["error_type"] == "arithmetic"


def test_success_has_no_error_type(client):
    r = post(client, "somar", "2", "3")
    assert r.status_code == 200
    body = r.get_json()
    assert body["result"] == "5"
    assert "error_type" not in body
