#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import sys
import unittest
PATH_TO_VALIDATOR = '/'.join(str(os.path.abspath(__file__)).split('/')[:-2])
sys.path.insert(0,PATH_TO_VALIDATOR)
import Validator


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
