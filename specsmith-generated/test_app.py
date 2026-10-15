import re
import unittest
from app import calculate, render_page


class CalculatorRenderingTests(unittest.TestCase):
    def test_render_page_contains_calculator_controls(self):
        html = render_page()
        self.assertIn("CalculadoraWebForms", html)
        self.assertIn('name="txtNro1"', html)
        self.assertIn('name="txtNro2"', html)
        self.assertIn('value="somar"', html)
        self.assertIn('value="subtrair"', html)
        self.assertIn('value="multiplicar"', html)
        self.assertIn('value="dividir"', html)
        self.assertIn('value="potencia"', html)
        self.assertIn('value="raizq"', html)
        self.assertIn('id="lbResultado"', html)

    def test_addition(self):
        self.assertEqual(calculate("somar", "2", "3"), "5.0")

    def test_subtraction(self):
        self.assertEqual(calculate("subtrair", "7", "2"), "5.0")

    def test_multiplication(self):
        self.assertEqual(calculate("multiplicar", "4", "2.5"), "10.0")

    def test_division(self):
        self.assertEqual(calculate("dividir", "9", "3"), "3.0")

    def test_division_by_zero_returns_infinity_shape(self):
        self.assertEqual(calculate("dividir", "2", "0"), "inf")

    def test_power(self):
        self.assertEqual(calculate("potencia", "2", "3"), "8.0")

    def test_square_root(self):
        self.assertEqual(calculate("raizq", "9", "0"), "3.0")

    def test_render_page_escapes_values(self):
        html = render_page('<tag>', '"quoted"', '&done')
        self.assertIn('&lt;tag&gt;', html)
        self.assertIn('&quot;quoted&quot;', html)
        self.assertIn('&amp;done', html)

    def test_invalid_numeric_input_raises_value_error(self):
        with self.assertRaises(ValueError):
            calculate("somar", "abc", "1")

    def test_invalid_operation_raises_value_error(self):
        with self.assertRaises(ValueError):
            calculate("desconhecida", "1", "2")


if __name__ == "__main__":
    unittest.main()
