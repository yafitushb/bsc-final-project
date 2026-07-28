# Script to generate a common password list for the Spraying attack simulation
passwords = [
    "123456",
    "password",
    "12345678",
    "qwerty",
    "123456789",
    "welcome1",
    "Password123!",
    "admin",
    "login",
    "football",
    "dragon"
]

filename = "common_passwords.txt"

with open(filename, "w") as f:
    for pwd in passwords:
        f.write(pwd + "\n")

print(f"[+] Successfully created '{filename}' with {len(passwords)} entries.")