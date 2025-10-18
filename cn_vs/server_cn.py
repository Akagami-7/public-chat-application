import socket
import threading
import logging

# Server configuration
HOST = '127.0.0.1'  # Localhost
PORT = 12345        # Server port

# Dictionary to store connected clients {username: socket}
clients = {}

# Set up logging
logger = logging.getLogger()  # Get the root logger
logger.setLevel(logging.INFO)

# Create a file handler for logging to a file
file_handler = logging.FileHandler('chat_server.log')
file_handler.setLevel(logging.INFO)          

# Create a stream handler for logging to the terminal
stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.INFO)

# Set up a log format
log_format = logging.Formatter('%(asctime)s - %(message)s')
file_handler.setFormatter(log_format)
stream_handler.setFormatter(log_format)

# Add both handlers to the logger
logger.addHandler(file_handler)
logger.addHandler(stream_handler)

# Function to log messages
def log_message(message):
    logger.info(message)

# Function to handle each client
def handle_client(client_socket, username):
    while True:
        try:
            message = client_socket.recv(1024).decode()
            if not message:
                break

            log_message(f"Received message from {username}: {message}")  # Log the received message in the terminal and log file
            if message.startswith("@"):
                # Unicast message format: @username message
                parts = message.split(" ", 1)
                if len(parts) > 1:
                    target_user = parts[0][1:]  # Remove '@' and get username
                    private_message = f"[Private] {username}: {parts[1]}"
                    if target_user in clients:
                        clients[target_user].send(private_message.encode())
                        log_message(f"Private message sent from {username} to {target_user}: {parts[1]}")
                    else:
                        client_socket.send(f"User {target_user} not found.".encode())
                        log_message(f"Failed private message attempt from {username} to {target_user}: {parts[1]}")
                else:
                    client_socket.send("Invalid message format. Use @username message".encode())
                    log_message(f"Invalid message format from {username}: {message}")
            else:
                # Broadcast message
                broadcast_message = f"{username}: {message}"
                for user, sock in clients.items():
                    if user != username:  # Don't send message to sender
                        sock.send(broadcast_message.encode())
                log_message(f"Broadcast message sent from {username}: {message}")

        except Exception as e:
            print(f"Error handling client {username}: {e}")
            break

    # Remove disconnected client
    log_message(f"{username} has disconnected.")
    del clients[username]
    client_socket.close()

# Function to accept incoming connections
def accept_connections():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST, PORT))
    server_socket.listen()

    log_message(f"Server started on {HOST}:{PORT}")

    while True:
        client_socket, addr = server_socket.accept()
        client_socket.send("Enter your username: ".encode())
        username = client_socket.recv(1024).decode().strip()

        if username in clients:
            client_socket.send("Username already taken. Try again.".encode())
            client_socket.close()
            log_message(f"Attempted connection with an existing username: {username} from {addr}")
            continue

        log_message(f"{username} connected from {addr}")
        clients[username] = client_socket
        client_socket.send("Welcome to the chat! Use @username message for private messages.".encode())

        # Start a new thread to handle the client
        threading.Thread(target=handle_client, args=(client_socket, username)).start()

# Start the server
accept_connections()
