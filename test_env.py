import sys

print("=== Python Interpreter Path ===")
print(sys.executable)

print("\n=== Checking installed packages ===")

packages = ["bcrypt", "argon2", "pyotp"]

for pkg in packages:
    try:
        __import__(pkg)
        print(f"[OK] {pkg} imported successfully")
    except Exception as e:
        print(f"[ERROR] {pkg} failed to import: {e}")