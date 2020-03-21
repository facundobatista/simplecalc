# Copyright 2015-2018 Canonical Ltd.
# All Rights Reserved

"""Tests for a simple calculator."""

from unittest import TestCase

import simplecalc


class BaseTestCase(TestCase):
    """Common code for all test cases."""

    def check(self, operations):
        for inp, result in operations:
            if isinstance(result, type) and issubclass(result, Exception):
                self.assertRaises(result, simplecalc.calc, inp)
            else:
                try:
                    calculated = simplecalc.calc(inp)
                except Exception as err:
                    self.fail("Calculator exploded with %s when %r" % (
                              err, inp))
                else:
                    m = "%r gave %r (should: %r)" % (inp, calculated, result)
                    self.assertEqual(calculated, result, m)


class SimpleIntegersTestCase(BaseTestCase):
    """Check the basic operations."""

    def test_sum(self):
        self.check([
            ('2 + 3', '5'),
            ('0 + 5', '5'),
            ('+2', '2'),
            ('2 + +2', '4'),
        ])

    def test_subtract(self):
        self.check([
            ('2 - 1', '1'),
            ('4-3', '1'),
            ('3 -7', '-4'),
            ('-7', '-7'),
            ('2 - -2', '4'),
        ])

    def test_product(self):
        self.check([
            ('2 * 5', '10'),
            ('-3 * 2', '-6'),
            ('3 * -2', '-6'),
            ('0 * 81256894562934562834652834562345', '0'),
            ('239846298462483 * 2429784263942', '582774761768877502456687986'),
            ('-7 * -2', '14'),
        ])

    def test_division(self):
        self.check([
            ('7 / 2', '3.5'),
            ('8 / 4', '2'),
            ('2 / 17', '0.117647058824'),
            ('2 / 124124124124', '1.61129032258e-11'),
        ])

    def test_exponentiation(self):
        self.check([
            ('2 ** 3', '8'),
            ('0 ** 2', '0'),
            ('13513515135153135 ** 0', '1'),
            ('-3 ** 2', '9'),
            ('-3 ** 3', '-27'),
            ('10 ** -1', '0.1'),
            ('2 ** -2', '0.25'),
            ('2 ** 1500', ArithmeticError),
        ])


class FloatTestCase(BaseTestCase):
    """Support floats."""

    def test_simple_ops(self):
        self.check([
            ('2 + 0.3', '2.3'),
            ('2.3 - 1.1', '1.2'),
            ('3.3 ** 0', '1'),
            ('144 ** 0.5', '12'),
            ('12 / 4.0', '3'),
        ])

    def test_alternate_formats(self):
        self.check([
            ('2 + .5', '2.5'),
            ('2 + 0,3', '2.3'),
            ('2 + ,3', '2.3'),
            ('1e2', '100'),
            ('1e+2', '100'),
            ('1e-2', '0.01'),
            ('1E2', '100'),
            ('1E+2', '100'),
            ('1E-2', '0.01'),
            ('1e2.3', ValueError),
            ('2,', '2'),
            ('2,e3', '2000'),
            ('2.', '2'),
            ('2.e3', '2000'),
        ])


class GroupingTestCase(BaseTestCase):
    """Different combination of parentheses."""

    def test_simple(self):
        self.check([
            ('(2 + 3)', '5'),
            ('3 - (2)', '1'),
            ('3 - (-2)', '5'),
            ('(2 + 3) * 3', '15'),
            ('2 + (3 * 5)', '17'),
        ])

    def test_multiple(self):
        self.check([
            ('((2 + 3) * 2) ** (1 + 0)', '10'),
        ])


class SpecialOperationsTestCase(BaseTestCase):
    """Some special operations."""

    def test_factorial(self):
        self.check([
            ('0!', '1'),
            ('1!', '1'),
            ('3!', '6'),
            ('2.3!', ValueError),
            ('-5!', ValueError),
            ('%d!' % (simplecalc.MAX_FACTORIAL_INP + 1,), ArithmeticError),
        ])


class FunctionsTestCase(BaseTestCase):
    """Allow to call functions."""

    def test_frommath_operations(self):
        self.check([
            ('acos(1)', '0'),
            ('acosh(2)', '1.31695789692'),
            ('asin(0)', '0'),
            ('asinh(4)', '2.09471254726'),
            ('atan(5)', '1.37340076695'),
            ('atanh(0)', '0'),
            ('ceil(6.1)', '7'),
            ('cos(8)', '-0.145500033809'),
            ('cosh(9)', '4051.54202549'),
            ('degrees(10)', '572.957795131'),
            ('exp(13)', '442413.392009'),
            ('factorial(16)', '20922789888000'),
            ('floor(1.7)', '1'),
            ('gamma(6)', '120'),
            ('radians(32)', '0.558505360638'),
            ('sin(33)', '0.999911860107'),
            ('sinh(34)', '2.91730871264e+14'),
            ('sqrt(35)', '5.9160797831'),
            ('tan(36)', '7.7504709057'),
            ('tanh(37)', '1'),
            ('trunc(38)', '38'),
            ('hypot(4, 3)', '5'),
            ('hypot(4 3)', '5'),
            ('pow(2, 3)', '8'),
            # without parens also
            ('acos 1', '0'),
            ('acosh 2', '1.31695789692'),
            ('asin 0', '0'),
            ('asinh 4', '2.09471254726'),
            ('atan 5', '1.37340076695'),
            ('atanh 0', '0'),
            ('ceil 6.1', '7'),
            ('cos 8', '-0.145500033809'),
            ('cosh 9', '4051.54202549'),
            ('degrees 10', '572.957795131'),
            ('exp 13', '442413.392009'),
            ('factorial 16', '20922789888000'),
            ('floor 1.7', '1'),
            ('gamma 6', '120'),
            ('radians 32', '0.558505360638'),
            ('sin 33', '0.999911860107'),
            ('sinh 34', '2.91730871264e+14'),
            ('sqrt 35', '5.9160797831'),
            ('tan 36', '7.7504709057'),
            ('tanh 37', '1'),
            ('trunc 38', '38'),
            ('hypot 4, 3', '5'),
            ('hypot 4 3', '5'),
            ('pow 2, 3', '8'),
            ('(pow 2, 3) * 5', '40'),
        ])

    def test_math_altered(self):
        toobig = simplecalc.MAX_FACTORIAL_INP + 1
        self.check([
            ('log(10)', '1'),
            ('ln(2.718281828459045)', '1'),
            ('log2(64)', '6'),
            ('log(64, 2)', '6'),
            ('distance(4, 3)', '5'),
            ('factorial(%d)' % (toobig,), ArithmeticError),
        ])

    def test_frombuiltin(self):
        self.check([
            ('int(2.3)', '2'),
            ('float(123)', '123'),
            ('int(44, 5)', '24'),
            ('round(12.1234, 2)', '12.12'),
            ('abs(-55)', '55'),
        ])


class ValuesTestCase(BaseTestCase):
    """Allow to use some names."""

    def test_basic(self):
        self.check([
            ('e', '2.71828182846'),
            ('pi', '3.14159265359'),
        ])

    def test_in_operations(self):
        self.check([
            ('sin(pi / 2)', '1'),
            ('ln(e)', '1'),
        ])


class ComparisonsTestCase(BaseTestCase):
    """Check comparisons."""

    def test_notallowed(self):
        self.check([
            ('2 + (5 < 6)', ValueError),
            ('1 < 2 < 3', ValueError),
            ('1 < 2 > 3', ValueError),
            ('1 < 2 == 3', ValueError),
        ])

    def test_lessthan(self):
        self.check([
            ('2 < 1', 'False'),
            ('2 < 3', 'True'),
            ('4 + 2 < 6', 'False'),
            ('2 + (5 < 6)', ValueError),
        ])

    def test_greaterthan(self):
        self.check([
            ('7 > -8', 'True'),
            ('7 > 8', 'False'),
            ('0 > 0', 'False'),
        ])

    def test_lessequalthan(self):
        self.check([
            ('2 <= 3', 'True'),
            ('2 <= 2', 'True'),
            ('2 <= 1', 'False'),
        ])

    def test_greaterequalthan(self):
        self.check([
            ('2 >= 1', 'True'),
            ('2 >= 2', 'True'),
            ('2 >= 3', 'False'),
        ])

    def test_equality(self):
        self.check([
            ('2 == 2', 'True'),
            ('2 == 1', 'False'),
            ('-2 == 2', 'False'),
            ('2 = 2', 'True'),
            ('2 === 2', 'True'),
        ])

    def test_different(self):
        self.check([
            ('2 != 1', 'True'),
            ('2 != 2', 'False'),
            ('2 != 3', 'True'),
            ('2 <> 2', 'False'),
        ])