var socket = io.connect();
var username = '';

// Join the chat
function joinChat() {
    username = document.getElementById('username').value;
    if (username.trim() === '') {
        alert('Please enter a username');
        return;
    }
    socket.emit('join', { username: username });

    document.getElementById('chat-box').classList.remove('hidden');
    document.getElementById('toggle-server').disabled = true;
    document.getElementById('username').disabled = true;  // Disable username input after joining
}

// Send a message to the server
function sendMessage() {
    var message = document.getElementById('message').value;
    if (message.trim() !== '') {
        socket.emit('message', { message: message });
        document.getElementById('message').value = '';  // Clear message input
    }
}

// Leave the chat
function leaveChat() {
    socket.disconnect();  // Disconnect the socket connection
    setTimeout(() => {
        location.reload();  // Reload the page after disconnect
    }, 100);  // Delay reload to allow disconnection to occur
}

// Update connected users count
socket.on('user_list', function(users) {
    document.getElementById('user-count').textContent = users.length;  // Update user count when user list changes
});

// Listen for updated user count
socket.on('user_count', function(userCount) {
    document.getElementById('user-count').textContent = userCount;  // Update the displayed count
});

// Show all messages in the chat
socket.on('message', function(message) {
    var messagesDiv = document.getElementById('messages');
    var newMessage = document.createElement('div');
    
    // Get current user's username dynamically
    var currentUsername = username;  // Or use a method to get the current username dynamically
    var sid = socket.id;  // Current user's socket ID

    // Check if it's a system message (user joined or left)
    if (message.includes("joined the chat.") || message.includes("left the chat.")) {
        newMessage.classList.add('system-message');  // Apply the system message style
    } else if (message.includes(`${currentUsername}:`)) {
        newMessage.classList.add('message', 'sender');  // Apply 'sender' class for current user's messages
    } else {
        newMessage.classList.add('message', 'receiver');  // Apply 'receiver' class for others' messages
    }

    // Split the message into username and message text
    var parts = message.split(': ');
    if (parts.length > 1) {
        var usernameSpan = document.createElement('span');
        usernameSpan.classList.add('username');  // Apply the 'username' class to make it bold
        usernameSpan.style.fontWeight = 'bold';  // Make the username bold
        usernameSpan.textContent = parts[0] + ": ";  // Get the username part
        
        var messageText = document.createElement('span');
        messageText.textContent = parts[1];  // Get the message part

        // Append username and message text
        newMessage.appendChild(usernameSpan);
        newMessage.appendChild(messageText);
    } else {
        newMessage.textContent = message;  // If message doesn't follow 'username: message' format
    }

    messagesDiv.appendChild(newMessage);
});

// Handle username errors (e.g., username already taken)
socket.on('username_error', function(errorMessage) {
    alert(errorMessage);  // Show alert with the error message

    // Make sure chat UI is hidden from the beginning
    document.getElementById('chat-box').classList.add('hidden');
    
    // Reset username input and make it available again for re-entering a new username
    document.getElementById('username').value = '';  
    document.getElementById('username').disabled = false;  // Re-enable the username field for retry
    document.querySelector('button[onclick="joinChat()"]').disabled = false;  // Re-enable the Join button

    // Show the login input area (if hidden) and ensure chat-related elements are not visible
    document.getElementById('toggle-server').disabled = false; // Re-enable the button if needed
});

// Show private messages in red
socket.on('private_message', function(data) {
    var messagesDiv = document.getElementById('messages');
    var newMessage = document.createElement('div');
    
    // Get current user's username dynamically
    var currentUsername = username;  // Or use a method to get the current username dynamically
    var message = data.message;
    var sender = data.from;  // Extract the sender's username
    var isPrivate = data.is_private;  // Flag to check if it's a private message

    // Check if it's a private message
    if (isPrivate) {
        if (sender === currentUsername) {
            // Private message from the current user (display on the right)
            newMessage.classList.add('message', 'sender');
        } else {
            // Private message to the current user (display on the left)
            newMessage.classList.add('message', 'receiver');
        }
    } else {
        // Normal message (broadcasted)
        if (message.includes(`${currentUsername}:`)) {
            newMessage.classList.add('message', 'sender');
        } else {
            newMessage.classList.add('message', 'receiver');
        }
    }

    // Split the message into username and message text
    var parts = message.split(': ');
    if (parts.length > 1) {
        var usernameSpan = document.createElement('span');
        usernameSpan.classList.add('username');  // Apply the 'username' class to make it bold
        usernameSpan.style.fontWeight = 'bold';  // Make the username bold
        usernameSpan.textContent = parts[0] + ": ";  // Get the username part
        
        var messageText = document.createElement('span');
        messageText.textContent = parts[1];  // Get the message part

        // Append username and message text
        newMessage.appendChild(usernameSpan);
        newMessage.appendChild(messageText);
    } else {
        newMessage.textContent = message;  // If message doesn't follow 'username: message' format
    }

    messagesDiv.appendChild(newMessage);
});

