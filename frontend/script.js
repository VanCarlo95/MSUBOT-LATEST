
// script.js

const originalBubblePosition = {
    bottom: "1%",
    right: "1%",
};

let isWaitingForResponse = false;
let chatHistory = [];

// Initialize chat with welcome message
window.onload = function() {
    const chatBubble = document.getElementById("chat-bubble");
    const chatWindow = document.getElementById("chat-window");
    
    // Ensure initial states
    chatBubble.style.opacity = "0";
    chatWindow.classList.add("hidden");
    chatWindow.style.display = "none";
    
    // Show chat bubble with animation
    setTimeout(() => {
        chatBubble.style.opacity = "1";
        // Start the welcome message after the bubble appears
        setTimeout(() => {
            addMessageWithTypewriterEffect("bot", "Hello! I'm A.L.A.B, your MSU-IIT virtual assistant. How can I help you today?");
        }, 800);
    }, 300);
};

function toggleChatWindow() {
    const chatWindow = document.getElementById("chat-window");
    const chatBubble = document.getElementById("chat-bubble");

    if (chatWindow.classList.contains("hidden")) {
        // Opening chat window
        chatWindow.style.display = "flex";
        chatBubble.classList.add("bubble-hidden");
        
        // Small delay to ensure the transition happens
        setTimeout(() => {
            chatWindow.classList.remove("hidden");
        }, 10);
    } else {
        // Closing chat window
        chatWindow.classList.add("hidden");
        
        // Wait for chat window animation to finish before showing bubble
        setTimeout(() => {
            chatWindow.style.display = "none";
            chatBubble.classList.remove("bubble-hidden");
        }, 300);
    }
}


function resetBubblePosition(chatBubble) {
    chatBubble.style.position = "fixed";
    chatBubble.style.bottom = originalBubblePosition.bottom;
    chatBubble.style.right = originalBubblePosition.right;
    chatBubble.style.top = "";
    chatBubble.style.left = "";
}

function positionBubble(chatBubble, chatWindow) {
    const chatWindowRect = chatWindow.getBoundingClientRect();
    chatBubble.style.position = "absolute";
    chatBubble.style.top = `${chatWindowRect.top + window.scrollY - 50}px`;
    chatBubble.style.left = `${chatWindowRect.left + 10}px`;
    chatBubble.style.zIndex = "9999";
}

function handleInput(event) {
    const input = document.getElementById("user-input");
    
    if (event.key === "Enter" && !isWaitingForResponse && input.value.trim()) {
        event.preventDefault();
        sendMessage();
    }
}

function sendMessage() {
    const input = document.getElementById("user-input");
    const message = input.value.trim();

    if (message && !isWaitingForResponse) {
        input.value = "";
        addMessageWithTypewriterEffect("user", message);
        showTypingIndicator();
        
        // Store in chat history
        chatHistory.push({ role: "user", content: message });
        
        sendMessageToServer(message);
    }
}

function showTypingIndicator() {
    const messagesDiv = document.getElementById("messages");
    const typingIndicator = document.createElement("div");
    typingIndicator.className = "typing-indicator";
    typingIndicator.innerHTML = `
        <div class="typing-dot"></div>
        <div class="typing-dot"></div>
        <div class="typing-dot"></div>
    `;
    messagesDiv.appendChild(typingIndicator);
    scrollToBottom();
    isWaitingForResponse = true;
}

function removeTypingIndicator() {
    const messagesDiv = document.getElementById("messages");
    const typingIndicator = messagesDiv.querySelector(".typing-indicator");
    if (typingIndicator) {
        typingIndicator.remove();
    }
    isWaitingForResponse = false;
}

function scrollToBottom() {
    const messagesDiv = document.getElementById("messages");
    if (messagesDiv) {
        messagesDiv.scrollTop = messagesDiv.scrollHeight;
    }
}

function sendMessageToServer(message) {
    const url = 'http://localhost:5005/chat';
    console.log('Sending message to server:', { message });
    
    fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        },
        mode: 'cors',
        body: JSON.stringify({ 
            sender: "user",
            message: message 
        })
    })
    .then(response => {
        console.log('Response status:', response.status);
        console.log('Response headers:', response.headers);
        
        if (!response.ok) {
            throw new Error(`Server responded with status: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        console.log('Received response:', data);
        removeTypingIndicator();
        
        if (data.message) {
            addMessageWithTypewriterEffect("bot", data.message);
        } else if (data.error) {
            addMessageWithTypewriterEffect("bot", `Error: ${data.error}`);
        } else {
            addMessageWithTypewriterEffect("bot", "I received your message but I'm not sure how to respond.");
        }
    })
    .catch((error) => {
        console.error('Network or parsing error:', error);
        removeTypingIndicator();
        addMessageWithTypewriterEffect(
            "bot", 
            `Sorry, I encountered an error: ${error.message}. Please ensure the Rasa server is running on port 5005.`
        );
    });
}

function addMessageWithTypewriterEffect(sender, message) {
    const messagesDiv = document.getElementById("messages");
    const messageContainer = document.createElement("div");
    const messageLabel = document.createElement("div");
    const messageText = document.createElement("div");

    messageContainer.className = `message ${sender}`;
    messageLabel.className = "message-label";
    messageText.className = "message-text";

    messageLabel.textContent = sender === "user" ? "You" : "A.L.A.B";
    messageContainer.appendChild(messageLabel);
    messageContainer.appendChild(messageText);
    messagesDiv.appendChild(messageContainer);

    // Format the message content
    let formattedText = message
    // Add extra line break after sections
    .replace(/:(.*?)•/g, ':$1\n\n•')
    // Add spacing after bullet points
    .replace(/•\s*/g, '\n• ')
    // Add spacing after numbers in lists
    .replace(/(\d+\.)\s*/g, '\n$1 ')
    // Add double line breaks between major sections
    .replace(/([.!?])\s+(Overview|Key Features|Learning Outcomes|Special Features|Technical Roles|Industries|Growth Path)/g, '$1\n\n$2')
    // Ensure proper spacing around headings
    .replace(/(Overview|Key Features|Learning Outcomes|Special Features|Technical Roles|Industries|Growth Path):/g, '\n$1:\n')
    // Add double line breaks between complete sentences that end responses
    .replace(/([.!?])\s+(?=[A-Z])/g, '$1\n\n');

    // Split into lines and clean up
    const lines = formattedText.split('\n').map(line => line.trim()).filter(line => line);

    let currentText = '';
    let lineIndex = 0;
    let charIndex = 0;

    function typeWriter() {
        if (lineIndex < lines.length) {
            const line = lines[lineIndex];

            if (charIndex < line.length) {
                currentText += line[charIndex];
                // Format the displayed text
                messageText.innerHTML = currentText
                    .split('\n')
                    .map(l => l.trim())
                    .filter(l => l)
                    .join('<br><br>');
                charIndex++;
                messagesDiv.scrollTop = messagesDiv.scrollHeight;
                setTimeout(typeWriter, 20);
            } else {
                currentText += '<br><br>';
                lineIndex++;
                charIndex = 0;
                setTimeout(typeWriter, 30);
            }
        }
    }

    typeWriter();
}



