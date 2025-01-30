// script.js

const originalBubblePosition = {
  bottom: "1%",
  right: "1%",
};

let isWaitingForResponse = false;
let chatHistory = [];

// Initialize chat with welcome message
window.onload = function () {
  setTimeout(() => {
    addMessageWithTypewriterEffect(
      "bot",
      "Hello! I'm A.L.A.B, your MSU-IIT virtual assistant. How can I help you today?"
    );
  }, 500);
};

function toggleChatWindow() {
  const chatWindow = document.getElementById("chat-window");
  const chatBubble = document.getElementById("chat-bubble");

  chatWindow.classList.toggle("hidden");

  if (chatWindow.classList.contains("hidden")) {
    resetBubblePosition(chatBubble);
  } else {
    positionBubble(chatBubble, chatWindow);
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
    addMessage("user", message);
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
  console.log("Sending message to server:", { message });

  fetch("https://7df9-49-148-156-93.ngrok-free.app/webhooks/rest/webhook", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Accept: "application/json",
    },
    body: JSON.stringify({ message: message }),
  })
    .then((response) => {
      console.log("Response status:", response.status);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      return response.json();
    })
    .then((data) => {
      console.log("Received response:", data);
      removeTypingIndicator();

      if (Array.isArray(data) && data.length > 0) {
        data.forEach((msg) => {
          if (msg.text) {
            addMessageWithTypewriterEffect("bot", msg.text);
          }
        });
      } else if (data.error) {
        addMessageWithTypewriterEffect(
          "bot",
          "Sorry, I encountered an error: " + data.error
        );
      } else {
        addMessageWithTypewriterEffect(
          "bot",
          "I'm not sure how to respond to that."
        );
      }
    })
    .catch((error) => {
      console.error("Error:", error);
      removeTypingIndicator();
      addMessageWithTypewriterEffect(
        "bot",
        "Sorry, I had trouble understanding that. Please try again."
      );
    });
}

function addMessage(sender, message) {
  const messagesDiv = document.getElementById("messages");
  const messageContainer = document.createElement("div");
  const messageLabel = document.createElement("div");
  const messageText = document.createElement("div");

  messageContainer.className = `message ${sender}`;
  messageLabel.className = "message-label";
  messageText.className = "message-text";

  messageLabel.textContent = sender === "user" ? "You" : "MSU-IIT Bot";
  messageText.textContent = message;

  messageContainer.appendChild(messageLabel);
  messageContainer.appendChild(messageText);
  messagesDiv.appendChild(messageContainer);

  messagesDiv.scrollTop = messagesDiv.scrollHeight;
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

  let index = 0;
  function typeWriter() {
    if (index < message.length) {
      messageText.textContent += message.charAt(index);
      index++;
      // Automatically scroll to the bottom after adding each character
      messagesDiv.scrollTop = messagesDiv.scrollHeight;
      setTimeout(typeWriter, 20);
    }
  }

  typeWriter();
}
