import json
import time
import hashlib
import os
import bcrypt
from argon2 import PasswordHasher
import pyotp

class AuthServer:
    def __init__(self, config_file, users_file):
        # Load configuration file
        with open(config_file, "r") as f:
            self.config = json.load(f)

        # Load raw users
        with open(users_file, "r") as f:
            self.users_raw = json.load(f)

        # Hash mode and log file path
        self.hash_mode = self.config["hashing"]["mode"]
        self.log_file = self.config["logging"]["output_file"]

        # Load PEPPER from environment (empty if not set)
        self.pepper = os.environ.get("PEPPER", "")

        # Argon2 password hasher
        self.ph = PasswordHasher(
            time_cost=self.config["hashing"]["argon2id"]["time_cost"],
            memory_cost=self.config["hashing"]["argon2id"]["memory_cost"],
            parallelism=self.config["hashing"]["argon2id"]["parallelism"]
        )

        # Internal user database
        self.db = {}
        self._initialize_users()
        
        # --- FIX: Ensure TOTP config is fully populated with defaults ---
        if "totp" not in self.config["protections"]:
            self.config["protections"]["totp"] = {}

        # Default values for TOTP if missing from config
        totp_defaults = {
            "enabled": False,
            "window": 1,
            "max_attempts_per_window": 5,  # Added default
            "max_failures": 3,
            "lockout_minutes": 10
        }
        
        # Merge defaults into existing config
        for key, val in totp_defaults.items():
            if key not in self.config["protections"]["totp"]:
                self.config["protections"]["totp"][key] = val

    def _initialize_users(self):
        for user in self.users_raw:
            username = user["username"]
            password = user["password"]
            totp_secret = user["totp_secret"]

            salt = os.urandom(16).hex()
            hashed = self.hash_password(password, salt)

            self.db[username] = {
                "salt": salt,
                "hash": hashed,
                "totp_secret": totp_secret,
                "totp_offset": 0,
                "failed_attempts": 0,
                "locked_until": 0,
                "recent_attempts": [],
                "captcha_required": False,
                "captcha_token": None,
                "totp_failed_attempts": 0,
                "totp_locked_until": 0,
            }

    def register(self, username, password):
        if username in self.db:
            return False, "user_already_exists"
        salt = os.urandom(16).hex()
        hashed = self.hash_password(password, salt)
        self.db[username] = {
            "salt": salt,
            "hash": hashed,
            "totp_secret": None,
            "totp_offset": 0,
            "failed_attempts": 0,
            "locked_until": 0,
            "recent_attempts": [],
            "captcha_required": False,
            "captcha_token": None,
            "totp_failed_attempts": 0,
            "totp_locked_until": 0,
        }
        self.log_attempt(username, "success", "user_registered")
        return True, "user_registered"

    def hash_password(self, password, salt):
        mode = self.hash_mode
        password_peppered = password + self.pepper
        if mode == "argon2id":
            return self.ph.hash(password_peppered + salt)
        elif mode == "bcrypt":
            salted = (password_peppered + salt).encode("utf-8")
            return bcrypt.hashpw(salted, bcrypt.gensalt()).decode("utf-8")
        elif mode == "sha256":
            return hashlib.sha256((password_peppered + salt).encode("utf-8")).hexdigest()
        else:
            raise ValueError(f"Unknown hashing mode: {mode}")

    def verify_password(self, password, salt, stored_hash):
        mode = self.hash_mode
        password_peppered = password + self.pepper
        if mode == "argon2id":
            try: return self.ph.verify(stored_hash, password_peppered + salt)
            except Exception: return False
        elif mode == "bcrypt":
            salted = (password_peppered + salt).encode("utf-8")
            try: return bcrypt.checkpw(salted, stored_hash.encode("utf-8"))
            except Exception: return False
        elif mode == "sha256":
            return stored_hash == hashlib.sha256((password_peppered + salt).encode("utf-8")).hexdigest()
        else:
            raise ValueError(f"Unknown hashing mode: {mode}")
        
    def check_rate_limit(self, username):
        rate_cfg = self.config["protections"]["rate_limit"]
        if not rate_cfg["enabled"]: return True

        user = self.db[username]
        now = time.time()
        one_sec_ago = now - 1
        user["recent_attempts"] = [t for t in user["recent_attempts"] if t > one_sec_ago]

        max_per_sec = 1#
        if len(user["recent_attempts"]) >= max_per_sec: return False
        user["recent_attempts"].append(now)
        return True

    def check_lockout(self, username):
        if not self.config["protections"]["lockout"]["enabled"]: return True
        threshold = self.config["protections"]["lockout"]["threshold"]
        lockout_seconds = self.config["protections"]["lockout"]["lockout_seconds"]
        user = self.db[username]
        now = time.time()
        if user["failed_attempts"] >= threshold:
            user["locked_until"] = now + lockout_seconds
        return user["locked_until"] <= now

    def check_captcha(self, username):
        if not self.config["protections"]["captcha"]["enabled"]: return True
        user = self.db[username]
        if user["captcha_required"]: return False
        threshold = self.config["protections"]["captcha"]["trigger_after_failures"]
        if user["failed_attempts"] >= threshold:
            user["captcha_required"] = True
            return False
        return True

    def check_totp_rate_limit(self, username):
        if not self.config["protections"]["totp"]["enabled"]: return True
        user = self.db[username]
        now = time.time()
        if "totp_attempt_window" not in user:
            user["totp_attempt_window"] = now
            user["totp_attempts"] = 0
        if now - user["totp_attempt_window"] > 30:
            user["totp_attempt_window"] = now
            user["totp_attempts"] = 0
        user["totp_attempts"] += 1
        return user["totp_attempts"] <= self.config["protections"]["totp"]["max_attempts_per_window"]

    def check_totp_lockout(self, username):
        if not self.config["protections"]["totp"]["enabled"]: return True
        user = self.db[username]
        now = time.time()
        return user["totp_locked_until"] <= now

    def admin_get_captcha_token(self, group_seed):
        if group_seed != self.config["group_seed"]: return None
        return os.urandom(8).hex()

    # Login function with proper indentation
    def login(self, username, password, captcha_token=None):
        start_time = time.time()  # Start measuring time (Latency)

        if username not in self.db:
            latency = (time.time() - start_time) * 1000
            self.log_attempt(username, "fail", "user_not_found", latency_ms=latency)
            return False, "user_not_found"

        user = self.db[username]
        
        # Check Lockout
        if not self.check_lockout(username):
            latency = (time.time() - start_time) * 1000
            self.log_attempt(username, "fail", "account_locked", latency_ms=latency)
            return False, "account_locked"
        
        # Check Rate Limit
        if not self.check_rate_limit(username):
            latency = (time.time() - start_time) * 1000
            self.log_attempt(username, "fail", "rate_limited", latency_ms=latency)
            time.sleep(1) #
            return False, "rate_limited"
            
        # Check CAPTCHA
        if not self.check_captcha(username):
            if captcha_token is None or captcha_token != user["captcha_token"]:
                latency = (time.time() - start_time) * 1000
                self.log_attempt(username, "fail", "captcha_required", latency_ms=latency)
                return False, "captcha_required"
            else:
                # Valid token provided, clear the requirement
                user["captcha_required"] = False
                user["captcha_token"] = None

        # Verify Password (The computationally expensive part for Argon2/Bcrypt)
        if self.verify_password(password, user["salt"], user["hash"]):
            user["failed_attempts"] = 0
            latency = (time.time() - start_time) * 1000  # Final calculation for success
            self.log_attempt(username, "success", "password_ok", latency_ms=latency)
            return True, "password_ok"

        # --- Handle Wrong Password ---
        user["failed_attempts"] += 1
        
        # Check if CAPTCHA needs to be triggered from now on
        captcha_threshold = self.config["protections"]["captcha"]["trigger_after_failures"]
        if user["failed_attempts"] >= captcha_threshold:
            user["captcha_required"] = True
            user["captcha_token"] = None
            latency = (time.time() - start_time) * 1000
            self.log_attempt(username, "fail", "captcha_triggered", latency_ms=latency)
            return False, "captcha_required"

        # Check if account needs to be locked
        lock_threshold = self.config["protections"]["lockout"]["threshold"]
        if user["failed_attempts"] >= lock_threshold:
            lock_seconds = self.config["protections"]["lockout"]["lockout_seconds"]
            user["locked_until"] = time.time() + lock_seconds
            latency = (time.time() - start_time) * 1000
            self.log_attempt(username, "fail", "account_locked_now", latency_ms=latency)
            return False, "account_locked"

        # Standard wrong password failure
        latency = (time.time() - start_time) * 1000
        self.log_attempt(username, "fail", "wrong_password", latency_ms=latency)
        return False, "wrong_password"

    def synchronize_totp(self, username, totp_code):
        if username not in self.db:
            return False, "user_not_found", 0
        user = self.db[username]
        secret = user["totp_secret"]
        if not secret: return False, "totp_not_enabled", 0
        totp = pyotp.TOTP(secret)
        now = time.time()
        for drift in range(-300, 301, 30):
            if totp.verify(totp_code, for_time=now + drift, valid_window=0):
                user["totp_offset"] = drift
                self.log_attempt(username, "success", f"totp_synced_drift_{drift}")
                return True, "synced", drift
        self.log_attempt(username, "fail", "totp_sync_failed")
        return False, "sync_failed", 0

    def login_totp(self, username, totp_code):
        if username not in self.db:
            self.log_attempt(username, "fail", "user_not_found_totp")
            return False, "user_not_found"
        user = self.db[username]
        secret = user["totp_secret"]
        if secret is None:
            self.log_attempt(username, "fail", "totp_not_enabled")
            return False, "totp_not_enabled"
        
        if not self.check_totp_lockout(username):
            self.log_attempt(username, "fail", "totp_locked")
            return False, "totp_locked"
        if not self.check_totp_rate_limit(username):
            self.log_attempt(username, "fail", "totp_rate_limited")
            return False, "totp_rate_limited"
        
        totp = pyotp.TOTP(secret)
        window = self.config["protections"]["totp"]["window"]
        offset = user.get("totp_offset", 0)
        verify_time = time.time() + offset
        
        if totp.verify(totp_code, for_time=verify_time, valid_window=window):
            user["totp_failed_attempts"] = 0
            self.log_attempt(username, "success", f"totp_ok_offset={offset}")
            return True, "totp_ok"
        
        user["totp_failed_attempts"] += 1
        if user["totp_failed_attempts"] >= self.config["protections"]["totp"]["max_failures"]:
            lock_minutes = self.config["protections"]["totp"]["lockout_minutes"]
            user["totp_locked_until"] = time.time() + lock_minutes * 60
            self.log_attempt(username, "fail", "totp_locked_now")
            return False, "totp_locked"
        
        self.log_attempt(username, "fail", "totp_wrong")
        return False, "totp_wrong"

    # --- פונקציית הלוגים המתוקנת (עם הזחה נכונה) ---
    def log_attempt(self, username, result, reason, latency_ms=0):
        user = self.db.get(username, {})
        entry = {
            "timestamp": time.time(),
            "group_seed": self.config["group_seed"],
            "username": username,
            "hash_mode": self.hash_mode,
            "result": result,
            "reason": reason,
            "latency_ms": latency_ms,  
            "failed_attempts": user.get("failed_attempts"),
            "captcha_required": user.get("captcha_required"),
            "locked_until": user.get("locked_until"),
            "rate_limit_enabled": self.config["protections"]["rate_limit"]["enabled"],
            "account_lockout_enabled": self.config["protections"]["lockout"]["enabled"],
            "captcha_enabled": self.config["protections"]["captcha"]["enabled"],
            "totp_enabled_user": user.get("totp_secret") is not None,
            "totp_failed_attempts": user.get("totp_failed_attempts"),
            "totp_locked_until": user.get("totp_locked_until"),
            "totp_enabled_global": self.config["protections"]["totp"]["enabled"],
        }
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")