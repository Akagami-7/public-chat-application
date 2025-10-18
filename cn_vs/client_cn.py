import socket
import threading

HOST = '127.0.0.1'  # Server IP
PORT = 12345        # Server port

def receive_messages(client_socket):
    while True:
        try:
            message = client_socket.recv(1024).decode()
            if not message:
                break
            print(message)
        except:
            print("Connection closed by server.")
            break

def main():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((HOST, PORT))

    username = input("Enter your username: ")
    client_socket.send(username.encode())

    # Start a thread to receive messages
    threading.Thread(target=receive_messages, args=(client_socket,), daemon=True).start()

    while True:
        message = input()
        if message.lower() == "exit":
            break
        client_socket.send(message.encode())

    client_socket.close()

if __name__ == "__main__":
    main()
