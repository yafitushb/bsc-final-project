# 🔐 Authentication Security Analysis Project

![Python](https://img.shields.io/badge/Python-3.9+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-Framework-000000?style=for-the-badge&logo=flask&logoColor=white)
![Security](https://img.shields.io/badge/CyberSecurity-Research-red?style=for-the-badge)
![License](https://img.shields.io/badge/Academic-Research-blue?style=for-the-badge)

| 🎬 Live Demo & Telemetry Analytics |
| :---: |
| ![Demo](https://raw.githubusercontent.com/yafitushb/bsc-final-project/main/assets/demo.gif) |

---

## 📌 Overview

A modular authentication simulation environment designed to test and analyze the effectiveness of various security protections, including hashing algorithms, rate limiting, account lockout, CAPTCHA, TOTP, and peppering.

> ⚠️ **Academic Disclaimer:** This project is for educational and academic research purposes only. Do not use this code to target production systems.

> 🔬 **Experimental Consistency:** In order to maintain research consistency across the project, a fixed data ID (`group_seed: 123456789`) was defined. This demonstrates that user creation and attack scenarios are controlled rather than random. It ensures full authority over the experiment and proves that the attacker's success rates remain consistent across runs.

---

## 📄 Research & Documentation

This project includes a comprehensive academic research report and a summary presentation analyzing authentication mechanisms, hashing performance, and attack resistance.

* 📄 **[Full Research Report (PDF)](./docs/Research_Report_Authentication_Security.pdf)**
  * **In-depth Analysis:** Empirical comparison between SHA-256, Bcrypt, and Argon2id.
  * **Defense Mechanisms:** Evaluation of Rate Limiting, Account Lockout, CAPTCHA, TOTP, Pepper, and Clock Drift synchronization (90ms).
  * **Attack Vectors:** Detailed results from Brute-Force and Password Spraying simulations.

* 📊 **[Project Presentation (PDF)](./docs/Presentation_Authentication_Security.pdf)**
  * **Visual Summary:** Key findings, hashing latency graphs, and trade-off analysis between security and system performance.

---

## 📁 Project Structure

```text
├── docs/                                             # Academic documentation & presentation
│   ├── Research_Report_Authentication_Security.pdf   # Full research paper & empirical analysis
│   └── Presentation_Authentication_Security.pdf      # Visual presentation of findings & metrics
│
├── src/                                              # Application source code & scripts
│   ├── main.py                                       # Entry point for the analysis tool (Runs logic & report gen)
│   ├── auth_server.py                                # The authentication server (Flask)
│   ├── attacker.py                                   # The simulation engine for attacks
│   ├── run_experiments.py                            # Orchestrates the various experiment scenarios
│   ├── create_data.py                                # Generates synthetic users.json and wordlist.txt
│   ├── run_combinations.py                           # Runs combination tests for protections
│   ├── create_wordlist.py                            # Generates the wordlist for brute force attacks
│   ├── logic.py                                      # Data processing and graph generation logic
│   ├── report_gen.py                                 # HTML report generation logic
│   ├── analyze.py                                    # Standalone analysis script
│   ├── test_env.py                                   # Test script for environment setup
│   ├── run_all.bat                                   # Batch script for Windows automation
│   └── run_experiment.ps1                            # PowerShell script for single experiment execution
│
├── configs/                                          # Configuration files (e.g. config_sha256_no_protection.json)
│   └── config_*.json
│
├── data/                                             # Datasets & password dictionaries
│   ├── users.json                                    # User dataset (30 users, varied strength)
│   └── wordlist.txt                                  # Dictionary for brute-force attacks
│
├── logs/                                             # Directory for raw JSON logs 
│   └── attempts_*.log                                # Individual experiment logs
│
├── output/                                           # Directory for analysis results 
│   ├── graphs/                                       # Generated visualizations (PNG)
│   └── analysis_report.html                          # Final interactive report
│
└── requirements.txt                                  # List of Python dependencies


## 🧪 Experiments Included

1. Hash Mode & Protection Experiments
SHA256 — No Protection

SHA256 — Rate Limit: Limits login attempts per minute.

SHA256 — Lockout: Locks user after repeated failures.

bcrypt — No Protection

bcrypt — CAPTCHA: Triggered after configurable number of failures.

Argon2id — No Protection

Argon2id — TOTP: Two-factor authentication simulation.

Argon2id — Full Protection: Rate Limit + Lockout + CAPTCHA + Pepper.

Pepper: Secret server-side value added to password.

2. Password Strength Experiments
user01 – user10 → Weak passwords

user11 – user20 → Medium passwords

user21 – user26 → Strong passwords

user27 – user29 → Strong + TOTP

user30 → Mixed / Random strength

## 📊 Output Files

logs/: Contains all raw log files (JSON lines) generated during the experiments.

output/graphs/: Contains all PNG graphs created by the analysis logic.

output/analysis_report.html: The final interactive report including graphs, summaries, and timestamp.






## ⚙️ Installation & Usage

### 1. Create Virtual Environment
```bash
python -m venv .venv

### 2. Activate:
```powershell
.\.venv\Scripts\activate
```
 
### 3. Install Dependencies: 
```bash
pip install -r requirements.txt
```

### 4. How to Run: 
### Generate the dictionary and user lists required for the attacks.
```bash
python create_wordlist.py
```

### 5. Execute the attack scenarios (combination tests & the main experiments separately.
### Run Combinations:
```bash
python run_combinations.py
```

### 5.1 OR
### Run Standard Experiments:
```bash
python run_experiments.py
```

### 5.2 OR
### Alternatively, run everything at once using the batch file:
```dos
.\run_all.bat
```

### 6. Run Analysis (Generates Graphs):
```bash
python analyze.py
```

### 7. Generate Final Report (HTML):
```bash
python main.py
```

### Summary of Execution Order
### 1. For a complete run from scratch, execute these commands in order:
```bash
python create_wordlist.py
```
```bash
python run_combinations.py
```
```bash
python run_experiments.py
```
```bash
python analyze.py
```
```bash
python main.py
```

>  ⚠️ Note: Before performing a new full run, it is recommended to delete or move the logs and graphs folders from the previous run to /output & /logs in order to prevent statistical and graphical errors.

### 2. OR simply run the batch file:
```dos
.\run_all.bat
```
```bash
python analyze.py
```
```bash
python main.py
```
