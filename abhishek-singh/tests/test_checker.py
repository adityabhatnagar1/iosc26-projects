"""
Automated Test Suite for the Password Checker
Author: Abhishek Singh
Description: Unit tests for entropy, pattern detection, rating logic,
             the generator, and the HIBP k-Anonymity lookup (mocked).
"""

from unittest.mock import MagicMock, patch

import requests

from src.generator import generate_secure_password
from src.pwd_checker import (BREACH_UNKNOWN, PasswordAnalyzer, generate_report,
                             rate_password)


def _mock_response(text: str, status: int = 200) -> MagicMock:
    resp = MagicMock()
    resp.status_code = status
    resp.text = text
    return resp


# ------------------------------------------------------------------ entropy
def test_entropy_calculation():
    assert PasswordAnalyzer("aaaaaa").calculate_entropy() == 0.0
    assert str(PasswordAnalyzer("aaaaaa").calculate_entropy()) == "0.0"  # no -0.0
    assert PasswordAnalyzer("k9#mX2!pL9$v").calculate_entropy() > 30.0
    assert PasswordAnalyzer("").calculate_entropy() == 0.0


def test_entropy_known_value():
    # 4 distinct symbols, equal frequency -> 2 bits/char x 4 chars = 8 bits
    assert PasswordAnalyzer("abcd").calculate_entropy() == 8.0


# ----------------------------------------------------------------- patterns
def test_pattern_detection():
    patterns = PasswordAnalyzer("P@ssw0rd12345").detect_patterns()
    assert "Sequential Number Sequence" in patterns
    assert "Common Dictionary Base Keyword" in patterns


def test_leetspeak_normalization():
    analyzer = PasswordAnalyzer("P@ssw0rd")
    assert analyzer.normalized_password == "password"
    assert "Common Dictionary Base Keyword" in analyzer.detect_patterns()


def test_keyboard_walk_and_year():
    patterns = PasswordAnalyzer("qwerty2024!").detect_patterns()
    assert "Keyboard Walk Pattern" in patterns
    assert "Four-Digit Calendar Year" in patterns
    assert "Short Length (< 12 characters)" in patterns


def test_repeated_characters():
    assert "Repeated Character Sequence" in \
        PasswordAnalyzer("aaaaaaaaaaaaaaaa").detect_patterns()


def test_strong_password_has_no_patterns():
    assert PasswordAnalyzer("xT9#mK2$vL9@pQ4!").detect_patterns() == []


# ------------------------------------------------------------------- rating
def test_rating_logic():
    assert rate_password(62.0, [], 0) == "STRONG"
    assert rate_password(62.0, [], 5) == "CRITICAL / WEAK"
    assert rate_password(20.0, [], 0) == "CRITICAL / WEAK"
    assert rate_password(50.0, [], 0) == "FAIR / MODERATE"
    assert rate_password(70.0, ["Keyboard Walk Pattern"], 0) == "FAIR / MODERATE"
    assert rate_password(70.0, ["Short Length (< 12 characters)"], 0) == "CRITICAL / WEAK"


# --------------------------------------------------------------------- HIBP
def test_hibp_breach_lookup_found():
    analyzer = PasswordAnalyzer("password123")
    body = (f"0018A45C4D1DEF81644B54AB7F969B88D65:100\n"
            f"{analyzer.sha1_suffix}:50")
    with patch("src.pwd_checker.requests.get", return_value=_mock_response(body)) as get:
        assert analyzer.check_hibp_breach() == 50
        # Only the 5-char prefix may appear in the request URL
        url = get.call_args[0][0]
        assert url.endswith("/" + analyzer.sha1_prefix)
        assert analyzer.sha1_suffix not in url
        assert analyzer.password not in url


def test_hibp_breach_lookup_not_found():
    body = "0018A45C4D1DEF81644B54AB7F969B88D65:100"
    with patch("src.pwd_checker.requests.get", return_value=_mock_response(body)):
        assert PasswordAnalyzer("unlikely_random_secure_str_999").check_hibp_breach() == 0


def test_hibp_padding_entries_count_as_zero():
    analyzer = PasswordAnalyzer("some-padded-case")
    with patch("src.pwd_checker.requests.get",
               return_value=_mock_response(f"{analyzer.sha1_suffix}:0")):
        assert analyzer.check_hibp_breach() == 0


def test_hibp_network_error_falls_back():
    with patch("src.pwd_checker.requests.get", side_effect=requests.ConnectionError):
        assert PasswordAnalyzer("anything").check_hibp_breach() == BREACH_UNKNOWN


def test_hibp_timeout_falls_back():
    with patch("src.pwd_checker.requests.get", side_effect=requests.Timeout):
        assert PasswordAnalyzer("anything").check_hibp_breach() == BREACH_UNKNOWN


def test_hibp_non_200_falls_back():
    with patch("src.pwd_checker.requests.get", return_value=_mock_response("", 503)):
        assert PasswordAnalyzer("anything").check_hibp_breach() == BREACH_UNKNOWN


def test_generate_report_offline_still_returns_local_analysis():
    with patch("src.pwd_checker.requests.get", side_effect=requests.ConnectionError):
        report = generate_report("qwerty2024!")
    assert report["breach_count"] == BREACH_UNKNOWN
    assert report["overall_rating"] == "CRITICAL / WEAK"
    assert "Keyboard Walk Pattern" in report["patterns_found"]


# ---------------------------------------------------------------- generator
def test_generator_entropy_and_length():
    pwd = generate_secure_password(16)
    assert len(pwd) == 16
    assert PasswordAnalyzer(pwd).calculate_entropy() > 40.0


def test_generator_minimum_length_and_character_classes():
    pwd = generate_secure_password(5)  # raised to the minimum of 12
    assert len(pwd) == 12
    assert any(c.islower() for c in pwd)
    assert any(c.isupper() for c in pwd)
    assert any(c.isdigit() for c in pwd)
    assert any(not c.isalnum() for c in pwd)


def test_generator_without_symbols():
    pwd = generate_secure_password(20, include_symbols=False)
    assert len(pwd) == 20 and pwd.isalnum()


def test_generator_outputs_are_unique():
    assert len({generate_secure_password(16) for _ in range(50)}) == 50
