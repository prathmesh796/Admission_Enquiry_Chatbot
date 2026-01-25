const msgerForm = get(".msger-inputarea");
const msgerInput = get(".msger-input");
const msgerChat = get(".msger-chat");

const BOT_IMG = "static/img/chatbot.png";
const PERSON_IMG = "static/img/person.png";
const BOT_NAME = "ChatBot";
const PERSON_NAME = "You";

// Append message with smooth animation
function appendMessage(name, img, side, text) {
    const msgHTML = `
<div class="msg ${side}-msg">
  <div class="msg-img"><img src="${img}" alt="${name}" width="32px" height="32px"></div>

  <div class="msg-bubble">
    <div class="msg-info">
      <div class="msg-info-name">${name}</div>
      <div class="msg-info-time">${formatDate(new Date())}</div>
    </div>

    <div class="msg-text">${text}</div>
  </div>
</div>
`;

    msgerChat.insertAdjacentHTML("beforeend", msgHTML);
    
    // Smooth scroll to bottom
    setTimeout(() => {
        msgerChat.scrollTo({
            top: msgerChat.scrollHeight,
            behavior: 'smooth'
        });
    }, 100);
}

// Show typing indicator
function showTypingIndicator() {
    const typingHTML = `
<div class="msg left-msg typing-indicator-msg">
  <div class="msg-img"><img src="${BOT_IMG}" alt="Bot" width="32px" height="32px"></div>
  <div class="msg-bubble">
    <div class="typing-indicator">
      <span></span>
      <span></span>
      <span></span>
    </div>
  </div>
</div>
`;
    msgerChat.insertAdjacentHTML("beforeend", typingHTML);
    
    // Smooth scroll to bottom
    setTimeout(() => {
        msgerChat.scrollTo({
            top: msgerChat.scrollHeight,
            behavior: 'smooth'
        });
    }, 100);
}

// Remove typing indicator
function removeTypingIndicator() {
    const typingMsg = msgerChat.querySelector(".typing-indicator-msg");
    if (typingMsg) {
        typingMsg.style.animation = "messageSlide 0.3s cubic-bezier(0.4, 0, 0.2, 1) reverse";
        setTimeout(() => {
            typingMsg.remove();
        }, 300);
    }
}

// Form submit handler
msgerForm.addEventListener("submit", event => {
    event.preventDefault();

    const msgText = msgerInput.value.trim();
    if (!msgText) return;

    // Append user message
    appendMessage(PERSON_NAME, PERSON_IMG, "right", msgText);
    msgerInput.value = "";
    
    // Add slight delay before showing typing indicator
    setTimeout(() => {
        botResponse(msgText);
    }, 300);
});

// Handle Enter key for better UX
msgerInput.addEventListener("keypress", event => {
    if (event.key === "Enter" && !event.shiftKey) {
        event.preventDefault();
        msgerForm.dispatchEvent(new Event("submit"));
    }
});

// Bot response handler
function botResponse(rawText) {
    // Show typing indicator
    showTypingIndicator();
    
    // Get bot response
    $.get("/get", { msg: rawText })
        .done(function (data) {
            console.log("User:", rawText);
            console.log("Bot:", data);
            
            // Remove typing indicator
            removeTypingIndicator();
            
            // Add bot message after a short delay
            setTimeout(() => {
                const msgText = data;
                appendMessage(BOT_NAME, BOT_IMG, "left", msgText);
            }, 400);
        })
        .fail(function() {
            removeTypingIndicator();
            setTimeout(() => {
                appendMessage(BOT_NAME, BOT_IMG, "left", "Sorry, I'm having trouble responding right now. Please try again.");
            }, 400);
        });
}

// Utility functions
function get(selector, root = document) {
    return root.querySelector(selector);
}

function formatDate(date) {
    const h = "0" + date.getHours();
    const m = "0" + date.getMinutes();
    return `${h.slice(-2)}:${m.slice(-2)}`;
}

// Auto-focus input on load
window.addEventListener("load", () => {
    msgerInput.focus();
});