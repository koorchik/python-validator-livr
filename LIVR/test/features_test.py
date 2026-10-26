#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import sys
import unittest
PATH_TO_VALIDATOR = '/'.join(str(os.path.abspath(__file__)).split('/')[:-2])
sys.path.insert(0,PATH_TO_VALIDATOR)
import Validator


class TestAutoTrim(unittest.TestCase):
    def setUp(self):
        self.validator = Validator.Validator({
            'code': 'required',
            'password': ['required', {'min_length': 3}],
            'list': {'list_of': ['string']},
            'address': {'nested_object': {
                'street': {'min_length': 5}
            }}
        }, True)

    def test_negative(self):
        output = self.validator.validate({
            'code': '  ',
            'password': ' 12  ',
            'address': {'street': '  hell '}
        })

        self.assertFalse(output)
        self.assertEqual(self.validator.get_errors(), {
            'code': 'REQUIRED',
            'password': 'TOO_SHORT',
            'address': {'street': 'TOO_SHORT'}
        })

    def test_positive(self):
        output = self.validator.validate({
            'code': ' A ',
            'password': ' 123  ',
            'list': [' aaa ', ' bbb '],
            'address': {'street': '  hello '}
        })

        self.assertEqual(output, {
            'code': 'A',
            'password': '123',
            'list': ['aaa', 'bbb'],
            'address': {'street': 'hello'}
        })

    def test_default_auto_trim(self):
        Validator.Validator.set_default_auto_trim(True)
        try:
            output = Validator.Validator({'code': 'required'}).validate({'code': ' A '})
        finally:
            Validator.Validator.set_default_auto_trim(False)

        self.assertEqual(output, {'code': 'A'})
        self.assertEqual(Validator.Validator({'code': 'required'}).validate({'code': ' A '}), {'code': ' A '})


class TestNotObjectInput(unittest.TestCase):
    def test_not_object(self):
        validator = Validator.Validator({'code': 'required'})

        for data in ['code', ['code'], None]:
            self.assertEqual(validator.validate(data), False)
            self.assertEqual(validator.get_errors(), 'FORMAT_ERROR')


class TestLike(unittest.TestCase):
    def test_not_anchored(self):
        validator = Validator.Validator({'code': {'like': '[0-9]+'}})

        self.assertEqual(validator.validate({'code': 'abc123'}), {'code': 'abc123'})


# Python 2 has unicode strings, long integers and shorter str() of floats
class TestPython2(unittest.TestCase):
    def test_unicode_characters(self):
        validator = Validator.Validator({
            'removed': {'remove': u'ä-'},
            'left': {'leave_only': u'äb'},
            'word': {'like': [u'^\\w+$', 'i']}
        })
        output = validator.validate({'removed': u'bä-c', 'left': u'bä-c', 'word': u'Привет'})

        self.assertEqual(output, {'removed': u'bc', 'left': u'bä', 'word': u'Привет'})

    def test_long_integer(self):
        validator = Validator.Validator({'number': 'integer', 'text': 'string'})
        output = validator.validate({'number': 12345678901234567890, 'text': 12345678901234567890})

        self.assertEqual(output, {'number': 12345678901234567890, 'text': '12345678901234567890'})

    def test_float(self):
        validator = Validator.Validator({'text': 'string', 'value': {'eq': '0.3'}})
        output = validator.validate({'text': 0.1 + 0.2, 'value': 0.1 + 0.2})

        self.assertFalse(output)
        self.assertEqual(validator.get_errors(), {'value': 'NOT_ALLOWED_VALUE'})
        self.assertEqual(validator.validate({'text': 0.1 + 0.2}), {'text': '0.30000000000000004'})


if __name__ == '__main__':
    unittest.main()
