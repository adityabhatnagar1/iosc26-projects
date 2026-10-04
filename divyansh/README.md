# PASSMAN — CLI Password Manager & Security Tool

> An interactive, privacy-focused Python Command-Line Interface (CLI) security tool providing offline password breach checking, entropy calculation, and secure password generation.

```text
 _______  _______  _______  _______  __   __  _______  __    _
|       ||   _   ||       ||       ||  |_|  ||   _   ||  |  | |
|    _  ||  |_|  ||  _____||  _____||       ||  |_|  ||   |_| |
|   |_| ||       || |_____ | |_____ |       ||       ||       |
|    ___||       ||_____  ||_____  ||       ||       ||  _    |
|   |    |   _   | _____| | _____| || ||_|| ||   _   || | |   |
|___|    |__| |__||_______||_______||_|   |_||__| |__||_|  |__|
```

**Track:** Cybersecurity  
**Candidate:** Divyansh Gupta  
**Github Username**: divyanshg221220  
**Phone Number**: 7065221206  
**Email ID**: divyansh.5319051925@std.ggsipu.ac.in

---

## 1. Overview

### What & Why
**PASSMAN** is an interactive, privacy-focused Python Command-Line Interface (CLI) security tool. It provides offline password breach checking against known compromised password datasets (`Common passwords.txt`), mathematically computes password entropy, generates cryptographically strong passwords, and provides instant strength assessments—all with **zero network dependencies** and **zero external package requirements**.

### Expected Outcome
The goal was to build a 100% private, zero-dependency local CLI utility that empowers users to verify credential safety, assess password resilience to brute-force attacks via mathematical entropy scoring ($E = L \times \log_2 N$), and generate non-compromised secure passwords without transmitting any data over the network.

---

## 2. Requirements

### Hardware
| Component | Qty | Purpose |
|---|---:|---|
| Host PC / Workstation | 1 | Environment for running Python 3 CLI |

### Software
| Tool / Library | Version | Purpose |
|---|---|---|
| Python | 3.6+ | Core runtime environment |
| `random` (Standard Library) | Built-in | Cryptographic & randomized character sampling |
| `math` (Standard Library) | Built-in | Logarithmic calculations for entropy scoring |
| `string` (Standard Library) | Built-in | Character set definitions (letters, digits, punctuation) |

**Constraints:** 100% offline execution (zero network requests), standard library only (zero external package dependencies), local file-based dataset lookup.

---

## 3. Design

### System Overview
PASSMAN operates through a menu-driven terminal UI. The system takes user inputs (candidate passwords, generation preferences, or menu choices) and routes them through three core execution modules:

1. **Password Breach Checker**: Queries a local database (`Common passwords.txt`) to verify if a candidate password appears in leaked credential sets.
2. **Entropy Calculator**: Calculates password resilience in bits ($E = L \times \log_2 N$) based on length and character set diversity.
3. **Password Generator**: Generates cryptographically randomized strings matching user length/character requirements, verifies non-compromise against the local dataset, and outputs entropy metrics.

```text
===========================================================================
                          Interactive CLI Terminal
===========================================================================
       |                               |                               |
       v                               v                               v
[1. Breach Checker]          [2. Password Generator]       [3. Strength Tester]
       |                               |                               |
       v                               v                               v
Local Dataset Lookup          Random Sampling & Verify        Entropy Calculations
 (`Common passwords.txt`)      (Non-compromised output)       (E = L * log2(N))
===========================================================================
```

### Key Decisions
* **100% Offline Architecture**: Avoided third-party cloud APIs (e.g., HaveIBeenPwned API) to guarantee that user credentials are never exposed to network traffic or external servers.
* **Zero External Dependencies**: Constructed strictly using built-in Python standard libraries (`random`, `math`, `string`) to ensure zero-setup execution on any system with Python 3.6+ while eliminating supply-chain vulnerabilities.
* **Entropy Scoring vs. Rule-Based Validation**: Utilized mathematical information entropy ($E = L \times \log_2 N$) instead of basic regex rule checks (e.g., mandatory special character counts) to measure actual brute-force resistance space.

---

## 4. Implementation

### How Entropy Scoring Works
Unlike basic regex checkers that only test character inclusion, PASSMAN measures password strength through **information entropy in bits**:

$$E = L \times \log_2(N)$$

Where:
* **$L$** = Length of the password.
* **$N$** = Total pool size of character sets present in the password:
  * Lowercase letters (`a-z`): $+26$
  * Uppercase letters (`A-Z`): $+26$
  * Digits (`0-9`): $+10$
  * Special characters / Punctuation: $+32$

### Strength Rating Scale

| Entropy (Bits) | Strength Rating | Visual Indicator | Search Space Complexity |
| :--- | :--- | :--- | :--- |
| **< 28 bits** | **Very Weak** | 🔴 Red | High vulnerability to brute-force attacks |
| **28 – 35 bits** | **Weak** | 🔴 Red | Low brute-force resistance |
| **36 – 59 bits** | **Medium** | 🟡 Yellow | Moderate protection against online guessing |
| **60 – 126 bits** | **Strong** | 🟢 Green | High resistance to offline cracking |
| **≥ 127 bits** | **Very Strong** | 🟢 Green | Cryptographic grade security |

### Core Algorithms
1. **Breach Checking (`passman.py`)**: Sanitizes user input and compares against loaded lines from `Common passwords.txt`.
2. **Secure Generation (`passman.py`)**: Prompts user for length and character flags, guarantees inclusion of at least one character from each selected pool, shuffles using `random.shuffle()`, and checks against the breach dataset prior to rendering.

---

## 5. Demonstration

### Quick Start & Execution

1. **Navigate to project directory**:
   ```bash
   cd divyansh
   ```

2. **Run PASSMAN**:
   ```bash
   python src/passman.py
   ```

3. **Run Unit Tests**:
   ```bash
   python -m unittest discover -s tests -p "test_*.py"
   ```

### Interactive Menu
```text
===========================================================================

     _______  _______  _______  _______  __   __  _______  __    _
    |       ||   _   ||       ||       ||  |_|  ||   _   ||  |  | |
    |    _  ||  |_|  ||  _____||  _____||       ||  |_|  ||   |_| |
    |   |_| ||       || |_____ | |_____ |       ||       ||       |
    |    ___||       ||_____  ||_____  ||       ||       ||  _    |
    |   |    |   _   | _____| | _____| || ||_|| ||   _   || | |   |
    |___|    |__| |__||_______||_______||_|   |_||__| |__||_|  |__|
        
===========================================================================
1. PASSWORD BREACH CHECKER
2. PASSWORD GENERATOR
3. PASSWORD STRENGTH TESTER
4. EXIT
===========================================================================
```

### Detailed Menu Features
* **1. Password Breach Checker**: Evaluates any entered string against `Common passwords.txt`. Displays `PASSWORD IS COMPROMISED` (Red) if found or `PASSWORD IS SAFE` (Green) if absent.
* **2. Password Generator**: Interactive prompts select length and character sets (Uppercase, Lowercase, Digits, Special Characters). Generates non-compromised passwords and displays calculated entropy & strength rating.
* **3. Password Strength Tester**: Evaluates user-supplied strings and outputs exact calculated entropy in bits alongside color-coded classification.

### Demonstration Video

[🎥 Watch PASSMAN Terminal Demonstration Video](./media/PASSMAN-Demo.mp4)

---

## 6. Final Result

### Working
- [x] **Password Breach Checker**: Instant local database lookup (`Common passwords.txt`).
- [x] **Secure Password Generator**: Configurable length/set parameters with guaranteed non-compromised output.
- [x] **Entropy Strength Tester**: Precise entropy calculation ($E = L \times \log_2 N$) with color-coded terminal feedback.
- [x] **100% Offline & Private Terminal UI**: Menu-driven interface requiring zero network requests and zero external libraries.

### Known Issues
* Database scope is restricted to entries present in the local `Common passwords.txt` file.

**Demo Video:** [🎥 Watch PASSMAN Demo Video](./media/PASSMAN-Demo.mp4)

---

## 7. Limitations & Improvements

**Limitations:**
* Local breach checking is bounded by the size of `Common passwords.txt`.
* Generated passwords are printed to console but not saved to an encrypted local vault.

**Next Steps:**
* Implement an encrypted local vault (using AES-GCM via standard `hashlib` / `secrets`) for secure password storage.
* Integrate larger custom dictionary files and k-Anonymity hash lookup capabilities.

---

## 8. Key Learnings

* Applied mathematical information entropy ($E = L \times \log_2 N$) to evaluate cryptographic strength over heuristic pattern matching.
* Developed responsive menu-driven terminal user interfaces using pure Python standard libraries.
* Enforced strict offline security practices to prevent credential exposure during strength testing and password generation.

---

## 9. Repository Structure

```text
divyansh/
├── README.md             # Project documentation (Template compliant)
├── LICENSE               # Project license file
├── src/                  # Source code directory
│   ├── passman.py        # Core application source code
│   └── Common passwords.txt # Local database of compromised passwords
├── hardware/             # Hardware files (N/A for software CLI)
├── docs/                 # System documentation & diagrams
│   └── SYSTEM_DESIGN.md  # Architecture & math entropy specification
├── tests/                # Automated unit testing suite
│   └── test_passman.py   # Unit tests (unittest framework)
└── media/                # Demonstration videos & media
    └── PASSMAN-Demo.mp4  # Terminal execution recording
```

---

## 10. Ownership & Rights Disclaimer

> ⚠️ **Notice**: This project was built and completed entirely by **Divyansh Gupta**. IOSC (Intel oneAPI Club / iOSC) does **not** possess or hold any rights, intellectual property, or copyright over this project, its source code, or associated assets. All rights are reserved solely by Divyansh Gupta.


