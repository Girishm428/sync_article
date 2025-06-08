from cryptography.fernet import Fernet
import os

# You can store this in a secure location or environment variable
SECRET_KEY_FILE = os.path.join(os.path.dirname(__file__), "../../.secret_key")

def load_or_create_key():
    if not os.path.exists(SECRET_KEY_FILE):
        key = Fernet.generate_key()
        with open(SECRET_KEY_FILE, "wb") as f:
            f.write(key)
    else:
        with open(SECRET_KEY_FILE, "rb") as f:
            key = f.read()
    return key

fernet = Fernet(load_or_create_key())

def encrypt(text: str) -> str:
    return fernet.encrypt(text.encode()).decode()

def decrypt(token: str) -> str:
    return fernet.decrypt(token.encode()).decode()
