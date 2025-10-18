# Public Chat Application

A simple public chat application that allows users to join using a unique username and chat with anyone connected globally. The app supports both broadcast messages visible to all users and private messages sent directly to a specific user.

---

## Features

- Join the chat with a unique username
- Broadcast messages to all connected users
- Send private messages to specific users using `@username` prefix
- Real-time user count and user list updates
- Web-based chat interface using Flask and Socket.IO
- Command-line socket client-server example included
- Server status handling and graceful shutdown

---

## Project Structure
```
├── client.py # TCP socket client example
├── server.py # TCP socket server example
├── app.py # Flask + Socket.IO web chat server
├── static/
│ ├── style.css # CSS styles for the web chat UI
│ └── script.js # JavaScript for frontend Socket.IO client
├── templates/
│ └── index.html # Web chat interface HTML template
└── README.md # This file
```

---

## Requirements

- Python 3.7+
- Flask
- Flask-SocketIO
- eventlet or gevent (for async Flask-SocketIO server)

Install dependencies with:

```
pip install flask flask-socketio eventlet
```
---

### 1. TCP Socket Chat (client.py & server.py)

This is a simple command-line chat client and server using raw TCP sockets.

Start the server:
```
python server.py
```
The server listens on 127.0.0.1:12345.

Start the client(s):
```
python client.py
```
* Enter your username when prompted.
* Type messages to send broadcast messages.
* Use @username your_message to send private messages.
* Type exit to quit.

### 2. Web Chat Application (app.py)
   
This is a Flask web application with Socket.IO enabling real-time chat via a web browser.

Run the server:
```
python app.py
```
* The server runs on ```http://0.0.0.0:5000/``` by default.
* Open your browser and go to ```http://localhost:5000```
* Enter a unique username to join the chat.
* Send messages in the chatbox.
* Use ```@username``` message to send private messages.
* See real-time user list and connected user count.

---

#### How Private Messaging Works

* Messages starting with ```@username``` are treated as private.
* The message will be sent only to the specified user and the sender.
* Other users will not see private messages.

#### Notes

+ Usernames must be unique; duplicate username attempts will be rejected.
+ The Flask app handles server status and user connection updates in real time.
+ The TCP socket server logs all messages and events to ```chat_server.log```.
+ You can stop the Flask server gracefully with ```Ctrl+C```; it will notify clients of shutdown.

---

### Future Improvements

+ Add authentication and persistent user accounts
+ Support message history and offline messages
+ Improve UI/UX with better styling and notifications
+ Deploy with HTTPS and a proper domain
+ Add group chat rooms or channels

---

## License

This project is open source and free to use.
Feel free to contribute or raise issues!
