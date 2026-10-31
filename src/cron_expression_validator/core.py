"""Core validation logic for cron expressions.

Supports the classic five-field cron format:
    minute hour day-of-month month day-of-week

Each field is validated for syntax and range.  The library deliberately does
not compute fire times; it only checks that the expression is well-formed.

Field ranges:
    minute        0-59
    hour          0-23
    day-of-month  1-31
    month         1-12 (names JAN-DEC accepted)
    day-of-week   0-6  (names SUN-SAT accepted, 0 and 7 both mean Sunday)

Supported syntax per field:
    *           any value
    n           single value
    n-m         inclusive range
    n-m/s       range with step
    */s         any value with step
    n/s         single value with step (treated as n-max/s)
    a,b,c       list of the above
"""

import re

__all__ = ["validate_cron", "is_valid_cron", "CronExpressionError"]


class CronExpressionError(ValueError):
    """Raised when a cron expression is syntactically invalid or out of range."""


# Month and day-of-week names are case-insensitive.
_MONTH_NAMES = {
    "JAN": 1, "FEB": 2, "MAR": 3, "APR": 4, "MAY": 5, "JUN": 6,
    "JUL": 7, "AUG": 8, "SEP": 9, "OCT": 10, "NOV": 11, "DEC": 12,
}

_DOW_NAMES = {
    "SUN": 0, "MON": 1, "TUE": 2, "WED": 3, "THU": 4, "FRI": 5, "SAT": 6,
}

# (min, max, names) for each of the five fields, in order.
_FIELDS = [
    (0, 59, {}),          # minute
    (0, 23, {}),          # hour
    (1, 31, {}),          # day of month
    (1, 12, _MONTH_NAMES),  # month
    (0, 7, _DOW_NAMES),   # day of week; 7 is normalised to 0
]

_FIELD_NAMES = ["minute", "hour", "day-of-month", "month", "day-of-week"]

# A single element is one of:
#   *
#   n
#   n-m
#   n-m/s
#   */s
#   n/s
# Tokens may be numeric or names (JAN, MON, ...).  The regex is intentionally
# permissive about tokens; range checks happen after parsing so we can produce
# precise error messages.
_ELEMENT_RE = re.compile(
    r"^(?P<base>\*|[A-Za-z0-9]+(?:-[A-Za-z0-9]+)?)(?:/(?P<step>\d+))?$"
)


def _normalise_token(token, names):
    """Return the numeric value for a token, resolving names.

    Names are only valid for month and day-of-week fields.  We uppercase the
    token because cron implementations are conventionally case-insensitive.
    """
    upper = token.upper()
    if upper in names:
        return names[upper]
    if token.isdigit():
        return int(token)
    raise CronExpressionError(f"invalid value: {token!r}")


def _parse_element(element, min_val, max_val, names, field_name):
    """Validate one comma-separated element and return (start, end, step).

    The returned tuple is only used for validation; callers do not need the
    expanded set of values.  ``step`` is always at least 1.
    """
    match = _ELEMENT_RE.match(element)
    if not match:
        raise CronExpressionError(
            f"invalid element {element!r} in {field_name} field"
        )

    base = match.group("base")
    step_text = match.group("step")

    if base == "*":
        start, end = min_val, max_val
    elif "-" in base:
        left, right = base.split("-", 1)
        start = _normalise_token(left, names)
        end = _normalise_token(right, names)
    else:
        start = end = _normalise_token(base, names)

    if not (min_val <= start <= max_val):
        raise CronExpressionError(
            f"value {start} out of range [{min_val}, {max_val}] in {field_name} field"
        )
    if not (min_val <= end <= max_val):
        raise CronExpressionError(
            f"value {end} out of range [{min_val}, {max_val}] in {field_name} field"
        )
    if start > end:
        raise CronExpressionError(
            f"range start {start} greater than end {end} in {field_name} field"
        )

    if step_text is None:
        step = 1
    else:
        step = int(step_text)
        if step == 0:
            raise CronExpressionError(
                f"step must be positive in {field_name} field"
            )

    return start, end, step


def _validate_field(field, min_val, max_val, names, field_name):
    """Validate one whole field (comma-separated list of elements)."""
    if not field:
        raise CronExpressionError(f"empty {field_name} field")

    for element in field.split(","):
        if not element:
            raise CronExpressionError(
                f"empty element in {field_name} field"
            )
        _parse_element(element, min_val, max_val, names, field_name)


def validate_cron(expression):
    """Validate a five-field cron expression.

    Returns ``True`` if the expression is syntactically valid and every field
    is within its legal range.  Raises :class:`CronExpressionError` with a
    human-readable message otherwise.

    The function does not compute fire times; it only checks structure and
    ranges.  This keeps it fast and free of timezone or DST concerns.
    """
    if not isinstance(expression, str):
        raise CronExpressionError("expression must be a string")

    # Collapse runs of whitespace so that accidental double spaces do not
    # produce spurious empty fields.
    parts = expression.split()
    if len(parts) != 5:
        raise CronExpressionError(
            f"expected 5 fields, got {len(parts)}"
        )

    for field, (min_val, max_val, names), name in zip(parts, _FIELDS, _FIELD_NAMES):
        _validate_field(field, min_val, max_val, names, name)

    return True


def is_valid_cron(expression):
    """Return ``True`` if the expression is valid, ``False`` otherwise.

    This is a convenience wrapper around :func:`validate_cron` for callers who
    prefer a boolean over exception handling.
    """
    try:
        validate_cron(expression)
    except CronExpressionError:
        return False
    return True
