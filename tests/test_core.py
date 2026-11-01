import unittest

from cron_expression_validator import (
    validate_cron,
    is_valid_cron,
    CronExpressionError,
)


class TestValidateCron(unittest.TestCase):
    def test_simple_expression(self):
        self.assertTrue(validate_cron("* * * * *"))

    def test_specific_values(self):
        self.assertTrue(validate_cron("0 12 1 1 0"))

    def test_ranges(self):
        self.assertTrue(validate_cron("0-30 0-12 1-15 1-6 0-3"))

    def test_steps(self):
        self.assertTrue(validate_cron("*/15 */6 */2 */3 */2"))

    def test_lists(self):
        self.assertTrue(validate_cron("1,2,3 4,5 6,7 8,9 0,1"))

    def test_names(self):
        self.assertTrue(validate_cron("0 0 1 JAN MON"))
        self.assertTrue(validate_cron("0 0 1 jan mon"))

    def test_day_of_week_seven_is_sunday(self):
        self.assertTrue(validate_cron("0 0 * * 7"))

    def test_extra_whitespace(self):
        self.assertTrue(validate_cron("  0   12   *   *   *  "))

    def test_invalid_field_count(self):
        with self.assertRaises(CronExpressionError):
            validate_cron("* * * *")
        with self.assertRaises(CronExpressionError):
            validate_cron("* * * * * *")

    def test_empty_string(self):
        with self.assertRaises(CronExpressionError):
            validate_cron("")

    def test_out_of_range_minute(self):
        with self.assertRaises(CronExpressionError):
            validate_cron("60 * * * *")

    def test_out_of_range_hour(self):
        with self.assertRaises(CronExpressionError):
            validate_cron("* 24 * * *")

    def test_out_of_range_day_of_month(self):
        with self.assertRaises(CronExpressionError):
            validate_cron("* * 0 * *")
        with self.assertRaises(CronExpressionError):
            validate_cron("* * 32 * *")

    def test_out_of_range_month(self):
        with self.assertRaises(CronExpressionError):
            validate_cron("* * * 0 *")
        with self.assertRaises(CronExpressionError):
            validate_cron("* * * 13 *")

    def test_out_of_range_day_of_week(self):
        with self.assertRaises(CronExpressionError):
            validate_cron("* * * * 8")

    def test_invalid_range_order(self):
        with self.assertRaises(CronExpressionError):
            validate_cron("30-10 * * * *")

    def test_zero_step(self):
        with self.assertRaises(CronExpressionError):
            validate_cron("*/0 * * * *")

    def test_invalid_element(self):
        with self.assertRaises(CronExpressionError):
            validate_cron("a * * * *")
        with self.assertRaises(CronExpressionError):
            validate_cron("1- * * * *")
        with self.assertRaises(CronExpressionError):
            validate_cron("* * * * *-")

    def test_non_string_input(self):
        with self.assertRaises(CronExpressionError):
            validate_cron(123)
        with self.assertRaises(CronExpressionError):
            validate_cron(None)


class TestIsValidCron(unittest.TestCase):
    def test_valid(self):
        self.assertTrue(is_valid_cron("0 0 * * *"))

    def test_invalid(self):
        self.assertFalse(is_valid_cron("not a cron"))
        self.assertFalse(is_valid_cron("* * * *"))
        self.assertFalse(is_valid_cron(123))

    def test_does_not_raise(self):
        # is_valid_cron must never propagate CronExpressionError.
        self.assertFalse(is_valid_cron(""))


if __name__ == "__main__":
    unittest.main()
