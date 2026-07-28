Markdown
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

## 📁 Project Structure

├── src/                          # Application source code & scripts
│   ├── main.py                   # Entry point for the analysis tool (Runs logic & report gen)
│   ├── auth_server.py            # The authentication server (Flask)
│   ├── attacker.py               # The simulation engine for attacks
│   ├── run_experiments.py        # Orchestrates the various experiment scenarios
│   ├── create_data.py            # Generates synthetic users.json and wordlist.txt
│   ├── run_combinations.py       # Runs combination tests for protections
│   ├── create_wordlist.py        # Generates the wordlist for brute force attacks
│   ├── logic.py                  # Data processing and graph generation logic
│   ├── report_gen.py             # HTML report generation logic
│   ├── analyze.py                # Standalone analysis script
│   ├── test_env.py               # Test script for environment setup
│   ├── run_all.bat               # Batch script for Windows automation
│   └── run_experiment.ps1        # PowerShell script for single experiment execution
│
├── configs/                      # Configuration files (e.g. config_sha256_no_protection.json)
│   └── config_*.json
│
├── data/                         # Datasets & password dictionaries
│   ├── users.json                # User dataset (30 users, varied strength)
│   └── wordlist.txt              # Dictionary for brute-force attacks
│
├── logs/                         # Directory for raw JSON logs 
│   └── attempts_*.log            # Individual experiment logs
│
├── output/                       # Directory for analysis results 
│   ├── graphs/                   # Generated visualizations (PNG)
│   └── analysis_report.html      # Final interactive report
│
└── requirements.txt              # List of Python dependencies
🧪 Experiments Included
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

📊 Output Files
logs/: Contains all raw log files (JSON lines) generated during the experiments.

output/graphs/: Contains all PNG graphs created by the analysis logic.

output/analysis_report.html: The final interactive report including graphs, summaries, and timestamp.

⚙️ Installation
1. Create Virtual Environment
Bash
python -m venv .venv
2. Activate Environment
PowerShell
.\.venv\Scripts\activate
3. Install Dependencies
Bash
pip install -r requirements.txt
🚀 How to Run
4. Generate Required Data
Generate the dictionary and user lists required for the attacks:

Bash
python create_wordlist.py
5. Execute Attack Scenarios
Execute the attack scenarios (combination tests & the main experiments separately):

Run Combinations:
Bash
python run_combinations.py
OR Run Standard Experiments:
Bash
python run_experiments.py
OR Run Everything via Batch:
Alternatively, run everything at once using the batch file:

DOS
.\run_all.bat
6. Run Analysis
Generates output graphs and metrics:

Bash
python analyze.py
7. Generate Final Report
Generates the interactive HTML report:

Bash
python main.py
🔄 Summary of Execution Order
Option A: Complete Run from Scratch
For a complete run from scratch, execute these commands in order:

Bash
python create_wordlist.py
python run_combinations.py
python run_experiments.py
python analyze.py
python main.py
💡 Tip: Before performing a new full run, it is recommended to delete or move the logs and graphs folders from the previous run in /output & /logs to prevent statistical and graphical errors.

Option B: Batch Automation
Or simply run the batch file and analysis workflow:

Bash
.\run_all.bat
python analyze.py
python main.py