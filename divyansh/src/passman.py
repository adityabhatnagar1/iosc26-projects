import random
import math
import string
import os

RED = "\033[31m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
RESET = "\033[0m"

rng = random.SystemRandom()
_COMMON_PASSWORDS_CACHE = None

def load_common_passwords():
    global _COMMON_PASSWORDS_CACHE
    if _COMMON_PASSWORDS_CACHE is None:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(script_dir, "Common passwords.txt")
        if not os.path.exists(file_path):
            file_path = "Common passwords.txt"
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                _COMMON_PASSWORDS_CACHE = set(line.strip() for line in f if line.strip())
        except FileNotFoundError:
            print(f"{YELLOW}Common passwords file not found. Skipping common password check.{RESET}")
            _COMMON_PASSWORDS_CACHE = set()
    return _COMMON_PASSWORDS_CACHE

def ask_yes_no(prompt):
    while True:
        answer = input(prompt).strip().lower()
        if answer in ("y", "yes"):
            return True
        if answer in ("n", "no"):
            return False
        print(f"{YELLOW}Please enter 'y' or 'n'.{RESET}")

def ask_positive_int(prompt):
    while True:
        try:
            value = int(input(prompt))
        except ValueError:
            print(f"{YELLOW}Please enter a whole number.{RESET}")
            continue
        if value < 1:
            print(f"{YELLOW}Please enter a number greater than 0.{RESET}")
            continue
        return value

def check_password(password):
    common_passwords = load_common_passwords()
    if not common_passwords:
        return False
    return (password in common_passwords) or (password.lower() in common_passwords)

def generate_password(length, upper_case, lower_case, numbers, special_characters):
    if not (upper_case or lower_case or numbers or special_characters):
        return False
    character_pool = []
    if upper_case:
        character_pool.append(string.ascii_uppercase)
    if lower_case:
        character_pool.append(string.ascii_lowercase)
    if numbers:
        character_pool.append(string.digits)
    if special_characters:
        character_pool.append(string.punctuation)
    if not character_pool or length < len(character_pool):
        return False
    all_chars = "".join(character_pool)
    max_attempts = 500
    for _ in range(max_attempts):
        chars = [rng.choice(pool) for pool in character_pool]
        chars += rng.choices(all_chars, k=length - len(character_pool))
        rng.shuffle(chars)
        password = "".join(chars)
        if not check_password(password):
            return password
    return False

def entropy_score(password):
    length = len(password)
    if length == 0:
        return 0.0
    character_pool = 0
    if any(c in string.ascii_uppercase for c in password):
        character_pool += 26
    if any(c in string.ascii_lowercase for c in password):
        character_pool += 26
    if any(c in string.digits for c in password):
        character_pool += 10
    if any(c in string.punctuation or c.isspace() or not c.isalnum() for c in password):
        character_pool += len(string.punctuation)
    if character_pool == 0:
        return 0.0
    entropy = length * math.log2(character_pool)
    return entropy

def entropy_range(entropy):
    if entropy < 28:
        return f"{RED}Very Weak{RESET}"
    elif 28 <= entropy < 36:
        return f"{RED}Weak{RESET}"
    elif 36 <= entropy < 60:
        return f"{YELLOW}Medium{RESET}"
    elif 60 <= entropy < 127:
        return f"{GREEN}Strong{RESET}"
    else:
        return f"{GREEN}Very Strong{RESET}"

def passman_breach_checker():
    print("=" * 75)
    print("PASSWORD BREACH CHECKER")
    password = input("Enter the password to be checked: ")
    if check_password(password):
        print(f"{RED}PASSWORD IS COMPROMISED{RESET}")
    else:
        print(f"{GREEN}PASSWORD IS SAFE{RESET}")
    print("=" * 75)

def passman_password_generator():
    print("=" * 75)
    print("PASSWORD GENERATOR")
    length = ask_positive_int("Enter the length of the password: ")
    upper_case = ask_yes_no("Do you want to include uppercase letters? (y/n): ")
    lower_case = ask_yes_no("Do you want to include lowercase letters? (y/n): ")
    numbers = ask_yes_no("Do you want to include numbers? (y/n): ")
    special_characters = ask_yes_no("Do you want to include special characters? (y/n): ")    
    password = generate_password(length, upper_case, lower_case, numbers, special_characters)
    if not password:
        print(f"{YELLOW}PASSWORD CAN'T BE GENERATED{RESET}")
        return
    print(f"Generated Password: {GREEN}{password}{RESET}")
    entropy = entropy_score(password)
    print(f"Entropy: {entropy:.2f} bits") 
    print(f"Password Strength: {entropy_range(entropy)}")
    print("=" * 75)

def passman_password_strength_tester():
    print("=" * 75)
    print("PASSWORD STRENGTH TESTER")
    password = input("Enter the password to be checked: ")
    entropy = entropy_score(password)
    print(f"Entropy: {entropy:.2f} bits") 
    print(f"Password Strength: {entropy_range(entropy)}")
    print("=" * 75)

def main():
    while True:
        print("=" * 75)
        print("""
     _______  _______  _______  _______  __   __  _______  __    _
    |       ||   _   ||       ||       ||  |_|  ||   _   ||  |  | |
    |    _  ||  |_|  ||  _____||  _____||       ||  |_|  ||   |_| |
    |   |_| ||       || |_____ | |_____ |       ||       ||       |
    |    ___||       ||_____  ||_____  ||       ||       ||  _    |
    |   |    |   _   | _____| | _____| || ||_|| ||   _   || | |   |
    |___|    |__| |__||_______||_______||_|   |_||__| |__||_|  |__|
        """)
        print("=" * 75)
        print("1. PASSWORD BREACH CHECKER")
        print("2. PASSWORD GENERATOR")
        print("3. PASSWORD STRENGTH TESTER")
        print("4. EXIT")
        print("=" * 75)
        choice = input("Enter your choice: ")
        if choice == "1":
            passman_breach_checker()
        elif choice == "2":
            passman_password_generator()
        elif choice == "3":
            passman_password_strength_tester()
        elif choice == "4":
            print("=" * 75)
            break
        else:
            print(f"{YELLOW}INVALID CHOICE{RESET}")

if __name__ == "__main__":
    main()