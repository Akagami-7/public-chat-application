import os
import signal
from flask import Flask, render_template, request
from flask_socketio import SocketIO, send, emit, disconnect

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

users = {}  # Store connected users
server_active = True  # Flag to control server status

@app.route("/")
def home():
    return render_template("index.html")

@socketio.on("connect")
def handle_connect():
    # Emit the current server status when a client connects
    if server_active:
        emit("server_status", {"active": True})
        # Emit the current user count on connect
        emit("user_count", len(users), broadcast=True)  # Send connected users count to the client
    else:
        emit("server_status", {"active": False})
        disconnect()  # Disconnect if the server is not active

@socketio.on("join")
def handle_join(data):
    global users
    username = data["username"]
    sid = request.sid  # Get the unique session ID for the user

    # Check if the username already exists (either in users or if it's a duplicate)
    if username in users.values():
        # Send error message back to the client if the username is taken
        emit('username_error', 'This username is already taken. Please choose another one.', to=sid)
        return  # Don't add the user to the chat if the username is taken

    # If username is available, add user
    users[sid] = username  # Store user with their session ID
    emit("user_list", list(users.values()), broadcast=True)
    send(f"{username} joined the chat.", broadcast=True)
    # Emit the updated user count
    emit("user_count", len(users), broadcast=True)

@socketio.on("message")
def handle_message(data):
    global users
    sid = request.sid  # Get sender's session ID
    username = users.get(sid, "Unknown")
    message = data['message']

    if message.startswith('@'):
        target_user = message.split(' ')[0][1:]
        private_message = f"[Private] {username}: {' '.join(message.split(' ')[1:])}"

        # Find the target user
        target_sid = None
        for user_sid, user_name in users.items():
            if user_name == target_user:
                target_sid = user_sid
                break

        if target_sid:
            # Send the private message to both the sender and receiver
            emit('private_message', {'message': private_message, 'is_private': True, 'from': username}, to=target_sid)
            emit('private_message', {'message': private_message, 'is_private': True, 'from': username}, to=sid)
        else:
            emit('message', "User not found.", to=sid)
    else:
        send(f"{username}: {message}", broadcast=True)

@socketio.on("disconnect")
def handle_disconnect():
    global users
    sid = request.sid  # Get user's session ID
    username = users.pop(sid, None)

    if username:
        send(f"{username} left the chat.", broadcast=True)
        # Send updated user list to all clients
        emit("user_list", list(users.values()), broadcast=True)
        # Update connected users count by emitting the new count
        emit("user_count", len(users), broadcast=True)  # Update count when a user disconnects

@socketio.on("server_toggle")
def toggle_server(data):
    global server_active
    server_active = data["active"]
    emit("server_status", {"active": server_active}, broadcast=True)

def on_shutdown(signal, frame):
    global server_active
    server_active = False
    print("Server is shutting down...")  # Optionally log shutdown
    # Emit the server status as "offline" to all clients
    socketio.emit("server_status", {"active": False}, broadcast=True)
    # Gracefully shut down the server
    socketio.stop()

if __name__ == "__main__":
    # Register shutdown signal (Ctrl+C or kill)
    signal.signal(signal.SIGINT, on_shutdown)

    print("Server is running...")  # Optional print statement
    # Start the SocketIO server
    socketio.run(app, host="0.0.0.0", port=5000, debug=True)
