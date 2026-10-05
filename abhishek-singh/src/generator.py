"""
Cryptographically Secure Password Generator
Author: Abhishek Singh
Description: Generates high-entropy random passwords using the secrets CSPRNG.
"""

import argparse
import secrets
import string

MIN_LENGTH = 12
SYMBOLS = "!@#$%^&*()_+-=[]{}|;:,.<>?"


def generate_secure_password(length: int = 16, include_symbols: bool = True) -> str:
    """Generate a random password using the secrets module (CSPRNG).

    Guarantees at least one lowercase letter, uppercase letter and digit
    (plus one symbol when include_symbols is True). Lengths below
    MIN_LENGTH are raised to MIN_LENGTH.
    """
    length = max(length, MIN_LENGTH)

    lowercase = string.ascii_lowercase
    uppercase = string.ascii_uppercase
    digits = string.digits
    symbols = SYMBOLS if include_symbols else ""

    alphabet = lowercase + uppercase + digits + symbols

    # Guarantee at least one character from each enabled pool
    password_chars = [
        secrets.choice(lowercase),
        secrets.choice(uppercase),
        secrets.choice(digits),
    ]
    if include_symbols:
        password_chars.append(secrets.choice(symbols))

    remaining = length - len(password_chars)
    password_chars.extend(secrets.choice(alphabet) for _ in range(remaining))

    # Shuffle so the guaranteed characters are not in predictable positions
    secrets.SystemRandom().shuffle(password_chars)
    return "".join(password_chars)


def main() -> None:
    parser = argparse.ArgumentParser(description="Secure password generator")
    parser.add_argument("--length", "-l", type=int, default=16,
                        help="Password length (minimum 12, default 16)")
    parser.add_argument("--no-symbols", action="store_true",
                        help="Exclude symbols from the password")
    args = parser.parse_args()
    print(generate_secure_password(args.length, not args.no_symbols))


if __name__ == "__main__":
    main()
