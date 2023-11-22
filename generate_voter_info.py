import hashlib
from cryptography.fernet import Fernet


def encrypt_password(password_hash, key):
    cipher = Fernet(key)
    encrypted_password = cipher.encrypt(password_hash)
    return encrypted_password.decode()


def main():
    voters = [
        {"name": "Alice", "voter_id": "1123456", "password": "1234"},
        {"name": "Bob", "voter_id": "1138765", "password": "5678"},
        {"name": "Tom", "voter_id": "1154571", "password": "9012"},
    ]

    key = Fernet.generate_key()
    with open("key", "wb") as key_file:
        key_file.write(key)

    with open("voterinfo", "w") as voterinfo_file:
        for voter in voters:
            password_hash = hashlib.md5(voter["password"].encode("utf-8")).digest()
            encrypted_password = encrypt_password(password_hash, key)
            voterinfo_file.write(
                f'{voter["name"]},{voter["voter_id"]},{encrypted_password}\n'
            )


if __name__ == "__main__":
    main()
