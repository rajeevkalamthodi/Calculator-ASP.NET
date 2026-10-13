"""Compatibility module retained to avoid ambiguous Python root runtime discovery.

The actual executable root entry is main.py. Runtime hosting logic lives in
calculator_app.py, and this module intentionally exposes no launcher.
"""

from calculator_app import CalculatorHandler, calculate, decimal_to_result_text, parse_number, render_page, run

__all__ = [
    "CalculatorHandler",
    "calculate",
    "decimal_to_result_text",
    "parse_number",
    "render_page",
    "run",
]
