import subprocess

def clear_keri():
    path = "/usr/local/var/keri/"
    confirm = input("🚨 This will clear your keystore. Are you sure? (y/n): ")
    if confirm.lower() == "y":
        print("Proceeding...")
        try:
            subprocess.run(["rm", "-rf", path], check=True)
            print(f"✅ Successfully removed: {path}")
        except subprocess.CalledProcessError as e:
            print(f"❌ Error removing {path}: {e}")
    else:
        print("Operation cancelled.")