import unittest
import sys
import os

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))

import passman

class TestPassman(unittest.TestCase):

    def setUp(self):
        # Ensure common passwords cache is loaded
        passman.load_common_passwords()

    def test_load_common_passwords(self):
        passwords = passman.load_common_passwords()
        self.assertIsInstance(passwords, set)
        self.assertGreater(len(passwords), 0)
        self.assertIn("123456", passwords)
        self.assertIn("password", passwords)

    def test_check_password_compromised(self):
        self.assertTrue(passman.check_password("123456"))
        self.assertTrue(passman.check_password("password"))
        self.assertTrue(passman.check_password("PASSWORD"))  # Case insensitive check
        self.assertTrue(passman.check_password("admin123"))

    def test_check_password_safe(self):
        self.assertFalse(passman.check_password("Xk9#mP2$vQ8!zL4"))
        self.assertFalse(passman.check_password("UnlikelyToExistCompromisedPassword2026!"))

    def test_entropy_score(self):
        # Empty password
        self.assertEqual(passman.entropy_score(""), 0.0)

        # Lowercase only, length 8: 8 * log2(26) ~= 37.60
        score_lower = passman.entropy_score("abcdefgh")
        self.assertAlmostEqual(score_lower, 8 * passman.math.log2(26), places=2)

        # Lowercase + Digits, length 10: 10 * log2(36) ~= 51.70
        score_mix = passman.entropy_score("abcde12345")
        self.assertAlmostEqual(score_mix, 10 * passman.math.log2(36), places=2)

        # Full pool (lower, upper, digit, special), pool size 94: length 16: 16 * log2(94) ~= 104.87
        score_full = passman.entropy_score("Aa1!Bb2@Cc3#Dd4$")
        self.assertAlmostEqual(score_full, 16 * passman.math.log2(94), places=2)

    def test_entropy_range(self):
        self.assertIn("Very Weak", passman.entropy_range(20))
        self.assertIn("Weak", passman.entropy_range(30))
        self.assertIn("Medium", passman.entropy_range(45))
        self.assertIn("Strong", passman.entropy_range(80))
        self.assertIn("Very Strong", passman.entropy_range(130))

    def test_generate_password_valid(self):
        pwd = passman.generate_password(
            length=16,
            upper_case=True,
            lower_case=True,
            numbers=True,
            special_characters=True
        )
        self.assertIsNotNone(pwd)
        self.assertNotEqual(pwd, False)
        self.assertEqual(len(pwd), 16)
        # Verify character set inclusions
        self.assertTrue(any(c.isupper() for c in pwd))
        self.assertTrue(any(c.islower() for c in pwd))
        self.assertTrue(any(c.isdigit() for c in pwd))
        self.assertTrue(any(c in passman.string.punctuation for c in pwd))
        # Verify generated password is not compromised
        self.assertFalse(passman.check_password(pwd))

    def test_generate_password_invalid_flags(self):
        # No character set selected
        res = passman.generate_password(12, False, False, False, False)
        self.assertFalse(res)

    def test_generate_password_short_length(self):
        # Length shorter than required character sets (4 sets selected, length 3)
        res = passman.generate_password(3, True, True, True, True)
        self.assertFalse(res)

if __name__ == "__main__":
    unittest.main()
