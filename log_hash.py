import bcrypt
from pathlib import Path

USERS_FILE = Path("user.txt")


def hash_password(password: str) -> str:
    """Return a bcrypt hash for the given plaintext password."""
    password_bytes = password.encode("utf-8")
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode("utf-8")


def verify_password(password: str, hashed_password: str) -> bool:
    """Check whether the plaintext password matches the stored bcrypt hash."""
    password_bytes = password.encode("utf-8")
    hash_bytes = hashed_password.encode("utf-8")
    return bcrypt.checkpw(password_bytes, hash_bytes)


def save_user(username: str, password: str) -> None:
    """
    Append a new user to user.txt in the format:
        username,hashed_password
    """
    hashed = hash_password(password)
    with USERS_FILE.open("a", encoding="utf-8") as f:
        f.write(f"{username},{hashed}\n")


def check_user(username: str, password: str) -> bool:
    """
    Return True if the username exists in user.txt and the password is correct.
    """
    if not USERS_FILE.exists():
        return False

    with USERS_FILE.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue

            # Safely split into username and hash
            try:
                stored_username, stored_hash = line.split(",", 1)
            except ValueError:
                # Malformed line, skip it
                continue

            if stored_username == username:
                return verify_password(password, stored_hash)

    return False


if __name__ == "__main__":
    # Optional manual test in the terminal
    name = input("Enter username: ")
    pwd = input("Enter password: ")
    save_user(name, pwd)
    print("User saved. Try logging in...")
    pwd_login = input("Enter password again: ")
    print("Login OK?", check_user(name, pwd_login))
