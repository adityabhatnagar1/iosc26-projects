"""
Password Strength & Breach-Pattern Checker
Author: Abhishek Singh
Description: Core evaluation module containing Shannon entropy calculation,
             heuristic pattern matching, and HIBP k-Anonymity REST API lookup.

Privacy model: only the first 5 hex characters of the SHA-1 digest are sent
to the network. The password and full hash never leave the machine.
"""

import argparse
import getpass
import hashlib
import math
import re
from typing import Dict, List, Tuple, Union

import requests

try:  # works as `python -m src.pwd_checker` and when imported as a package
    from src.generator import generate_secure_password
except ImportError:  # pragma: no cover
    from generator import generate_secure_password

# ---------------------------------------------------------------- constants
HIBP_RANGE_URL = "https://api.pwnedpasswords.com/range/"
HIBP_TIMEOUT_SECONDS = 3.0
SHORT_LENGTH_LABEL = "Short Length (< 12 characters)"
MIN_SAFE_LENGTH = 12

# Leetspeak substitutions, reversed before word-based pattern checks.
LEET_TRANS_TABLE = str.maketrans({
    '@': 'a', '4': 'a',
    '3': 'e',
    '1': 'i', '!': 'i',
    '0': 'o',
    '5': 's', '$': 's',
    '7': 't',
})

# Rules run against the leet-normalized string (words and keyboard walks).
NORMALIZED_RULES: List[Tuple[str, str]] = [
    (r'qwerty|asdfgh|zxcvbn|poiuyt|lkjhgf|mnbvcxz', "Keyboard Walk Pattern"),
    (r'pass|admin|welcome|login|master|secret|user', "Common Dictionary Base Keyword"),
]

# Rules run against the raw lowercase string. Digits must NOT be leet-translated
# first, otherwise "12345" would become "i2eas" and never match.
RAW_RULES: List[Tuple[str, str]] = [
    (r'12345|23456|34567|45678|56789|67890|09876|98765|87654|76543|65432|54321',
     "Sequential Number Sequence"),
    (r'(.)\1{2,}', "Repeated Character Sequence"),
    (r'(19|20)\d{2}', "Four-Digit Calendar Year"),
]

# Return value of check_hibp_breach() when the lookup could not be completed.
BREACH_UNKNOWN = -1


class PasswordAnalyzer:
    """Analyzes a single password: entropy, patterns, and breach exposure."""

    def __init__(self, password: str):
        self.password = password
        self.lowered = password.lower()
        self.normalized_password = self.lowered.translate(LEET_TRANS_TABLE)
        self.sha1_full = hashlib.sha1(password.encode("utf-8")).hexdigest().upper()
        self.sha1_prefix = self.sha1_full[:5]
        self.sha1_suffix = self.sha1_full[5:]

    def calculate_entropy(self) -> float:
        """Shannon entropy in bits: per-character entropy x password length."""
        if not self.password:
            return 0.0

        length = len(self.password)
        counts: Dict[str, int] = {}
        for char in self.password:
            counts[char] = counts.get(char, 0) + 1

        per_char = 0.0
        for count in counts.values():
            p = count / length
            per_char -= p * math.log2(p)

        # "+ 0.0" turns a possible -0.0 (single repeated symbol) into 0.0
        return round(per_char * length, 2) + 0.0

    def detect_patterns(self) -> List[str]:
        """Return labels of predictable patterns found in the password."""
        detected: List[str] = []

        for pattern, label in RAW_RULES:
            if re.search(pattern, self.lowered):
                detected.append(label)
        for pattern, label in NORMALIZED_RULES:
            if re.search(pattern, self.normalized_password):
                detected.append(label)

        if len(self.password) < MIN_SAFE_LENGTH:
            detected.append(SHORT_LENGTH_LABEL)

        return detected

    def check_hibp_breach(self) -> int:
        """Look up the password via the HIBP range API (k-Anonymity).

        Returns the exposure count, 0 if not found, or BREACH_UNKNOWN (-1)
        if the lookup failed (offline, timeout, non-200 response).
        """
        try:
            response = requests.get(
                f"{HIBP_RANGE_URL}{self.sha1_prefix}",
                headers={
                    "User-Agent": "PasswordBreachChecker-CLI",
                    "Add-Padding": "true",  # pads responses with fake entries
                },
                timeout=HIBP_TIMEOUT_SECONDS,
            )
            if response.status_code != 200:
                return BREACH_UNKNOWN

            for line in response.text.splitlines():
                suffix, _, count = line.partition(":")
                if suffix.strip().upper() == self.sha1_suffix:
                    return int(count.strip())
            return 0

        except (requests.RequestException, ValueError):
            return BREACH_UNKNOWN


def rate_password(entropy: float, patterns: List[str], breach_count: int) -> str:
    """Combine entropy, patterns and breach status into one rating."""
    if breach_count > 0 or entropy < 35 or SHORT_LENGTH_LABEL in patterns:
        return "CRITICAL / WEAK"
    if entropy < 60 or patterns:
        return "FAIR / MODERATE"
    return "STRONG"


def generate_report(password: str) -> Dict[str, Union[str, float, int, List[str]]]:
    """Return a structured evaluation (usable from the CLI or an API)."""
    analyzer = PasswordAnalyzer(password)
    entropy = analyzer.calculate_entropy()
    patterns = analyzer.detect_patterns()
    breach_count = analyzer.check_hibp_breach()

    return {
        "length": len(password),
        "sha1_prefix": analyzer.sha1_prefix,
        "entropy_bits": entropy,
        "patterns_found": patterns,
        "breach_count": breach_count,
        "overall_rating": rate_password(entropy, patterns, breach_count),
    }


def print_cli_report(password: str, show_password: bool = False) -> None:
    """Print a formatted report to standard output."""
    report = generate_report(password)
    shown = password if show_password else "*" * len(password)

    print("=" * 60)
    print("              PASSWORD SECURITY AUDIT REPORT")
    print("=" * 60)
    print(f"Target String:       {shown}")
    print(f"String Length:       {report['length']} characters")
    print(f"SHA-1 Hash Prefix:   {report['sha1_prefix']} (k-Anonymity Bucket)")
    print(f"Calculated Entropy:  {report['entropy_bits']} bits")

    print("\n--- Heuristic Pattern Vulnerabilities ---")
    if report["patterns_found"]:
        for label in report["patterns_found"]:
            print(f" [!] {label}")
    else:
        print(" [+] No structural vulnerability patterns detected.")

    print("\n--- Data Breach Verification (HIBP API) ---")
    breach = report["breach_count"]
    if breach > 0:
        print(" [CRITICAL] EXPOSED IN DATA LEAKS!")
        print(f" Found {breach:,} times in public breach datasets.")
    elif breach == 0:
        print(" [SAFE] ZERO EXPOSURES FOUND.")
        print(" This string does not appear in known data leaks.")
    else:
        print(" [WARNING] COULD NOT VERIFY BREACH STATUS (Offline/Network Error).")

    print("\n--- Overall Rating & Actionable Guidance ---")
    print(f" Final Assessment:   {report['overall_rating']}")
    if report["overall_rating"] == "STRONG":
        print(" Recommendation:     Meets security standards for production deployment.")
    else:
        print(" Recommendation:     DO NOT USE. Change immediately.")
        print(f" Suggested Fix:      {generate_secure_password(16)}")
    print("=" * 60)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Password Strength & Breach-Pattern Checker")
    parser.add_argument("--password", "-p", type=str,
                        help="Password to analyze (may be saved in shell history; "
                             "omit to be prompted securely)")
    parser.add_argument("--show", action="store_true",
                        help="Print the password in the report (masked by default)")
    args = parser.parse_args()

    password = args.password if args.password is not None \
        else getpass.getpass("Enter password to evaluate (hidden): ")
    print_cli_report(password, show_password=args.show)


if __name__ == "__main__":
    main()
