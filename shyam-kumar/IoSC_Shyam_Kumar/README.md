# Password Strength & Breach-Pattern Checker

A Python-based, privacy-first cybersecurity web application designed to evaluate password security using Shannon theoretical entropy calculation and an offline local breached-password database.

Instead of relying solely on superficial complexity rules (e.g., must contain 1 uppercase letter and 1 symbol), this application estimates the actual search space of a password, detects human predictability patterns (sequential characters, keyboard walks, repetitions), and checks whether the password appears in a locally stored dataset of compromised passwords.

> Key Security Insight: Password security is not merely about satisfying rigid complexity rules. Length, character variety, true randomness, and absence from leaked password databases are the true foundations of security.

---

 🌟 Key Features

* 🔐 Theoretical Entropy Engine: Calculates Shannon entropy in bits using H = L \times \log_2(R).
* 🗃️ Offline Breach-Pattern Checking: Instantly looks up passwords against local datasets (such as `10millionPasswords.csv` with over 1,000,000 breached passwords and `common_passwords.txt`) with exact breach rank detection.
* 🔒 100% Local & Privacy-Preserving: No passwords or hashes are ever transmitted over the network or sent to third-party APIs.
* 📏 Character-Set & Pool Analysis: Real-time breakdown of lowercase (a-z), uppercase (A-Z), numbers (0-9), special characters (!@\#\), and pool size R.
* 📈 Educational Classification: Categorizes passwords into *Very Weak* (<28 bits), *Weak* (28–35 bits), *Moderate* (36–59 bits), *Strong* (60–79 bits), and *Very Strong* (≥80 bits).
* ⚡ Instant Real-Time Evaluation: Dynamic debounced client evaluation as you type, with zero-lag responsiveness.
* 🛡️ Predictability & Pattern Detection: Detects sequential numbers (`12345`), alphabetical sequences (`abcdef`), keyboard walks (`qwerty`, `asdfgh`), and repeated characters.
* ⏱️ Brute-Force Crack Time Estimates: Multi-scenario cracking duration estimates (throttled online attack, modern 10 GH/s GPU rig, and 10 TH/s supercomputer cluster).
* 🎲 Cryptographically Secure Generator: Built-in password generator using Python's `secrets` module (CSPRNG).
* 🖥️ Modern Cybersecurity UI: Glassmorphic dark aesthetic with glowing status meters, live formula breakdown, and interactive educational tables.

---

 🧮 Mathematical Entropy Calculation

Entropy (H) represents the theoretical uncertainty or size of the password's search space:

H = L \times \log_2(R)

Where:
* H = Estimated entropy in bits
* L = Password length (number of characters)
* R = Estimated character pool size based on active character classes:
  - Lowercase letters (a-z): 26
  - Uppercase letters (A-Z): 26
  - Digits (0-9): 10
  - Special characters & symbols: 32
  - Space: 1

# Calculation Examples

1. Weak Password (`password`):
   - Length L = 8
   - Character Pool R = 26 (lowercase only)
   - H = 8 \times \log_2(26) \approx 37.60 \text{ bits}
   - Breach Status: ⚠ Found in breach dataset (Rank #2 most breached password in history).

2. Predictable Password (`Password123`):
   - Length L = 11
   - Character Pool R = 26 + 26 + 10 = 62
   - H = 11 \times \log_2(62) \approx 65.50 \text{ bits}
   - Breach Status: ⚠ Flagged in breach dataset & sequential pattern `123` detected.

3. Random Password (`x7!Qm9#Lp2`):
   - Length L = 10
   - Character Pool R = 26 + 26 + 10 + 32 = 94
   - H = 10 \times \log_2(94) \approx 65.55 \text{ bits}
   - Breach Status: ✓ Clean (Not found in local dataset).

---

 📊 Strength Classification Scale

| Entropy Range | Classification | Theoretical Combinations | Real-World Resilience |
| ------------- | -------------- | ------------------------ | --------------------- |
| `< 28 bits` | Very Weak | < 2.68 \times 10^8 | Cracked in fractions of a second |
| `28–35 bits` | Weak | 2.68 \times 10^8 - 6.87 \times 10^{10} | Susceptible to fast dictionary lists |
| `36–59 bits` | Moderate | Up to 1.15 \times 10^{18} | Resists basic online attacks |
| `60–79 bits` | Strong | Up to 1.20 \times 10^{24} | Resists dedicated GPU cracking rigs |
| `≥ 80 bits` | Very Strong | > 1.20 \times 10^{24} | Computationally unfeasible to brute force |

> Note: Even if a password has high theoretical entropy, it will be flagged as Compromised if it appears in the local breached database.

---

 📁 Project Structure

```text
password-strength-checker/
│
├── app.py                      # Flask backend, entropy math, and breach dataset loader
├── common_passwords.txt        # Standard offline common password dataset
├── 10millionPasswords.csv      # 1,000,000+ breached passwords dataset with rank metrics
├── .env                        # Local environment variables (ignored by git)
├── .env.example                # Example environment template
├── .gitignore                  # Git ignore rules for cache, venv, and secrets
├── requirements.txt            # Project dependencies
├── templates/
│   └── index.html              # Modern, responsive UI with formula & breakdown cards
├── static/
│   ├── style.css               # Cybersecurity dark theme with glassmorphism
│   └── script.js               # Real-time AJAX analysis, copy, visibility toggle, generator
└── README.md                   # Full documentation and theoretical explanations
```

---

 🚀 Installation & Running Locally

# 1. Prerequisites
Ensure Python 3.8+ is installed on your computer:
```bash
python --version
```

# 2. Install Dependencies
```bash
pip install -r requirements.txt
```

# 3. Environment Configuration (Optional)
Copy `.env.example` to `.env` and configure your settings if needed:
```bash
cp .env.example .env
```

# 4. Start the Server
```bash
python app.py
```

Output:
```text
[*] Successfully loaded 999,996 passwords from 10millionPasswords.csv
[*] Starting Password Strength & Breach-Pattern Checker...
[*] Access the dashboard at http://127.0.0.1:5000
```

Open `http://127.0.0.1:5000` in your web browser.

---

 🛡️ Privacy & Security Design

* Zero Outbound Requests: All computations and dataset queries run on your CPU inside the local Flask process.
* No Telemetry or Logging: Passwords entered in the interface are never recorded to disk, log files, or databases.
* Safe Educational Testing: Users and students can safely test potential passwords without risk of exposing credentials to online breach lookup APIs.

---

 💡 Educational Takeaways

1. Why Rules Alone Fail: Attackers know humans follow templates like `Summer2024!` or `Welcome@123`. Complexity rules without randomness create false security.
2. Search Space Geometry: Every additional character exponentially expands the search space (R^L). A 16-character passphrase is vastly stronger than an 8-character complex string.
3. Breach Databases: Over 80% of data breaches involve compromised or reused passwords. Avoiding known lists is the single most critical step in password defense.
