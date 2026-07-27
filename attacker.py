import json
import time
import os
import argparse
import pyotp
from auth_server import AuthServer

class Attacker:
    def __init__(self, config_file, users_file, wordlist_file):
        # Load configuration
        with open(config_file, "r") as f:
            self.config = json.load(f)

        # Load users list
        with open(users_file, "r") as f:
            self.users = json.load(f)

        # Load wordlist
        with open(wordlist_file, "r", encoding="utf-8", errors="ignore") as f:
            self.wordlist = [line.strip() for line in f.readlines()]

        # Create server instance
        self.server = AuthServer(config_file, users_file)

        # Experiment settings
        self.max_attempts = self.config["experiment"]["max_attempts"]
        self.group_seed = self.config["group_seed"]
        self.experiment_name = self.config["experiment"]["name"]

        # Ensure logs folder exists
        os.makedirs("logs", exist_ok=True)

        # Log file for this experiment
        self.log_file = f"logs/attempts_{self.experiment_name}.log"

    #  Logging helper now accepts latency 
    def log_attempt(self, username, password_or_code, success, reason, latency_ms=0.0):
        entry = {
            "timestamp": time.time(),
            "username": username,
            "password": password_or_code,
            "result": "success" if success else "fail",
            "reason": reason,
            "hash_mode": self.config["hashing"]["mode"],
            "experiment": self.experiment_name,
            "latency_ms": latency_ms  
        }
        with open(self.log_file, "a") as f:
            f.write(json.dumps(entry) + "\n")

    # Helper for High-Precision Timing 
    def measure_login(self, func, *args, **kwargs):
        """
        Runs a login function and measures execution time with high precision.
        Returns: ((success, reason), latency_ms)
        """
        start_time = time.perf_counter() # Precise timer
        result = func(*args, **kwargs)
        end_time = time.perf_counter()
        
        latency_ms = (end_time - start_time) * 1000
        
        # Safety: Prevent absolute 0.0 which crashes log-scale graphs
        if latency_ms == 0: 
            latency_ms = 0.001
        
        return result, latency_ms

    # Brute-Force (Password Only)
    def brute_force(self, username):
        print(f"\n[Brute-Force] Attacking user: {username}")

        attempts = 0
        
        for password in self.wordlist:
            if attempts >= self.max_attempts:
                break

            # Measure Latency
            (success, reason), latency = self.measure_login(self.server.login, username, password)
            attempts += 1

            self.log_attempt(username, password, success, reason, latency)

            if reason == "captcha_required":
                print("[!] CAPTCHA triggered — stopping attack (no token)")
                return False

            if success:
                print(f"[+] Password found for {username}: {password}")
                return True

        print(f"[-] Password NOT found for {username}")
        return False


    # Brute-Force with CAPTCHA Support
    def brute_force_with_captcha(self, username):
        print(f"\n[Brute-Force + CAPTCHA] Attacking user: {username}")

        attempts = 0

        for password in self.wordlist:
            if attempts >= self.max_attempts:
                break

            # Measure Latency
            (success, reason), latency = self.measure_login(self.server.login, username, password)
            attempts += 1

            self.log_attempt(username, password, success, reason, latency)

            if reason == "captcha_required":
                token = self.server.admin_get_captcha_token(self.group_seed)
                # Retry with token and measure again
                (success, reason), latency = self.measure_login(self.server.login, username, password, captcha_token=token)
                self.log_attempt(username, password, success, reason, latency)

            if success:
                print(f"[+] Password found for {username}: {password}")
                return True

        print(f"[-] Password NOT found for {username}")
        return False

    # Password-Spraying
    def password_spraying(self, common_passwords):
        print("\n[Password-Spraying] Starting attack...")

        for pwd in common_passwords:
            for user in self.users:
                username = user["username"]
                
                # Measure Latency
                (success, reason), latency = self.measure_login(self.server.login, username, pwd)

                self.log_attempt(username, pwd, success, reason, latency)

                if success:
                    print(f"[+] SUCCESS: {username} -> {pwd}")


    # Password-Spraying with CAPTCHA
    def password_spraying_with_captcha(self, common_passwords):
        print("\n[Password-Spraying + CAPTCHA] Starting attack...")

        for pwd in common_passwords:
            for user in self.users:
                username = user["username"]
                
                # Measure Latency
                (success, reason), latency = self.measure_login(self.server.login, username, pwd)
                self.log_attempt(username, pwd, success, reason, latency)

                if reason == "captcha_required":
                    token = self.server.admin_get_captcha_token(self.group_seed)
                    # Retry
                    (success, reason), latency = self.measure_login(self.server.login, username, pwd, captcha_token=token)
                    self.log_attempt(username, pwd, success, reason, latency)

                if success:
                    print(f"[+] SUCCESS: {username} -> {pwd}")


    # TOTP Attack
    def totp_attack(self, username, totp_codes):
        print(f"\n[TOTP Attack] Attacking TOTP for user: {username}")

        for code in totp_codes:
            # Measure Latency for TOTP login
            (success, reason), latency = self.measure_login(self.server.login_totp, username, code)

            self.log_attempt(username, code, success, reason, latency)

            if success:
                print(f"[+] VALID TOTP code found for {username}: {code}")
                return True

            if reason in ("totp_locked", "totp_rate_limited"):
                print(f"[!] TOTP protection triggered: {reason}")
                return False

        print(f"[-] No valid TOTP code found for {username}")
        return False


    # Password + TOTP (Full MFA)
    def full_mfa_attack(self, username, totp_codes):
        print(f"\n[Full MFA Attack] Starting MFA attack on {username}")

        print("[*] Step 1: Password brute-force...")
        # Note: Brute force function already handles logging and timing internally
        password_found = self.brute_force_with_captcha(username)

        if not password_found:
            print("[-] Password not found — cannot continue to TOTP stage.")
            return False

        print("[*] Step 2: TOTP brute-force...")
        return self.totp_attack(username, totp_codes)

    # Test Registration Endpoint 
    def test_registration(self):
        print("\n[Registration Test] Creating a new user 'new_attacker'...")
        
        # Measure Registration
        (success, reason), latency = self.measure_login(self.server.register, "new_attacker", "Password123!")
        
        self.log_attempt("new_attacker", "REGISTER", success, reason, latency)

        if success:
            print(f"[+] Registration successful: {reason}")
            # Try to login with the new user
            (success_login, reason_login), latency_login = self.measure_login(self.server.login, "new_attacker", "Password123!")
            self.log_attempt("new_attacker", "LOGIN_AFTER_REG", success_login, reason_login, latency_login)
            
            if success_login:
                print(f"[+] Login with new user successful!")
            else:
                print(f"[-] Login failed: {reason_login}")
        else:
            print(f"[-] Registration failed: {reason}")

    # Test TOTP Time Drift 
    def test_totp_drift(self, username, drift_seconds):
        print(f"\n[TOTP Drift Test] Simulating clock drift of {drift_seconds} seconds for {username}...")
        
        user_data = next((u for u in self.users if u["username"] == username), None)
        if not user_data:
             if username in self.server.db:
                secret = self.server.db[username]["totp_secret"]
             else:
                print("[-] User not found.")
                return
        else:
            secret = user_data.get("totp_secret")

        if not secret:
            print("[-] User has no TOTP secret for simulation.")
            return

        totp = pyotp.TOTP(secret)
        drifted_time = time.time() + float(drift_seconds)
        drifted_code = totp.at(drifted_time)
        
        print(f"[*] Generated code {drifted_code} for time {drifted_time}")
        
        # 1. Normal login attempt
        print("[*] Attempting normal login_totp (Expected: Fail)...")
        (success, reason), latency = self.measure_login(self.server.login_totp, username, drifted_code)
        self.log_attempt(username, f"DRIFT_LOGIN_{drift_seconds}", success, reason, latency)
        
        if not success:
            print(f"[+] Normal login failed as expected: {reason}")
        else:
            print(f"[-] Unexpected success in normal login!")

        # 2. Sync attempt
        print("[*] Attempting TOTP Synchronization...")
        # Special handling for sync because it returns 3 values
        start = time.perf_counter()
        success, reason, detected_drift = self.server.synchronize_totp(username, drifted_code)
        end = time.perf_counter()
        latency = (end - start) * 1000
        if latency == 0: latency = 0.001

        self.log_attempt(username, f"SYNC_ATTEMPT_{drift_seconds}", success, reason, latency)
        
        if success:
            print(f"[+] Sync Successful! Server detected drift: {detected_drift} seconds.")
            
            # 3. Retry login
            print("[*] Retrying normal login_totp after sync (Expected: Success)...")
            (success_retry, reason_retry), latency_retry = self.measure_login(self.server.login_totp, username, drifted_code)
            self.log_attempt(username, f"LOGIN_AFTER_SYNC_{drift_seconds}", success_retry, reason_retry, latency_retry)
            
            if success_retry:
                print(f"[+] Login successful after sync!")
            else:
                print(f"[-] Login failed even after sync: {reason_retry}")
        else:
            print(f"[-] Sync Failed: {reason}")


# Main entry point
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True, help="Path to config file")
    args = parser.parse_args()

    with open(args.config, "r") as f:
        cfg = json.load(f)

    attacker = Attacker(
        config_file=args.config,
        users_file=cfg["users"]["file"],
        wordlist_file=cfg["attack"]["password_list"]
    )

    attack_type = cfg["attack"]["type"]

    if attack_type == "bruteforce":
        attacker.brute_force(cfg["attack"]["target_user"])

    elif attack_type == "bruteforce_captcha":
        attacker.brute_force_with_captcha(cfg["attack"]["target_user"])

    elif attack_type == "spraying":
        with open(cfg["attack"]["spraying_user_file"], "r") as f:
            pwds = [line.strip() for line in f.readlines()]
        attacker.password_spraying(pwds)

    elif attack_type == "spraying_captcha":
        with open(cfg["attack"]["spraying_user_file"], "r") as f:
            pwds = [line.strip() for line in f.readlines()]
        attacker.password_spraying_with_captcha(pwds)

    elif attack_type == "totp":
        totp_codes = [f"{i:06d}" for i in range(1000000)]
        attacker.totp_attack(cfg["attack"]["target_user"], totp_codes)

    elif attack_type == "mfa":
        totp_codes = [f"{i:06d}" for i in range(1000000)]
        attacker.full_mfa_attack(cfg["attack"]["target_user"], totp_codes)

    elif attack_type == "test_register":
        attacker.test_registration()

    elif attack_type == "test_drift":
        target = cfg["attack"].get("target_user", "user29")
        drift = cfg["attack"].get("drift_seconds", 90)
        attacker.test_totp_drift(target, drift)

    else:
        print(f"Unknown attack type: {attack_type}")