import unittest
from calculator_app import calculate, render_page


class CalculatorTests(unittest.TestCase):
    def test_render_page_contains_all_actions(self):
        page = render_page({})
        for label in ["Somar", "Subtrair", "Multiplicar", "Dividir", "Potência", "Raiz Quadrada"]:
            self.assertIn(label, page)

    def test_addition(self):
        self.assertEqual(calculate("somar", "2", "3"), "5")

    def test_subtraction(self):
        self.assertEqual(calculate("subtrair", "10", "4"), "6")

    def test_multiplication(self):
        self.assertEqual(calculate("multiplicar", "7", "6"), "42")

    def test_division(self):
        self.assertEqual(calculate("dividir", "8", "2"), "4")

    def test_power(self):
        self.assertEqual(calculate("potencia", "2", "3"), "8")

    def test_square_root_uses_first_value(self):
        self.assertEqual(calculate("raizq", "9", "123"), "3")

    def test_invalid_numeric_input_raises(self):
        with self.assertRaises(ValueError):
            calculate("somar", "abc", "1")


if __name__ == "__main__":
    unittest.main()
