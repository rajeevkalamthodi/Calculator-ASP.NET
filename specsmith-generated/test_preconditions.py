import unittest

from calculator_app import calculate, parse_number


class PreconditionsTests(unittest.TestCase):
    def test_parse_number_rejects_none(self):
        with self.assertRaises(TypeError):
            parse_number(None)

    def test_parse_number_rejects_invalid_numeric_text(self):
        with self.assertRaises(ValueError):
            parse_number("not-a-number")

    def test_unknown_operation_is_rejected(self):
        with self.assertRaises(ValueError):
            calculate("unsupported", "1", "2")

    def test_binary_operations_require_second_operand(self):
        for operation in ["somar", "subtrair", "multiplicar", "dividir", "potencia"]:
            with self.subTest(operation=operation):
                with self.assertRaises(TypeError):
                    calculate(operation, "1", None)


if __name__ == "__main__":
    unittest.main()
