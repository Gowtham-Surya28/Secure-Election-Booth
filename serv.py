import socket
import sys
from cryptography.fernet import Fernet
import hashlib
import datetime
import os


def save_vote_history(history):
    with open("history", "w") as history_file:
        for name, timestamp in history.items():
            history_file.write(f"{name},{timestamp}\n")


def save_results(results):
    with open("result", "w") as result_file:
        result_file.write(f"Chris {results['Chris']}\n")
        result_file.write(f"Linda {results['Linda']}\n")


def load_voterinfo():
    voterinfo = {}
    with open("voterinfo", "r") as voterinfo_file:
        for line in voterinfo_file:
            name, voter_id, password = line.strip().split(",")
            voterinfo[name] = {"voter_id": voter_id, "password": password}
    return voterinfo


def validate_password(name, client_password, voterinfo, key):
    client_password_hash = hashlib.md5(client_password.encode("utf-8")).digest()
    stored_encrypted_password = voterinfo[name]["password"].encode()
    decrypted_stored_password_hash = decrypt_password(stored_encrypted_password, key)
    return client_password_hash == decrypted_stored_password_hash


def decrypt_password(encrypted_password, key):
    cipher = Fernet(key)
    decrypted_password = cipher.decrypt(encrypted_password)
    return decrypted_password


def encrypt_password(password_hash, key):
    cipher = Fernet(key)
    encrypted_password = cipher.encrypt(password_hash)
    return encrypted_password.decode()


def main():
    if len(sys.argv) != 2:
        print("Usage: serv.py <server’s port number>")
        sys.exit(1)

    server_port = int(sys.argv[1])

    with open("key", "rb") as key_file:
        key = key_file.read()

    voterinfo = load_voterinfo()

    results = {"Chris": 0, "Linda": 0}
    history = {}

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.bind(("", server_port))
        server.listen()

        print(f"Server is running on port {server_port}")

        if os.path.exists("history"):
            with open("history", "r") as history_file:
                for line in history_file:
                    name, timestamp = line.strip().split(",")
                    history[name] = timestamp

        if os.path.exists("result"):
            with open("result", "r") as result_file:
                for line in result_file:
                    candidate, votes = line.strip().split()
                    results[candidate] = int(votes)

        while True:
            conn, addr = server.accept()
            with conn:
                data = conn.recv(1024).decode().strip().split(",")

                if len(data) == 3:
                    name, voter_id, password = data

                    if (
                        name in voterinfo
                        and voter_id == voterinfo[name]["voter_id"]
                        and validate_password(name, password, voterinfo, key)
                    ):
                        print(f"Connected by {addr}")
                        conn.sendall(b"1")

                        while True:
                            option = conn.recv(1024).decode().strip()
                            if option == "1":
                                if name in history:
                                    conn.sendall(b"0")
                                else:
                                    conn.sendall(b"1")
                                    candidate = conn.recv(1024).decode().strip()
                                    if candidate == "1":
                                        results["Chris"] += 1
                                    elif candidate == "2":
                                        results["Linda"] += 1
                                    history[name] = str(datetime.datetime.now())

                                    save_vote_history(history)
                                    save_results(results)

                            elif option == "2":
                                if len(history) == len(voterinfo):
                                    conn.sendall(
                                        f"1,{results['Chris']},{results['Linda']}".encode()
                                    )
                                else:
                                    conn.sendall(b"0")

                            elif option == "3":
                                if name in history:
                                    conn.sendall(history[name].encode())
                                else:
                                    conn.sendall(b"No vote history")

                            elif option == "4":
                                break

                    else:
                        conn.sendall(b"0")


if __name__ == "__main__":
    main()
