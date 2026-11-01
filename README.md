# cron_expression_validator

Validates whether a five-field cron expression is syntactically correct and every field is within its legal range, without computing fire times.

```python
from cron_expression_validator import validate_cron, is_valid_cron, CronExpressionError

# validate_cron returns True or raises CronExpressionError with a message.
validate_cron("0 12 * * MON-FRI")   # True
validate_cron("*/15 0-6 1,15 JAN,JUL *")  # True

# is_valid_cron returns a plain boolean and never raises.
is_valid_cron("60 * * * *")          # False
try:
    validate_cron("60 * * * *")
except CronExpressionError as exc:
    print(exc)  # value 60 out of range [0, 59] in minute field
```

The five fields are minute, hour, day-of-month, month, and day-of-week.  Each field accepts `*`, a single number, a range `n-m`, a step `/s`, and comma-separated lists.  Month names (`JAN`-`DEC`) and day-of-week names (`SUN`-`SAT`) are accepted case-insensitively.  Day-of-week `7` is accepted and means Sunday, matching the common Vixie-cron convention.

## Why this exists

Most cron libraries parse an expression and then compute the next fire time.  That pulls in date arithmetic, timezone handling, and DST edge cases, all of which are easy to get subtly wrong and hard to test deterministically.  This library stops at the syntax and range check.  The trade-off is that it will accept expressions that a particular cron daemon might reject for non-syntactic reasons (for example, `0 0 31 2 *` is syntactically valid even though February never has 31 days), but it is fast, has no dependencies, and its behaviour is fully deterministic.

## Awkward edge

The day-of-week field accepts both `0` and `7` for Sunday.  If you are comparing expressions textually, `0` and `7` will not compare equal even though they mean the same day.  Normalise before comparing if that matters to you.
