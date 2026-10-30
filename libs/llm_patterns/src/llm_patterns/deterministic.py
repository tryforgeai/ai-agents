"""Week 03 'run, don't reason': calculate with code."""
from datetime import date
from decimal import Decimal


def days_between(start, end):
    """ISO dates; end-start, excluding the end date, signed if reversed."""
    return (date.fromisoformat(end) - date.fromisoformat(start)).days


def sum_amounts(values):
    """Use decimal strings, Decimal or integers; reject floats and NaN/Infinity."""
    total = Decimal("0")
    for value in values:
        if isinstance(value, (float, bool)):
            raise TypeError("use decimal strings, integers or Decimal, not float/bool")
        amount = Decimal(value)
        if not amount.is_finite():
            raise ValueError("amount must be finite")
        total += amount
    return total


def routing_report(expected, predicted):
    """None is a valid 'no matching skill' label, not an error."""
    expected, predicted = list(expected), list(predicted)
    if len(expected) != len(predicted) or not expected:
        raise ValueError("provide equally sized, nonempty label sequences")
    return {
        "accuracy": sum(a == b for a, b in zip(expected, predicted)) / len(expected),
        "mismatches": [{"index": i, "expected": a, "predicted": b}
                       for i, (a, b) in enumerate(zip(expected, predicted)) if a != b],
        "false_triggers": sum(a is None and b is not None for a, b in zip(expected, predicted)),
        "missed_triggers": sum(a is not None and b is None for a, b in zip(expected, predicted)),
    }
