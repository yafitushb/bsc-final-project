import json
import shutil
import time
import os

def run_experiment(name, config_updates):
    print(f"\n=== Running experiment: {name} ===")

    # Load base config
    with open("config_strength_medium.json", "r") as f:
        # We use one of the existing configs as a base template
        base = json.load(f)

    # Apply updates
    for key, value in config_updates.items():
        if "." in key:
            section, subkey = key.split(".", 1)
            # Handle deeper nesting if needed (simple 2-level here)
            if "." in subkey:
                subkey1, subkey2 = subkey.split(".")
                if section not in base: base[section] = {}
                if subkey1 not in base[section]: base[section][subkey1] = {}
                base[section][subkey1][subkey2] = value
            else:
                if section not in base: base[section] = {}
                base[section][subkey] = value
        else:
            base[key] = value
    
    # Set same experiment name
    if "experiment" not in base: base["experiment"] = {}
    base["experiment"]["name"] = name

    # Set log file
    base["files"] = base.get("files", {})
    base["logging"]["output_file"] = f"logs/attempts_{name}.log"

    # Save temp config
    with open("config_temp.json", "w") as f:
        json.dump(base, f, indent=2)

    # Remove old log if exists
    log_path = f"logs/attempts_{name}.log"
    if os.path.exists(log_path):
        os.remove(log_path)

    # Run attacker
    print("Running attacker...")
    os.system("python attacker.py --config config_temp.json")

    print(f"Experiment {name} completed.")
    time.sleep(1)


# Ensure logs folder exists
os.makedirs("logs", exist_ok=True)

# Baseline - No Protection
run_experiment("no_protection", {
    "attack.type": "bruteforce",
    "protections.rate_limit.enabled": False,
    "protections.lockout.enabled": False,
    "protections.captcha.enabled": False,
    "hashing.mode": "sha256"
})

# All Protections Enabled
run_experiment("with_protection", {
    "attack.type": "bruteforce_captcha",
    "protections.rate_limit.enabled": True,
    "protections.lockout.enabled": True,
    "protections.captcha.enabled": True,
    "hashing.mode": "sha256"
})

# Bcrypt Mode
run_experiment("bcrypt", {
    "attack.type": "bruteforce",
    "hashing.mode": "bcrypt",
    "protections.rate_limit.enabled": True
})

# Argon2id Mode
run_experiment("argon2id", {
    "attack.type": "bruteforce",
    "hashing.mode": "argon2id",
    "protections.rate_limit.enabled": True
})

# Registration Endpoint Test
run_experiment("registration_test", {
    "attack.type": "test_register",
    "hashing.mode": "sha256"
})

# TOTP Drift Simulation Test
# Note: Ensure 'user29' exists in users.json and has a TOTP secret
run_experiment("totp_drift_test", {
    "attack.type": "test_drift",
    "attack.target_user": "user29", 
    "attack.drift_seconds": 90,
    "protections.totp.enabled": True,
    "hashing.mode": "sha256"
})

print("\n=== All experiments completed ===")