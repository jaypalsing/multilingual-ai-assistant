// =========================================
// ELEMENTS
// =========================================

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

// =========================================
// OPEN CHAT
// =========================================

chatToggle.addEventListener("click", () => {

    chatPopup.classList.toggle("hidden");

    setTimeout(() => {
        userInput.focus();
    }, 300);

});

// =========================================
// CLOSE CHAT
// =========================================

closeChat.addEventListener("click", () => {

    chatPopup.classList.add("hidden");

});

// =========================================
// SEND BUTTON
// =========================================

sendBtn.addEventListener("click", sendMessage);

// =========================================
// ENTER KEY
// =========================================

userInput.addEventListener("keypress", function (e) {

    if (e.key === "Enter" && !e.shiftKey) {

        e.preventDefault();

        sendMessage();
    }

});

// =========================================
// CURRENT TIME
// =========================================

function getCurrentTime() {

    const now = new Date();

    return now.toLocaleTimeString([], {
        hour: "2-digit",
        minute: "2-digit"
    });

}

// =========================================
// AUTO SCROLL
// =========================================

function scrollToBottom() {

    chatBody.scrollTop = chatBody.scrollHeight;

}

// =========================================
// CREATE MESSAGE
// =========================================

function createMessageRow(type, message, time) {

    const row = document.createElement("div");

    row.className = `message-row ${type}`;

    // =========================================
    // AVATAR
    // =========================================

    const avatar = document.createElement("div");

    avatar.className = `avatar ${type}-avatar`;

    avatar.textContent = type === "bot" ? "🤖" : "👤";

    // =========================================
    // CONTENT
    // =========================================

    const content = document.createElement("div");

    content.className = "message-content";

    // =========================================
    // MESSAGE BUBBLE
    // =========================================

    const bubble = document.createElement("div");

    bubble.className =
        type === "bot"
            ? "bot-message"
            : "user-message";

    bubble.textContent = message;

    // =========================================
    // TIMESTAMP
    // =========================================

    const timestamp = document.createElement("div");

    timestamp.className = "timestamp";

    timestamp.textContent = time;

    // =========================================
    // APPEND
    // =========================================

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

// =========================================
// USER MESSAGE
// =========================================

function addUserMessage(message) {

    const row = createMessageRow(
        "user",
        message,
        getCurrentTime()
    );

    chatBody.appendChild(row);

    scrollToBottom();

}

// =========================================
// BOT MESSAGE
// =========================================

 
// =========================================
// BOT MESSAGE
// =========================================

function addBotMessage(message) {

    removeTypingIndicator();

    // =====================================
    // MESSAGE ROW
    // =====================================

    const row = document.createElement("div");

    row.className = "message-row bot";

    // =====================================
    // AVATAR
    // =====================================

    const avatar = document.createElement("div");

    avatar.className = "avatar bot-avatar";

    avatar.textContent = "🤖";

    // =====================================
    // CONTENT
    // =====================================

    const content = document.createElement("div");

    content.className = "message-content";

    // =====================================
    // MODERN CARD
    // =====================================

    const bubble = document.createElement("div");

    bubble.className = "bot-message modern-bot-card";

    // =====================================
    // FORMAT MESSAGE
    // =====================================

    let formattedMessage = message

        .replace(/\n/g, "<br>")

        // Google Maps Link
        .replace(
            /(https?:\/\/[^\s]+)/g,
            `
            <a href="$1"
               target="_blank"
               class="map-link">

               📍 Open Map

            </a>
            `
        );

    bubble.innerHTML = `

        <div class="bot-card-header">

            🤖 MultiLinguaAI

        </div>

        <div class="bot-card-body">

            ${formattedMessage}

        </div>
    `;

    // =====================================
    // TIMESTAMP
    // =====================================

    const timestamp = document.createElement("div");

    timestamp.className = "timestamp";

    timestamp.textContent = getCurrentTime();

    // =====================================
    // APPEND
    // =====================================

    content.appendChild(bubble);

    content.appendChild(timestamp);

    row.appendChild(avatar);

    row.appendChild(content);

    chatBody.appendChild(row);

    scrollToBottom();
}
 


// =========================================
// SHOW TYPING
// =========================================

function showTypingIndicator() {

    removeTypingIndicator();

    const row = document.createElement("div");

    row.className = "message-row bot";

    row.id = "typing-indicator";

    // =========================================
    // BOT AVATAR
    // =========================================

    const avatar = document.createElement("div");

    avatar.className = "avatar bot-avatar";

    avatar.textContent = "🤖";

    // =========================================
    // CONTENT
    // =========================================

    const content = document.createElement("div");

    content.className = "message-content";

    // =========================================
    // BUBBLE
    // =========================================

    const bubble = document.createElement("div");

    bubble.className = "typing-message";

    bubble.innerHTML = `
        <div class="typing-dots">
            <span></span>
            <span></span>
            <span></span>
        </div>
    `;

    // =========================================
    // TIMESTAMP
    // =========================================

    const timestamp = document.createElement("div");

    timestamp.className = "timestamp";

    timestamp.textContent = "Typing...";

    // =========================================
    // APPEND
    // =========================================

    content.appendChild(bubble);

    content.appendChild(timestamp);

    row.appendChild(avatar);

    row.appendChild(content);

    chatBody.appendChild(row);

    scrollToBottom();

}

// =========================================
// REMOVE TYPING
// =========================================

function removeTypingIndicator() {

    const typing =
        document.getElementById("typing-indicator");

    if (typing) {

        typing.remove();

    }

}

// =========================================
// FETCH RESPONSE
// =========================================

async function fetchBotResponse(message) {

    const response = await fetch(
        "http://127.0.0.1:8000/chat",
        {
            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({
                message: message
            })
        }
    );

    if (!response.ok) {

        throw new Error(
            "Backend response failed"
        );

    }

    return await response.json();

}

// =========================================
// SEND MESSAGE
// =========================================

async function sendMessage() {

    const message =
        userInput.value.trim();

    if (message === "") return;

    // =========================================
    // USER MESSAGE
    // =========================================

    addUserMessage(message);

    userInput.value = "";

    showTypingIndicator();

    try {

        const data =
            await fetchBotResponse(message);

        // =========================================
        // UPDATE LABELS
        // =========================================

        langLabel.textContent =
            data.language || "-";

        intentLabel.textContent =
            data.intent || "-";

        confidenceLabel.textContent =
            data.confidence
                ? Number(data.confidence).toFixed(2)
                : "-";

        // =========================================
        // BOT RESPONSE DELAY
        // =========================================

        setTimeout(() => {

            addBotMessage(data.reply);

        }, 700);

    } catch (error) {

        console.error(error);

        removeTypingIndicator();

        addBotMessage(
            "⚠ Backend connection error. Please start FastAPI server."
        );

        langLabel.textContent = "-";

        intentLabel.textContent = "-";

        confidenceLabel.textContent = "-";

    }

}

// =========================================
// INITIAL MESSAGES
// =========================================

function loadInitialMessages() {

    chatBody.innerHTML = "";

    setTimeout(() => {

        addBotMessage(
            "Hello! How can I help you today?"
        );

    }, 300);

    setTimeout(() => {

        addBotMessage(
            "नमस्ते! मैं आपकी कैसे मदद कर सकता हूँ?"
        );

    }, 900);

    setTimeout(() => {

        addBotMessage(
            "नमस्कार! मी तुम्हाला कशी मदत करू शकतो?"
        );

    }, 1500);

}

// =========================================
// CLEAR CHAT
// =========================================

clearBtn.addEventListener("click", () => {

    removeTypingIndicator();

    loadInitialMessages();

    langLabel.textContent = "-";

    intentLabel.textContent = "-";

    confidenceLabel.textContent = "-";

    userInput.value = "";

});

// =========================================
// INITIAL LOAD
// =========================================

loadInitialMessages();

