const chatToggle = document.getElementById("chat-toggle");
const chatPopup = document.getElementById("chat-popup");
const closeChat = document.getElementById("close-chat");
const sendBtn = document.getElementById("send-btn");
const clearBtn = document.getElementById("clear-btn");
const userInput = document.getElementById("user-input");
const chatBody = document.getElementById("chat-body");

const langLabel = document.getElementById("lang");
const intentLabel = document.getElementById("intent");
const confidenceLabel = document.getElementById("confidence");

// Open popup
chatToggle.addEventListener("click", () => {
  chatPopup.classList.toggle("hidden");
});

// Close popup
closeChat.addEventListener("click", () => {
  chatPopup.classList.add("hidden");
});

// Send button
sendBtn.addEventListener("click", sendMessage);

// Enter key
userInput.addEventListener("keypress", function (e) {
  if (e.key === "Enter") {
    sendMessage();
  }
});

// Time helper
function getCurrentTime() {
  const now = new Date();
  return now.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
}

// Scroll helper
function scrollToBottom() {
  chatBody.scrollTop = chatBody.scrollHeight;
}

// Create message row
function createMessageRow(type, message, time) {
  const row = document.createElement("div");
  row.className = `message-row ${type}`;

  const avatar = document.createElement("div");
  avatar.className = `avatar ${type}-avatar`;
  avatar.textContent = type === "bot" ? "🤖" : "👤";

  const content = document.createElement("div");
  content.className = "message-content";

  const bubble = document.createElement("div");
  bubble.className = type === "bot" ? "bot-message" : "user-message";
  bubble.textContent = message;

  const timestamp = document.createElement("div");
  timestamp.className = "timestamp";
  timestamp.textContent = time;

  content.appendChild(bubble);
  content.appendChild(timestamp);

  if (type === "bot") {
    row.appendChild(avatar);
    row.appendChild(content);
  } else {
    row.appendChild(content);
    row.appendChild(avatar);
  }

  return row;
}

// Add user message
function addUserMessage(message) {
  const row = createMessageRow("user", message, getCurrentTime());
  chatBody.appendChild(row);
  scrollToBottom();
}

// Add bot message
function addBotMessage(message) {
  removeTypingIndicator();
  const row = createMessageRow("bot", message, getCurrentTime());
  chatBody.appendChild(row);
  scrollToBottom();
}

// Typing indicator
function showTypingIndicator() {
  removeTypingIndicator();

  const row = document.createElement("div");
  row.className = "message-row bot";
  row.id = "typing-indicator";

  const avatar = document.createElement("div");
  avatar.className = "avatar bot-avatar";
  avatar.textContent = "🤖";

  const content = document.createElement("div");
  content.className = "message-content";

  const bubble = document.createElement("div");
  bubble.className = "typing-message";
  bubble.innerHTML = `
    <div class="typing-dots">
      <span></span>
      <span></span>
      <span></span>
    </div>
  `;

  const timestamp = document.createElement("div");
  timestamp.className = "timestamp";
  timestamp.textContent = "typing...";

  content.appendChild(bubble);
  content.appendChild(timestamp);

  row.appendChild(avatar);
  row.appendChild(content);

  chatBody.appendChild(row);
  scrollToBottom();
}

function removeTypingIndicator() {
  const typing = document.getElementById("typing-indicator");
  if (typing) {
    typing.remove();
  }
}

// Fetch backend response
async function fetchBotResponse(message) {
  const response = await fetch("http://127.0.0.1:8000/chat", {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({ message: message })
  });

  if (!response.ok) {
    throw new Error("Backend response failed");
  }

  return await response.json();
}

// Main send function
async function sendMessage() {
  const message = userInput.value.trim();

  if (message === "") return;

  addUserMessage(message);
  userInput.value = "";
  showTypingIndicator();

  try {
    const data = await fetchBotResponse(message);

    langLabel.textContent = `Language : ${data.language}`;
    intentLabel.textContent = `Intent : ${data.intent}`;
    confidenceLabel.textContent = `Confidence : ${data.confidence}`;

    setTimeout(() => {
      addBotMessage(data.reply);
    }, 600);
  } catch (error) {
    removeTypingIndicator();
    addBotMessage("Backend connection error. Please start FastAPI server.");
    langLabel.textContent = "Language : -";
    intentLabel.textContent = "Intent : -";
    confidenceLabel.textContent = "Confidence : -";
    console.error(error);
  }
}

// Load initial messages
function loadInitialMessages() {
  chatBody.innerHTML = "";
  addBotMessage("Hello! How can I help you?");
  addBotMessage("नमस्ते! मैं आपकी कैसे मदद कर सकता हूँ?");
  addBotMessage("नमस्कार! मी तुम्हाला कशी मदत करू शकतो?");
}

// Clear chat
clearBtn.addEventListener("click", () => {
  removeTypingIndicator();
  loadInitialMessages();

  langLabel.textContent = "Language : -";
  intentLabel.textContent = "Intent : -";
  confidenceLabel.textContent = "Confidence : -";
  userInput.value = "";
});

// Initial load
loadInitialMessages();