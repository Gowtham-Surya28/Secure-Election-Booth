import socket
import sys


def main_menu(name):
    print(f"Welcome {name}!")
    print("Please enter a number (1-4)")
    print("1. Vote")
    print("2. View election result")
    print("3. My vote history")
    print("4. Exit")


def main():
    if len(sys.argv) != 3:
        print("Usage: cli.py <server's domain name> <server’s port number>")
        sys.exit(1)

    server_domain = sys.argv[1]
    server_port = int(sys.argv[2])

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
        client.connect((server_domain, server_port))

        name = input("Enter your name: ")
        voter_id = input("Enter your voter registration number: ")
        password = input("Enter your password: ")

        client.sendall(f"{name},{voter_id},{password}".encode())

        response = client.recv(1024).decode()

        if response == "1":
            print("Successfully logged in.")

            while True:
                main_menu(name)
                option = input("Enter your choice: ").strip()
                client.sendall(option.encode())

                if option == "1":
                    response = client.recv(1024).decode()
                    if response == "1":
                        print("Candidates: (enter 1 or 2)")
                        print("1. Chris")
                        print("2. Linda")
                        candidate = input().strip()
                        client.sendall(candidate.encode())
                        print("Your vote has been recorded.")
                    else:
                        print("You have already voted.")
                elif option == "2":
                    response = client.recv(1024).decode()
                    if response.startswith("1"):  # Change this line
                        chris_votes, linda_votes = map(int, response.split(",")[1:])
                        if chris_votes > linda_votes:
                            winner = "Chris"
                        elif linda_votes > chris_votes:
                            winner = "Linda"
                        else:
                            winner = "Tie"
                        print(f"{winner} wins")
                        print(f"Chris {chris_votes}")
                        print(f"Linda {linda_votes}")
                    else:
                        print("The result is not available")

                elif option == "3":
                    vote_time = client.recv(1024).decode()
                    if vote_time == "No vote history":
                        print("You have not voted yet.")
                    else:
                        print("You voted on", vote_time)

                elif option == "4":
                    break
        elif response == "0":
            print("Invalid name, registration number, or password")


if __name__ == "__main__":
    main()
