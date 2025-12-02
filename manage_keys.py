import os
import json
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import getpass
import sys

# Files to encrypt/decrypt
FILES_TO_PROCESS = ['credentials.json', '.env']
ENCRYPTED_FILE = 'secrets.enc'

def get_key(password: str, salt: bytes) -> bytes:
    """Derives a key from the password using a salt."""
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=480000,
    )
    return base64.urlsafe_b64encode(kdf.derive(password.encode()))

def encrypt_files():
    password = getpass.getpass("Enter a password to encrypt the files: ")
    confirm_password = getpass.getpass("Confirm password: ")
    
    if password != confirm_password:
        print("Passwords do not match!")
        return

    # Generate a random salt
    salt = os.urandom(16)
    key = get_key(password, salt)
    f = Fernet(key)

    data_to_encrypt = {}
    for filename in FILES_TO_PROCESS:
        if os.path.exists(filename):
            with open(filename, 'r') as file:
                data_to_encrypt[filename] = file.read()
            print(f"Added {filename} to encryption package.")
        else:
            print(f"Warning: {filename} not found, skipping.")

    if not data_to_encrypt:
        print("No files found to encrypt.")
        return

    json_data = json.dumps(data_to_encrypt).encode()
    encrypted_data = f.encrypt(json_data)

    # Store salt + encrypted data
    with open(ENCRYPTED_FILE, 'wb') as file:
        file.write(salt + encrypted_data)
    
    print(f"Successfully created {ENCRYPTED_FILE}.")
    print("You can now commit this file. DO NOT commit the original json/.env files.")

def decrypt_files():
    if not os.path.exists(ENCRYPTED_FILE):
        print(f"Error: {ENCRYPTED_FILE} not found.")
        return

    password = getpass.getpass("Enter the password to decrypt the files: ")

    with open(ENCRYPTED_FILE, 'rb') as file:
        file_content = file.read()
    
    # Extract salt (first 16 bytes) and encrypted data
    salt = file_content[:16]
    encrypted_data = file_content[16:]

    try:
        key = get_key(password, salt)
        f = Fernet(key)
        decrypted_data = f.decrypt(encrypted_data)
        
        files_data = json.loads(decrypted_data.decode())
        
        for filename, content in files_data.items():
            with open(filename, 'w') as file:
                file.write(content)
            print(f"Restored {filename}.")
            
        print("Decryption successful!")
        
    except Exception as e:
        print("Failed to decrypt. Wrong password or corrupted file.")
        # print(e) # Uncomment for debug

def main():
    if len(sys.argv) < 2:
        print("Usage: python manage_keys.py [encrypt|decrypt]")
        return

    action = sys.argv[1]
    if action == 'encrypt':
        encrypt_files()
    elif action == 'decrypt':
        decrypt_files()
    else:
        print("Invalid action. Use 'encrypt' or 'decrypt'.")

if __name__ == "__main__":
    main()
