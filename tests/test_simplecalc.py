# Copyright 2015-2018 Canonical Ltd.
# Copyright 2020 Facundo Batista
# All Rights Reserved

"""Tests for a simple calculator."""

import math
from decimal import Decimal
from unittest import TestCase

import simplecalc


class BaseTestCase(TestCase):
    """Common code for all test cases."""

    def check(self, operations):
        for inp, result in operations:
            with self.subTest(inp=inp, result=result):
                if isinstance(result, type) and issubclass(result, Exception):
                    self.assertRaises(result, simplecalc.calc, inp)
                else:
                    try:
                        calculated = simplecalc.calc(inp)
                    except Exception as err:
                        self.fail("Calculator exploded with %s when %r" % (
                                  err, inp))
                    else:
                        msg = "%r gave %r (should: %r)" % (inp, calculated, result)
                        if isinstance(result, str):
                            result = Decimal(result)
                        self.assertAlmostEqual(calculated, Decimal(result), places=17, msg=msg)


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
            ('2 / 17', Decimal(2) / 17),
            ('2 / 124124124124', Decimal(2) / 124124124124),
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
            ('2 ** 1500', Decimal(2) ** 1500),
            ('2.5 ** 1500', Decimal('2.5') ** 1500),
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
            ('acosh(2)', '1.316957896924816573402949871'),
            ('asin(0)', '0'),
            ('asinh(4)', '2.094712547261101232010105377'),
            ('atan(5)', '1.373400766945015893938375484'),
            ('atanh(0)', '0'),
            ('ceil(6.1)', '7'),
            ('cos(8)', '-0.1455000338086135380777363935'),
            ('cosh(9)', '4051.54202549259434817940928'),
            ('degrees(10)', '572.9577951308232286464772187'),
            ('exp(13)', '442413.3920089205033261027759'),
            ('factorial(16)', '20922789888000'),
            ('floor(1.7)', '1'),
            ('gamma(6)', '120'),
            ('radians(32)', '0.5585053606381854551798937791'),
            ('sin(33)', '0.9999118601072671808083214273'),
            ('sinh(34)', '291730871263727.4375'),
            ('sqrt(35)', '5.916079783099616042567328292'),
            ('tan(36)', '7.750470905699147650125269138'),
            ('tanh(37)', '1'),
            ('trunc(38)', '38'),
            ('hypot(4, 3)', '5'),
            ('hypot(4 3)', '5'),
            ('pow(2, 3)', '8'),
            # without parens also
            ('acos 1', '0'),
            ('acosh 2', '1.316957896924816573402949871'),
            ('asin 0', '0'),
            ('asinh 4', '2.094712547261101232010105377'),
            ('atan 5', '1.373400766945015893938375484'),
            ('atanh 0', '0'),
            ('ceil 6.1', '7'),
            ('cos 8', '-0.1455000338086135380777363935'),
            ('cosh 9', '4051.54202549259434817940928'),
            ('degrees 10', '572.9577951308232286464772187'),
            ('exp 13', '442413.3920089205033261027759'),
            ('factorial 16', '20922789888000'),
            ('floor 1.7', '1'),
            ('gamma 6', '120'),
            ('radians 32', '0.5585053606381854551798937791'),
            ('sin 33', '0.9999118601072671808083214273'),
            ('sinh 34', '291730871263727.4375'),
            ('sqrt 35', '5.916079783099616042567328292'),
            ('tan 36', '7.750470905699147650125269138'),
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
            ('int(44, 5)', '24'),
            ('round(12.1234, 2)', '12.12'),
            ('abs(-55)', '55'),
        ])


class ValuesTestCase(BaseTestCase):
    """Allow to use some names."""

    def test_basic(self):
        self.check([
            ('e', Decimal(math.e)),
            ('pi', Decimal(math.pi)),
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
            ('2 < 1', False),
            ('2 < 3', True),
            ('4 + 2 < 6', False),
            ('2 + (5 < 6)', ValueError),
        ])

    def test_greaterthan(self):
        self.check([
            ('7 > -8', True),
            ('7 > 8', False),
            ('0 > 0', False),
        ])

    def test_lessequalthan(self):
        self.check([
            ('2 <= 3', True),
            ('2 <= 2', True),
            ('2 <= 1', False),
        ])

    def test_greaterequalthan(self):
        self.check([
            ('2 >= 1', True),
            ('2 >= 2', True),
            ('2 >= 3', False),
        ])

    def test_equality(self):
        self.check([
            ('2 == 2', True),
            ('2 == 1', False),
            ('-2 == 2', False),
            ('2 = 2', True),
            ('2 === 2', True),
        ])

    def test_different(self):
        self.check([
            ('2 != 1', True),
            ('2 != 2', False),
            ('2 != 3', True),
            ('2 <> 2', False),
        ])
