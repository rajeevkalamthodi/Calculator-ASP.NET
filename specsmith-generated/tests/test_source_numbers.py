import unittest

from app import FloatOverflowError, calculate, parse_float


class SourceNumberTests(unittest.TestCase):
    def test_operands_use_single_precision(self):
        self.assertEqual(parse_float("16777217"), 16777216)
        self.assertEqual(calculate("subtract", "16777217", "16777216"), "0")

    def test_arithmetic_rounds_and_formats_as_single(self):
        self.assertEqual(calculate("add", "0.1", "0.2"), "0.3")
        self.assertEqual(calculate("add", "16777216", "1"), "1.677722E+07")
        self.assertEqual(calculate("multiply", "3e38", "2"), "Infinity")

    def test_division_by_zero_retains_ieee_sign_and_nan(self):
        for first, second, expected in [
            ("1", "0", "Infinity"),
            ("-1", "0", "-Infinity"),
            ("1", "-0", "Infinity"),
            ("-1", "-0", "-Infinity"),
            ("0", "0", "NaN"),
        ]:
            with self.subTest(first=first, second=second):
                self.assertEqual(calculate("divide", first, second), expected)

    def test_framework_zero_parsing_precedes_single_precision_rounding(self):
        self.assertEqual(calculate("divide", "1", "-0.0"), "Infinity")
        self.assertEqual(calculate("divide", "1", "-1e-400"), "Infinity")
        self.assertEqual(calculate("divide", "1", "-1e-50"), "-Infinity")

    def test_square_root_ignores_second_operand_and_preserves_nan(self):
        self.assertEqual(calculate("sqrt", "9", "unused"), "3")
        self.assertEqual(calculate("sqrt", "-1", "unused"), "NaN")
        self.assertEqual(calculate("sqrt", "-0", "unused"), "0")

    def test_out_of_range_input_remains_an_error(self):
        with self.assertRaises(FloatOverflowError):
            parse_float("1e39")


if __name__ == "__main__":
    unittest.main()
