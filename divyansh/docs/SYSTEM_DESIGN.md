# System Architecture & Technical Specifications — PASSMAN

**Project:** PASSMAN — CLI Password Manager & Security Tool  
**Candidate:** Divyansh Gupta  
**Track:** Cybersecurity  

---

## 1. System Overview

PASSMAN is a zero-dependency, local-first Command Line Interface (CLI) application designed to evaluate, test, and generate passwords securely without exposing data over network interfaces.

```text
+-------------------------------------------------------------------------+
|                        Interactive CLI Engine                           |
|                             (passman.py)                                |
+-------------------------------------------------------------------------+
        |                                 |                               |
        v                                 v                               v
+------------------+           +------------------+          +------------------+
| Password Breach  |           | Password         |          | Password         |
| Checker Module   |           | Generator Module |          | Strength Tester  |
+------------------+           +------------------+          +------------------+
        |                                 |                               |
        v                                 v                               v
+------------------+           +------------------+          +------------------+
| Local Dataset    |           | SystemRandom()   |          | Entropy Formula  |
| Lookup Engine    |           | Sampling & Check |          | E = L * log2(N)  |
+------------------+           +------------------+          +------------------+
```

---

## 2. Component Specifications

### 2.1 Password Breach Checker
- **Data Source:** `Common passwords.txt` (local text file database containing compromised passwords).
- **Lookup Complexity:** $O(1)$ set lookup after initial $O(N)$ load into memory.
- **Privacy Model:** 100% offline, zero network requests, zero telemetry.

### 2.2 Password Generator
- **RNG:** Uses `random.SystemRandom()` for cryptographically secure pseudo-random number generation via OS entropy sources.
- **Criteria Enforcer:** Guarantees inclusion of at least one character from each selected character set (Uppercase, Lowercase, Digits, Special Characters).
- **Automated Verification:** Automatically verifies generated passwords against `Common passwords.txt` before displaying.

### 2.3 Entropy Strength Calculator
- **Mathematical Formula:** 
  $$E = L \times \log_2(N)$$
- **Character Pool Sizes ($N$):**
  - Lowercase (`a-z`): 26
  - Uppercase (`A-Z`): 26
  - Numbers (`0-9`): 10
  - Special characters / Punctuation: 32 (Total max pool: 94)

### 2.4 Rating Classification Scale
- **< 28 Bits:** Very Weak (🔴 Red)
- **28 – 35 Bits:** Weak (🔴 Red)
- **36 – 59 Bits:** Medium (🟡 Yellow)
- **60 – 126 Bits:** Strong (🟢 Green)
- **≥ 127 Bits:** Very Strong (🟢 Green)

---

## 3. Testing & Verification

The system includes automated unit test suites in `tests/test_passman.py` covering:
1. Entropy mathematical correctness.
2. Boundary classifications.
3. Common password breach lookups.
4. Cryptographic password generation criteria.
