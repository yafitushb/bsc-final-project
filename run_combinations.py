import json
import time
import os

def run_experiment(name, config_updates):
    """
    Executes a specific attack simulation based on the provided configuration updates.
    This function loads the base configuration, applies specific protection settings,
    and runs the attacker script.
    """
    print(f"\n=== Running experiment: {name} ===")

    # Load the base configuration template (using medium strength profile)
    try:
        with open("config_strength_medium.json", "r") as f:
            base = json.load(f)
    except FileNotFoundError:
        print("Error: Base configuration file 'config_strength_medium.json' not found.")
        return

    # Apply configuration overrides for the specific experiment
    for key, value in config_updates.items():
        # Handle nested configuration keys (e.g., 'protections.rate_limit.enabled')
        if "." in key:
            parts = key.split(".")
            if len(parts) == 2:
                if parts[0] not in base: base[parts[0]] = {}
                base[parts[0]][parts[1]] = value
            elif len(parts) == 3:
                if parts[0] not in base: base[parts[0]] = {}
                if parts[1] not in base[parts[0]]: base[parts[0]][parts[1]] = {}
                base[parts[0]][parts[1]][parts[2]] = value
        else:
            base[key] = value

    # Set experiment metadata and output log path
    if "experiment" not in base: base["experiment"] = {}
    base["experiment"]["name"] = name
    base["logging"]["output_file"] = f"logs/attempts_{name}.log"

    # Save the temporary configuration file for the attacker script
    with open("config_temp.json", "w") as f:
        json.dump(base, f, indent=2)

    # Clean up previous log files for this experiment to ensure data integrity
    log_file = f"logs/attempts_{name}.log"
    if os.path.exists(log_file):
        os.remove(log_file)

    # Execute the attack
    print(f"[*] Launching attacker for {name}...")
    os.system("python attacker.py --config config_temp.json")
    print(f"[+] Experiment {name} completed.")
    
    # Brief pause to allow file I/O operations to finalize
    time.sleep(1)

# --- Main Execution Block ---

print("--- Starting Security Mechanism Analysis (Combinations) ---")

# Ensure logs directory exists
if not os.path.exists("logs"):
    os.makedirs("logs")

# 1. Salt Only
# Isolating the effect of cryptographic salting without active protections.
run_experiment("sha256_salt", {
    "attack.type": "bruteforce",
    "hashing.mode": "sha256",
    "protections.rate_limit.enabled": False,
    "protections.lockout.enabled": False,
    "protections.captcha.enabled": False
})

# 2. Pepper Only
# Testing the effect of a server-side secret (Pepper) added to the hash.
run_experiment("sha256_pepper", {
    "attack.type": "bruteforce",
    "hashing.mode": "sha256",
    "protections.rate_limit.enabled": False,
    "protections.lockout.enabled": False,
    "protections.captcha.enabled": False
})

# 3. Account Lockout Only
# Evaluation of the account lockout mechanism after repeated failures.
run_experiment("sha256_lockout", {
    "attack.type": "bruteforce",
    "hashing.mode": "sha256",
    "protections.lockout.enabled": True,
    "protections.rate_limit.enabled": False,
    "protections.captcha.enabled": False
})

# 4. CAPTCHA Only
# Evaluation of CAPTCHA challenges as a mitigation strategy against bots.
run_experiment("sha256_captcha", {
    "attack.type": "bruteforce_captcha", 
    "hashing.mode": "sha256",
    "protections.captcha.enabled": True,
    "protections.rate_limit.enabled": False,
    "protections.lockout.enabled": False
})

# 5. Rate Limiting Only
# Testing the throttling mechanism (time delay) on failed attempts.
run_experiment("sha256_rate_limit", {
    "attack.type": "bruteforce",
    "hashing.mode": "sha256",
    "protections.rate_limit.enabled": True,
    "protections.lockout.enabled": False,
    "protections.captcha.enabled": False
})

# 6. Password Spraying Attack
# Simulating a lateral movement attempt using common passwords across multiple users.
# Requires 'common_passwords.txt' to be present.
run_experiment("spraying_weak", {
    "attack.type": "spraying",
    "attack.spraying_user_file": "common_passwords.txt", 
    "protections.rate_limit.enabled": False,
    "protections.lockout.enabled": False
})

print("\n=== All experiments completed successfully ===")