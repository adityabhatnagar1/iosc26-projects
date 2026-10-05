import os
import math
import string
import secrets
import csv
from flask import Flask, render_template, request, jsonify

# Load environment variables from .env file if available
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", secrets.token_hex(32))

BREACH_DATASET = {}        # exact match: password -> rank or source
BREACH_DATASET_LOWER = {}  # case-insensitive match: lower(password) -> rank or source
DATASET_STATS = {
    "total_passwords": 0,
    "source_file": "None",
    "has_ranks": False
}

def load_breach_data():
    global BREACH_DATASET, BREACH_DATASET_LOWER, DATASET_STATS
    BREACH_DATASET.clear()
    BREACH_DATASET_LOWER.clear()
    
    csv_filename = os.environ.get("BREACH_CSV_FILE", "10millionPasswords.csv")
    txt_filename = os.environ.get("BREACH_TXT_FILE", "common_passwords.txt")
    
    csv_file = os.path.join(os.path.dirname(__file__), csv_filename) if not os.path.isabs(csv_filename) else csv_filename
    txt_file = os.path.join(os.path.dirname(__file__), txt_filename) if not os.path.isabs(txt_filename) else txt_filename
    
    loaded_from_csv = False
    
    # 1. Try loading full 1-million breached dataset if available
    if os.path.exists(csv_file):
        try:
            with open(csv_file, "r", encoding="utf-8", errors="ignore") as f:
                reader = csv.reader(f)
                header = next(reader, None)
                rank_col = 0
                pw_col = 1
                for row_idx, row in enumerate(reader, start=1):
                    if len(row) >= 2:
                        pw = row[pw_col]
                        try:
                            rank = int(row[rank_col])
                        except (ValueError, TypeError):
                            rank = row_idx
                        BREACH_DATASET[pw] = rank
                        if pw.lower() not in BREACH_DATASET_LOWER:
                            BREACH_DATASET_LOWER[pw.lower()] = rank
                    elif len(row) == 1 and row[0]:
                        pw = row[0]
                        BREACH_DATASET[pw] = row_idx
                        if pw.lower() not in BREACH_DATASET_LOWER:
                            BREACH_DATASET_LOWER[pw.lower()] = row_idx
            loaded_from_csv = True
            DATASET_STATS["source_file"] = "10millionPasswords.csv (1 Million Leaked Passwords)"
            DATASET_STATS["has_ranks"] = True
            print(f"[*] Successfully loaded {len(BREACH_DATASET):,} passwords from {csv_file}")
        except Exception as e:
            print(f"[!] Warning loading CSV: {e}")
            
    # 2. Also merge/fallback to common_passwords.txt
    if os.path.exists(txt_file):
        try:
            with open(txt_file, "r", encoding="utf-8", errors="ignore") as f:
                for line_idx, line in enumerate(f, start=1):
                    pw = line.strip()
                    if pw and pw not in BREACH_DATASET:
                        rank = line_idx if not loaded_from_csv else 999999 + line_idx
                        BREACH_DATASET[pw] = rank
                        if pw.lower() not in BREACH_DATASET_LOWER:
                            BREACH_DATASET_LOWER[pw.lower()] = rank
            if not loaded_from_csv:
                DATASET_STATS["source_file"] = "common_passwords.txt"
                DATASET_STATS["has_ranks"] = False
                print(f"[*] Successfully loaded {len(BREACH_DATASET):,} passwords from {txt_file}")
        except Exception as e:
            print(f"[!] Warning loading TXT: {e}")
            
    DATASET_STATS["total_passwords"] = len(BREACH_DATASET)

# Initialize dataset once
load_breach_data()


# ---------------------------------------------------------
# Core Security & Entropy Logic
# ---------------------------------------------------------

def analyze_character_categories(password: str):
    """
    Identifies presence of character classes and calculates the
    theoretical character pool size R according to specification:
    - Lowercase: 26
    - Uppercase: 26
    - Numbers: 10
    - Special characters: 32 (ASCII punctuation)
    - Space: 1
    """
    has_lower = any(c.islower() for c in password)
    has_upper = any(c.isupper() for c in password)
    has_digit = any(c.isdigit() for c in password)
    has_space = " " in password
    
    # Symbols: printable punctuation or non-alphanumeric non-space
    symbol_set = set(string.punctuation)
    has_symbol = any((c in symbol_set or (not c.isalnum() and not c.isspace())) for c in password)
    
    count_lower = sum(1 for c in password if c.islower())
    count_upper = sum(1 for c in password if c.isupper())
    count_digit = sum(1 for c in password if c.isdigit())
    count_symbol = sum(1 for c in password if (c in symbol_set or (not c.isalnum() and not c.isspace())))
    count_space = sum(1 for c in password if c == " ")
    
    pool_size = 0
    pool_breakdown = []
    
    if has_lower:
        pool_size += 26
        pool_breakdown.append("26 (a-z)")
    if has_upper:
        pool_size += 26
        pool_breakdown.append("26 (A-Z)")
    if has_digit:
        pool_size += 10
        pool_breakdown.append("10 (0-9)")
    if has_symbol:
        pool_size += 32
        pool_breakdown.append("32 (Special)")
    if has_space:
        pool_size += 1
        pool_breakdown.append("1 (Space)")
        
    return {
        "has_lower": has_lower,
        "has_upper": has_upper,
        "has_digit": has_digit,
        "has_symbol": has_symbol,
        "has_space": has_space,
        "count_lower": count_lower,
        "count_upper": count_upper,
        "count_digit": count_digit,
        "count_symbol": count_symbol,
        "count_space": count_space,
        "unique_characters": len(set(password)),
        "pool_size": pool_size,
        "pool_breakdown": " + ".join(pool_breakdown) if pool_breakdown else "0"
    }


def calculate_entropy(length: int, pool_size: int):
    """
    H = L * log2(R)
    """
    if length <= 0 or pool_size <= 0:
        return 0.0
    return length * math.log2(pool_size)


def classify_strength(entropy: float, in_breach_list: bool, patterns: list = None):
    """
    Classification based on educational entropy ranges:
    < 28 bits:  Very Weak
    28-35 bits: Weak
    36-59 bits: Moderate
    60-79 bits: Strong
    >= 80 bits: Very Strong

    Educational security rules:
    - If found in local breach dataset: Flagged and downgraded to Weak/Very Weak
      because theoretical search space does not protect against known leaked lists.
    - If human predictability patterns exist (e.g., sequential sequences or keyboard walks):
      Downgrades Strong to Moderate to reflect real-world predictability.
    """
    # Base theoretical classification
    if entropy < 28.0:
        tier = "Very Weak"
        color = "#EF4444"       # Red
        badge_class = "danger"
        score_percent = min(25, max(5, int((entropy / 28.0) * 25)))
        summary = "Extremely vulnerable to instant guessing and automated brute-force attacks."
    elif 28.0 <= entropy <= 35.99:
        tier = "Weak"
        color = "#F97316"       # Orange
        badge_class = "warning"
        score_percent = int(25 + ((entropy - 28) / (36 - 28)) * 20)
        summary = "Vulnerable to dictionary attacks and moderate offline cracking."
    elif 36.0 <= entropy <= 59.99:
        tier = "Moderate"
        color = "#EAB308"       # Yellow
        badge_class = "moderate"
        score_percent = int(45 + ((entropy - 36) / (60 - 36)) * 25)
        summary = "Reasonable for non-critical accounts, but may yield to dedicated GPU clusters."
    elif 60.0 <= entropy <= 79.99:
        tier = "Strong"
        color = "#10B981"       # Emerald Green
        badge_class = "strong"
        score_percent = int(70 + ((entropy - 60) / (80 - 60)) * 20)
        summary = "Good security margin. Unfeasible for standard brute-force attacks."
    else:
        tier = "Very Strong"
        color = "#06B6D4"       # Cyan
        badge_class = "very-strong"
        score_percent = min(100, int(90 + min(10, (entropy - 80) / 4)))
        summary = "Exceptional search space. Virtually immune to theoretical brute-force methods."

    # Rule 1: Breach list override
    if in_breach_list:
        if entropy < 28.0:
            tier = "Very Weak"
            score_percent = 10
        else:
            tier = "Weak"
            score_percent = 25
        color = "#EF4444"
        badge_class = "danger"
        summary = "Compromised! Found in local breach list. Theoretical entropy does not protect a known leaked password."

    # Rule 2: Predictable pattern degradation (if not already breached)
    elif patterns and len(patterns) > 0:
        if tier in ["Strong", "Very Strong"]:
            tier = "Moderate"
            color = "#EAB308"
            badge_class = "moderate"
            score_percent = min(score_percent, 55)
            summary = "Downgraded to Moderate: Contains predictable human patterns (e.g., sequences or common templates) that attackers exploit."

    return {
        "tier": tier,
        "color": color,
        "badge_class": badge_class,
        "score_percent": score_percent,
        "summary": summary
    }


def check_breach_status(password: str):
    """
    Checks whether password appears in local dataset.
    """
    if not password:
        return {
            "in_breach_list": False,
            "status_text": "NO",
            "rank": None,
            "details": "Enter a password to check against the local breach dataset."
        }
        
    # Check exact match
    if password in BREACH_DATASET:
        rank = BREACH_DATASET[password]
        rank_msg = f" (Rank #{rank:,} in breached passwords database)" if rank else ""
        return {
            "in_breach_list": True,
            "status_text": "YES",
            "rank": rank,
            "is_case_insensitive": False,
            "details": f"WARNING: Password found in the local common-password dataset{rank_msg}."
        }
        
    # Check case-insensitive match for helpful guidance
    if password.lower() in BREACH_DATASET_LOWER:
        rank = BREACH_DATASET_LOWER[password.lower()]
        return {
            "in_breach_list": True,
            "status_text": "YES (Case Variant)",
            "rank": rank,
            "is_case_insensitive": True,
            "details": f"WARNING: Lowercase version of this password appears in the breach dataset (Rank #{rank:,}). Attackers frequently test case variations."
        }
        
    return {
        "in_breach_list": False,
        "status_text": "NO",
        "rank": None,
        "is_case_insensitive": False,
        "details": f"Not found in the local dataset ({DATASET_STATS['total_passwords']:,} passwords). Note: This does not guarantee it has never appeared in other online breaches."
    }


def detect_patterns(password: str):
    """
    Identifies common human predictability patterns:
    - Repeated characters (e.g., 'aaaa', '111')
    - Sequential numbers or letters (e.g., '12345', 'abcdef')
    - Keyboard walks ('qwerty', 'asdfgh')
    - Common template patterns (e.g., TitleWord + Digits + SpecialChar)
    """
    patterns = []
    
    if len(password) < 2:
        return patterns
        
    # 1. Repeated consecutive characters
    repeats = []
    current_char = password[0]
    current_count = 1
    for c in password[1:]:
        if c == current_char:
            current_count += 1
        else:
            if current_count >= 3:
                repeats.append(f"'{current_char * current_count}'")
            current_char = c
            current_count = 1
    if current_count >= 3:
        repeats.append(f"'{current_char * current_count}'")
        
    if repeats:
        patterns.append({
            "type": "Repeated Characters",
            "severity": "high",
            "desc": f"Repeated sequence detected: {', '.join(repeats)}. This drastically reduces real-world entropy."
        })
        
    # 2. Sequential characters (numbers or letters)
    lower_pw = password.lower()
    seq_num = "01234567890123456789"
    seq_num_rev = "98765432109876543210"
    seq_alpha = "abcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyz"
    seq_alpha_rev = "zyxwvutsrqponmlkjihgfedcbazyxwvutsrqponmlkjihgedcba"
    
    found_seqs = []
    for seq_pattern in [seq_num, seq_num_rev, seq_alpha, seq_alpha_rev]:
        for i in range(len(seq_pattern) - 3):
            sub = seq_pattern[i:i+4]
            if sub in lower_pw and sub not in found_seqs:
                found_seqs.append(sub)
                
    if found_seqs:
        patterns.append({
            "type": "Sequential Sequence",
            "severity": "high",
            "desc": f"Predictable sequence detected ({', '.join(found_seqs[:3])}). Standard wordlists test sequential patterns first."
        })
        
    # 3. Keyboard walks
    keyboard_walks = ["qwerty", "asdfgh", "zxcvbn", "1qaz", "2wsx", "zaq1", "qwer", "asdf", "zxcv", "poiuy", "lkjhg", "mnbvc"]
    found_walks = [w for w in keyboard_walks if w in lower_pw]
    if found_walks:
        patterns.append({
            "type": "Keyboard Walk",
            "severity": "high",
            "desc": f"Keyboard layout pattern detected ('{found_walks[0]}'). Easy for dictionary attacks to crack."
        })
        
    # 4. Predictable Template (e.g. Word + digits/symbols at end like Admin@123)
    if (len(password) >= 6 and 
        password[0].isupper() and 
        password[1:5].isalpha() and 
        (password[-1].isdigit() or password[-1] in string.punctuation or password[-2:].isdigit())):
        patterns.append({
            "type": "Predictable Suffix Template",
            "severity": "medium",
            "desc": "Follows common human pattern: Capitalized Word + Special character/Year at the end (e.g. Summer2026!)."
        })
        
    return patterns


def format_time_duration(seconds: float):
    """
    Converts seconds into human-readable duration string.
    """
    if seconds < 0.001:
        return "Instant (< 1 ms)"
    elif seconds < 1.0:
        return f"{int(seconds * 1000)} milliseconds"
    elif seconds < 60:
        return f"{seconds:.1f} seconds"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.1f} minutes"
    elif seconds < 86400:
        hours = seconds / 3600
        return f"{hours:.1f} hours"
    elif seconds < 31536000:
        days = seconds / 86400
        return f"{days:.1f} days"
    elif seconds < 31536000 * 100:
        years = seconds / 31536000
        return f"{years:.1f} years"
    elif seconds < 31536000 * 1000000:
        years = seconds / 31536000
        return f"{int(years):,} years"
    elif seconds < 31536000 * 1000000000:
        m_years = seconds / (31536000 * 1000000)
        return f"{m_years:.1f} Million years"
    else:
        b_years = seconds / (31536000 * 1000000000)
        if b_years > 1e12:
            return "Trillions of centuries"
        return f"{b_years:.1f} Billion years"


def calculate_crack_times(entropy: float):
    """
    Estimates time to guess the search space on average:
    Guesses = 2^(H - 1)
    Scenarios:
    1. Online Web Login (Throttled/Rate-limited): 100 guesses/sec
    2. Single Modern GPU (Hashcat fast hashes): 10,000,000,000 (10 GH/s)
    3. State-Sponsored GPU Cluster / Supercomputer: 10,000,000,000,000 (10 TH/s)
    """
    if entropy <= 0:
        return {
            "online": "Instant",
            "fast_gpu": "Instant",
            "supercomputer": "Instant",
            "combinations_formula": "0"
        }
        
    # Cap exponent calculation to avoid overflow
    if entropy > 120:
        return {
            "online": "Trillions of centuries",
            "fast_gpu": "Billions of years",
            "supercomputer": "Millions of years",
            "combinations_formula": f"2^{entropy:.1f}"
        }
        
    avg_guesses = 2 ** (entropy - 1)
    
    online_sec = avg_guesses / 100.0
    gpu_sec = avg_guesses / 10_000_000_000.0
    super_sec = avg_guesses / 10_000_000_000_000.0
    
    return {
        "online": format_time_duration(online_sec),
        "fast_gpu": format_time_duration(gpu_sec),
        "supercomputer": format_time_duration(super_sec),
        "combinations_formula": f"2^{entropy:.2f}"
    }


def full_password_evaluation(password: str):
    """
    Runs full evaluation workflow:
    1. Analyze characters and pool size R
    2. Calculate entropy H = L * log2(R)
    3. Check local breach list
    4. Classify strength
    5. Detect human patterns
    6. Estimate crack times
    7. Generate recommendations
    """
    clean_pw = password if password is not None else ""
    length = len(clean_pw)
    
    char_analysis = analyze_character_categories(clean_pw)
    pool_size = char_analysis["pool_size"]
    
    entropy = calculate_entropy(length, pool_size)
    breach_info = check_breach_status(clean_pw)
    patterns = detect_patterns(clean_pw)
    strength = classify_strength(entropy, breach_info["in_breach_list"], patterns)
    crack_times = calculate_crack_times(entropy)
    
    # Recommendations
    recommendations = []
    if breach_info["in_breach_list"]:
        recommendations.append("CRITICAL: Change this password immediately. It is exposed in public breach databases.")
    if length < 12:
        recommendations.append(f"Increase password length (currently {length} chars). Aim for at least 14-16 characters.")
    if not char_analysis["has_upper"]:
        recommendations.append("Add uppercase letters (A-Z) to expand character pool.")
    if not char_analysis["has_lower"]:
        recommendations.append("Add lowercase letters (a-z).")
    if not char_analysis["has_digit"]:
        recommendations.append("Add numbers (0-9) to increase uncertainty.")
    if not char_analysis["has_symbol"]:
        recommendations.append("Add special characters or symbols (!@#$%^&*) to maximize search space.")
    if patterns:
        recommendations.append("Avoid obvious sequences, keyboard walks (like 'qwerty'), and repetitive characters.")
    if not recommendations:
        recommendations.append("Password has strong entropy and does not appear in local breach files! Keep it unique across services.")

    # Formula step-by-step representation
    if length > 0 and pool_size > 0:
        log2_val = math.log2(pool_size)
        formula_math = f"H = {length} × log₂({pool_size}) = {length} × {log2_val:.4f} ≈ {entropy:.2f} bits"
    else:
        formula_math = "H = 0 × log₂(0) = 0.00 bits"

    return {
        "password": clean_pw,
        "length": length,
        "entropy": round(entropy, 2),
        "formula_math": formula_math,
        "char_analysis": char_analysis,
        "strength": strength,
        "breach_info": breach_info,
        "patterns": patterns,
        "crack_times": crack_times,
        "recommendations": recommendations,
        "dataset_stats": DATASET_STATS
    }


# ---------------------------------------------------------
# Password Generator
# ---------------------------------------------------------

def generate_random_password(length=16, use_upper=True, use_lower=True, use_digits=True, use_symbols=True):
    length = max(8, min(64, int(length)))
    
    char_pools = []
    guaranteed = []
    
    if use_lower:
        char_pools.append(string.ascii_lowercase)
        guaranteed.append(secrets.choice(string.ascii_lowercase))
    if use_upper:
        char_pools.append(string.ascii_uppercase)
        guaranteed.append(secrets.choice(string.ascii_uppercase))
    if use_digits:
        char_pools.append(string.digits)
        guaranteed.append(secrets.choice(string.digits))
    if use_symbols:
        symbols = "!@#$%^&*()-_=+[]{}|;:,.<>?"
        char_pools.append(symbols)
        guaranteed.append(secrets.choice(symbols))
        
    if not char_pools:
        # Deny generation if all character options are unchecked
        return None
        
    all_chars = "".join(char_pools)
    remaining_length = max(0, length - len(guaranteed))
    password_chars = guaranteed + [secrets.choice(all_chars) for _ in range(remaining_length)]
    
    # Shuffle cryptographically
    shuffled = []
    temp_list = list(password_chars)
    while temp_list:
        idx = secrets.randbelow(len(temp_list))
        shuffled.append(temp_list.pop(idx))
        
    return "".join(shuffled)


# ---------------------------------------------------------
# Flask Web Routes
# ---------------------------------------------------------

@app.route("/", methods=["GET", "POST"])
def index():
    initial_password = ""
    result = None
    
    if request.method == "POST":
        initial_password = request.form.get("password", "")
        if initial_password:
            result = full_password_evaluation(initial_password)
            
    return render_template(
        "index.html", 
        result=result, 
        initial_password=initial_password,
        dataset_stats=DATASET_STATS
    )


@app.route("/api/check", methods=["POST"])
def api_check():
    data = request.get_json(silent=True) or {}
    password = data.get("password", "")
    evaluation = full_password_evaluation(password)
    return jsonify(evaluation)


@app.route("/api/generate", methods=["GET"])
def api_generate():
    length = request.args.get("length", 16, type=int)
    use_upper = request.args.get("upper", "true").lower() == "true"
    use_lower = request.args.get("lower", "true").lower() == "true"
    use_digits = request.args.get("digits", "true").lower() == "true"
    use_symbols = request.args.get("symbols", "true").lower() == "true"
    
    if not (use_upper or use_lower or use_digits or use_symbols):
        return jsonify({
            "error": "Action Denied: Please select at least one character type (Uppercase, Lowercase, Digits, or Symbols) to generate a password."
        }), 400

    generated = generate_random_password(
        length=length,
        use_upper=use_upper,
        use_lower=use_lower,
        use_digits=use_digits,
        use_symbols=use_symbols
    )
    
    if not generated:
        return jsonify({
            "error": "Action Denied: Please select at least one character type to generate a password."
        }), 400
        
    evaluation = full_password_evaluation(generated)
    return jsonify({
        "password": generated,
        "evaluation": evaluation
    })


@app.route("/api/stats", methods=["GET"])
def api_stats():
    return jsonify(DATASET_STATS)


if __name__ == "__main__":
    host = os.environ.get("FLASK_HOST", "127.0.0.1")
    port = int(os.environ.get("FLASK_PORT", 5000))
    debug = os.environ.get("FLASK_DEBUG", "True").lower() in ("true", "1", "yes")

    print("[*] Starting Password Strength & Breach-Pattern Checker...")
    print(f"[*] Dataset: {DATASET_STATS['total_passwords']:,} passwords loaded offline.")
    print(f"[*] Access the dashboard at http://{host}:{port}")
    app.run(host=host, port=port, debug=debug)
