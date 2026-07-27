import json
import pyotp
import random

users = []
for i in range(1, 31):
    username = f"user{i:02d}"  # user01, user02... user30
    
    password = f"Password{i}!" 
    
    # Give TOTP only to strong users (e.g., 21-30)
    totp_secret = pyotp.random_base32() if i > 20 else None
    
    users.append({
        "username": username,
        "password": password,
        "totp_secret": totp_secret
    })

with open("users.json", "w") as f:
    json.dump(users, f, indent=4)
print("[+] users.json created/updated with 30 users.")