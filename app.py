import os
import signal
from flask import Flask, render_template, request
from flask_socketio import SocketIO, send, emit, disconnect

app = Flask(__name__)

socketio = SocketIO(app, cors_allowed_origins="*", async_mode="eventlet")

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
        emit("user_count", len(users), broadcast=True)
    else:
        emit("server_status", {"active": False})
        disconnect()  # Disconnect if the server is not active

@socketio.on("join")
def handle_join(data):
    global users
    username = data["username"]
    sid = request.sid  # Get the unique session ID for the user

    # Check if the username already exists
    if username in users.values():
        emit(
            'username_error',
            'This username is already taken. Please choose another one.',
            to=sid
        )
        return

    # Add user
    users[sid] = username

    emit("user_list", list(users.values()), broadcast=True)
    send(f"{username} joined the chat.", broadcast=True)
    emit("user_count", len(users), broadcast=True)

@socketio.on("message")
def handle_message(data):
    sid = request.sid
    username = users.get(sid, "Unknown")
    message = data['message']

    # Private message
    if message.startswith('@'):
        target_user = message.split(' ')[0][1:]
        private_message = f"[Private] {username}: {' '.join(message.split(' ')[1:])}"

        target_sid = None
        for user_sid, user_name in users.items():
            if user_name == target_user:
                target_sid = user_sid
                break

        if target_sid:
            emit(
                'private_message',
                {'message': private_message, 'is_private': True, 'from': username},
                to=target_sid
            )
            emit(
                'private_message',
                {'message': private_message, 'is_private': True, 'from': username},
                to=sid
            )
        else:
            emit('message', "User not found.", to=sid)

    else:
        send(f"{username}: {message}", broadcast=True)

@socketio.on("disconnect")
def handle_disconnect():
    global users
    sid = request.sid
    username = users.pop(sid, None)

    if username:
        send(f"{username} left the chat.", broadcast=True)
        emit("user_list", list(users.values()), broadcast=True)
        emit("user_count", len(users), broadcast=True)

@socketio.on("server_toggle")
def toggle_server(data):
    global server_active
    server_active = data["active"]
    emit("server_status", {"active": server_active}, broadcast=True)

def on_shutdown(signal_num, frame):
    global server_active
    server_active = False
    print("Server is shutting down...")

    socketio.emit("server_status", {"active": False}, broadcast=True)
    socketio.stop()

if __name__ == "__main__":
    signal.signal(signal.SIGINT, on_shutdown)

    print("Server is running...")
    socketio.run(app, host="0.0.0.0", port=5000)
