"""Automated tests for the Caesar Cipher project.

Run with:  python -m unittest discover tests -v
       or:  python tests/test_caesar.py
"""

import os
import sys
import unittest
from unittest.mock import patch

# make src/ importable regardless of where the test is run from
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from caesar_cipher import Encrypt, Decrypt, shift_letter, get_key


class TestShiftLetter(unittest.TestCase):
    def test_basic_shift(self):
        self.assertEqual(shift_letter('a', 3), 'd')

    def test_wraparound(self):
        # z shifted by 3 wraps back to c
        self.assertEqual(shift_letter('z', 3), 'c')

    def test_uppercase_preserved(self):
        self.assertEqual(shift_letter('H', 3), 'K')
        self.assertEqual(shift_letter('Z', 3), 'C')

    def test_decrypt_is_negative_shift(self):
        self.assertEqual(shift_letter('d', -3), 'a')


class TestEncrypt(unittest.TestCase):
    def test_readme_example(self):
        self.assertEqual(Encrypt('Hello World', 3), 'Khoor Zruog')

    def test_full_alphabet(self):
        self.assertEqual(
            Encrypt('abcdefghijklmnopqrstuvwxyz', 1),
            'bcdefghijklmnopqrstuvwxyza')

    def test_punctuation_passthrough(self):
        self.assertEqual(Encrypt('Attack at Dawn!', 7), 'Haahjr ha Khdu!')

    def test_numbers_passthrough(self):
        self.assertEqual(Encrypt('abc123', 1), 'bcd123')


class TestDecrypt(unittest.TestCase):
    def test_readme_example(self):
        self.assertEqual(Decrypt('Khoor Zruog', 3), 'Hello World')

    def test_all_valid_keys_roundtrip(self):
        message = 'The Quick Brown Fox 2026!'
        for key in range(1, 26):
            self.assertEqual(Decrypt(Encrypt(message, key), key), message)


class TestGetKeyValidation(unittest.TestCase):
    """Simulate a user entering bad input, then a valid key."""

    def test_rejects_out_of_range_then_accepts(self):
        # user types 30 (rejected), then 3 (accepted)
        with patch('builtins.input', side_effect=['30', '3']), \
             patch('builtins.print') as mock_print:
            key = get_key()
        self.assertEqual(key, 3)
        mock_print.assert_called_with('KEY MUST BE 1-25. TRY AGAIN.')

    def test_rejects_non_numeric_then_accepts(self):
        # user types 'abc' (rejected), then 5 (accepted)
        with patch('builtins.input', side_effect=['abc', '5']), \
             patch('builtins.print') as mock_print:
            key = get_key()
        self.assertEqual(key, 5)
        mock_print.assert_called_with('ENTER A WHOLE NUMBER. TRY AGAIN.')


if __name__ == '__main__':
    unittest.main(verbosity=2)
