"""Core arithmetic logic mirroring the ASP.NET Web Forms calculator.

The original code-behind parses each textbox with float.Parse and assigns the
computed result to a label via ToString(). Non-numeric input raises a
FormatException; divide-by-zero raises an arithmetic error. We reproduce that
observable behavior here.
"""

import math
import struct


class FormatError(ValueError):
    """Raised when an operand cannot be parsed as a number (FormatException)."""


class CalculationError(ArithmeticError):
    """Raised for arithmetic failures such as divide-by-zero."""


def parse_number(text):
    """Emulate .NET float.Parse: trim, reject empty/invalid, narrow to single."""
    if text is None:
        raise FormatError("Input string was not in a correct format.")
    s = str(text).strip()
    if s == "":
        raise FormatError("Input string was not in a correct format.")
    try:
        value = float(s)
    except ValueError:
        raise FormatError("Input string was not in a correct format.")
    narrowed = struct.unpack("f", struct.pack("f", value))[0]
    return narrowed


def _format(value):
    """Format a float result similar to .NET Single/Double ToString()."""
    if isinstance(value, float):
        if math.isnan(value):
            return "NaN"
        if math.isinf(value):
            return "Infinity" if value > 0 else "-Infinity"
        if value == int(value) and abs(value) < 1e16:
            return str(int(value))
        return repr(value)
    return str(value)


def somar(nro1, nro2):
    return _format(parse_number(nro1) + parse_number(nro2))


def subtrair(nro1, nro2):
    return _format(parse_number(nro1) - parse_number(nro2))


def multiplicar(nro1, nro2):
    return _format(parse_number(nro1) * parse_number(nro2))


def dividir(nro1, nro2):
    a = parse_number(nro1)
    b = parse_number(nro2)
    if b == 0:
        raise CalculationError("Attempted to divide by zero.")
    return _format(a / b)


def potencia(nro1, nro2):
    return _format(math.pow(parse_number(nro1), parse_number(nro2)))


def raizq(nro1):
    return _format(math.sqrt(parse_number(nro1)))


OPERATIONS = {
    "somar": ("binary", somar),
    "subtrair": ("binary", subtrair),
    "multiplicar": ("binary", multiplicar),
    "dividir": ("binary", dividir),
    "potencia": ("binary", potencia),
    "raizq": ("unary", lambda n1, n2: raizq(n1)),
}


def calculate(operation, nro1, nro2):
    if operation not in OPERATIONS:
        raise ValueError("Unknown operation: %s" % operation)
    _, fn = OPERATIONS[operation]
    return fn(nro1, nro2)
