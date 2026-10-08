from app import app


def client():
    app.config["TESTING"] = True
    return app.test_client()


def test_health_endpoint():
    response = client().get("/health")
    assert response.status_code == 200
    assert response.get_json() == {"status": "ok"}


def test_index_page_renders_calculator_controls():
    response = client().get("/")
    html = response.get_data(as_text=True)

    assert response.status_code == 200
    assert "Calculadora" in html
    assert "Somar" in html
    assert "Subtrair" in html
    assert "Multiplicar" in html
    assert "Dividir" in html
    assert "Potência" in html
    assert "Raiz Quadrada" in html


def test_add_operation_renders_result():
    response = client().post("/", data={"n1": "2", "n2": "3", "operation": "add"})
    assert response.status_code == 200
    assert "5.0" in response.get_data(as_text=True)


def test_subtract_operation_renders_result():
    response = client().post("/", data={"n1": "7", "n2": "4", "operation": "subtract"})
    assert "3.0" in response.get_data(as_text=True)


def test_multiply_operation_renders_result():
    response = client().post("/", data={"n1": "6", "n2": "5", "operation": "multiply"})
    assert "30.0" in response.get_data(as_text=True)


def test_divide_operation_renders_result():
    response = client().post("/", data={"n1": "8", "n2": "2", "operation": "divide"})
    assert "4.0" in response.get_data(as_text=True)


def test_power_operation_renders_result():
    response = client().post("/", data={"n1": "2", "n2": "3", "operation": "power"})
    assert "8.0" in response.get_data(as_text=True)


def test_square_root_operation_renders_result():
    response = client().post("/", data={"n1": "9", "n2": "999", "operation": "sqrt"})
    assert "3.0" in response.get_data(as_text=True)


def test_invalid_numeric_input_surfaces_error():
    response = client().post("/", data={"n1": "abc", "n2": "2", "operation": "add"})
    body = response.get_data(as_text=True)
    assert response.status_code == 200
    assert "ValueError" in body
