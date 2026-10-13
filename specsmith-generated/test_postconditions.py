import unittest

from calculator_app import calculate, render_page


class PostconditionTests(unittest.TestCase):
    def test_page_load_returns_rendered_page_markup(self):
        page = render_page({})
        self.assertIsInstance(page, str)
        self.assertIn("<form", page)

    def test_addition_sets_numeric_sum_string(self):
        self.assertEqual(calculate("somar", "2", "3"), "5")
        self.assertEqual(calculate("somar", "2.5", "0.5"), "3")

    def test_subtraction_sets_result_string(self):
        self.assertEqual(calculate("subtrair", "10", "4"), "6")
        self.assertEqual(calculate("subtrair", "5.5", "2"), "3.5")

    def test_division_returns_result_string(self):
        self.assertEqual(calculate("dividir", "8", "2"), "4")
        self.assertEqual(calculate("dividir", "7.5", "2.5"), "3")

    def test_power_returns_result_string(self):
        self.assertEqual(calculate("potencia", "2", "3"), "8")
        self.assertEqual(calculate("potencia", "9", "0.5"), "3")

    def test_square_root_returns_result_string(self):
        self.assertEqual(calculate("raizq", "9", "123"), "3")
        self.assertEqual(calculate("raizq", "2.25", "0"), "1.5")

    def test_binary_operations_raise_value_error_on_invalid_numeric_text(self):
        for operation in ["somar", "subtrair", "multiplicar", "dividir", "potencia"]:
            with self.subTest(operation=operation):
                with self.assertRaises(ValueError):
                    calculate(operation, "abc", "1")

    def test_binary_operations_raise_type_error_on_null_text(self):
        for operation in ["somar", "subtrair", "multiplicar", "dividir", "potencia"]:
            with self.subTest(operation=operation):
                with self.assertRaises(TypeError):
                    calculate(operation, None, "1")

    def test_square_root_raises_value_error_for_invalid_numeric_text(self):
        with self.assertRaises(ValueError):
            calculate("raizq", "abc", "0")

    def test_square_root_raises_overflow_error_for_out_of_range_input(self):
        with self.assertRaises(OverflowError):
            calculate("raizq", "1e1000000", "0")


if __name__ == "__main__":
    unittest.main()
