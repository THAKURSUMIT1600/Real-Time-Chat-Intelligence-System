// Chat Intelligence System - Frontend JavaScript

// Global variables
let socket;
let username = "";
let currentRoom = "general";
let messageCount = 0;
let charts = {
  emotion: null,
  entity: null,
  sentiment: null,
};

// Initialize app when DOM is loaded
document.addEventListener("DOMContentLoaded", function () {
  initializeApp();
});

function initializeApp() {
  console.log("🚀 Initializing Chat Intelligence System...");

  // Connect to Socket.IO server
  connectSocket();

  // Setup event listeners
  setupEventListeners();

  // Initialize charts
  initializeCharts();
}

// Socket.IO Connection
function connectSocket() {
  socket = io();

  socket.on("connect", function () {
    console.log("✅ Connected to server");
    updateConnectionStatus("Connected", "success");
  });

  socket.on("disconnect", function () {
    console.log("❌ Disconnected from server");
    updateConnectionStatus("Disconnected", "danger");
  });

  socket.on("connection_response", function (data) {
    console.log("Connection response:", data);
  });

  socket.on("user_joined", function (data) {
    displaySystemMessage(`${data.username} joined the room`);
  });

  socket.on("user_left", function (data) {
    displaySystemMessage(`${data.username} left the room`);
  });

  socket.on("new_message", function (data) {
    displayMessage(data);
    messageCount++;
    updateMessageCount();
  });

  socket.on("message_history", function (data) {
    console.log("Received message history:", data.messages.length, "messages");
    clearMessages();
    data.messages.forEach((msg) => displayMessage(msg));
    messageCount = data.messages.length;
    updateMessageCount();
  });

  socket.on("analytics_update", function (data) {
    console.log("Analytics update received:", data);
    updateAnalytics(data);
  });

  socket.on("error", function (data) {
    console.error("Server error:", data);
    alert("Error: " + data.message);
  });
}

// Setup Event Listeners
function setupEventListeners() {
  // Join button
  document.getElementById("joinBtn").addEventListener("click", joinRoom);

  // Leave button
  document.getElementById("leaveBtn").addEventListener("click", leaveRoom);

  // Message form
  document
    .getElementById("messageForm")
    .addEventListener("submit", sendMessage);

  // Message input character count
  document
    .getElementById("messageInput")
    .addEventListener("input", function () {
      const charCount = this.value.length;
      document.getElementById("charCount").textContent = charCount;
    });

  // Refresh analytics button
  document
    .getElementById("refreshAnalyticsBtn")
    .addEventListener("click", refreshAnalytics);

  // Tab change listener
  document
    .getElementById("analytics-tab")
    .addEventListener("shown.bs.tab", function () {
      refreshAnalytics();
    });

  // Enter key in username/room inputs
  document
    .getElementById("usernameInput")
    .addEventListener("keypress", function (e) {
      if (e.key === "Enter") joinRoom();
    });

  document
    .getElementById("roomInput")
    .addEventListener("keypress", function (e) {
      if (e.key === "Enter") joinRoom();
    });
}

// Join Room
function joinRoom() {
  const usernameInput = document.getElementById("usernameInput").value.trim();
  const roomInput = document.getElementById("roomInput").value.trim();

  if (!usernameInput) {
    alert("Please enter a username");
    return;
  }

  username = usernameInput;
  currentRoom = roomInput || "general";

  // Emit join event
  socket.emit("join", {
    username: username,
    room: currentRoom,
  });

  // Update UI
  document.getElementById("loginForm").style.display = "none";
  document.getElementById("userInfoSection").style.display = "block";
  document.getElementById("roomInfo").style.display = "block";
  document.getElementById("messageInputSection").style.display = "block";

  document.getElementById("currentUsername").textContent = username;
  document.getElementById("currentRoom").textContent = currentRoom;

  // Enable message input
  document.getElementById("messageInput").disabled = false;
  document.getElementById("sendBtn").disabled = false;
  document.getElementById("messageInput").focus();

  console.log(`✅ Joined room: ${currentRoom} as ${username}`);
}

// Leave Room
function leaveRoom() {
  socket.emit("leave", {
    username: username,
    room: currentRoom,
  });

  // Reset UI
  document.getElementById("loginForm").style.display = "block";
  document.getElementById("userInfoSection").style.display = "none";
  document.getElementById("roomInfo").style.display = "none";
  document.getElementById("messageInputSection").style.display = "none";

  document.getElementById("messageInput").disabled = true;
  document.getElementById("sendBtn").disabled = true;

  clearMessages();
  messageCount = 0;
  updateMessageCount();

  console.log("👋 Left room");
}

// Send Message
function sendMessage(e) {
  e.preventDefault();

  const messageInput = document.getElementById("messageInput");
  const text = messageInput.value.trim();

  if (!text) return;

  // Emit message
  socket.emit("send_message", {
    username: username,
    room: currentRoom,
    text: text,
  });

  // Clear input
  messageInput.value = "";
  document.getElementById("charCount").textContent = "0";
  messageInput.focus();
}

// Display Message
function displayMessage(data) {
  const container = document.getElementById("messagesContainer");

  // Remove "no messages" placeholder if exists
  const placeholder = container.querySelector(".text-center.text-muted");
  if (placeholder) {
    placeholder.remove();
  }

  // Create message element
  const messageDiv = document.createElement("div");
  messageDiv.className = "message";

  const timestamp = new Date(data.timestamp).toLocaleTimeString();
  const initial = data.username.charAt(0).toUpperCase();

  // Get analysis data
  const analysis = data.analysis || {};
  const emotion = analysis.emotion || data.emotion || "neutral";
  const entities =
    analysis.entities || (data.entities ? JSON.parse(data.entities) : []);
  const aspectSentiment =
    analysis.aspect_sentiment ||
    (data.aspect_sentiment ? JSON.parse(data.aspect_sentiment) : {});

  messageDiv.innerHTML = `
        <div class="message-header">
            <div class="message-avatar">${initial}</div>
            <span class="message-username">${escapeHtml(data.username)}</span>
            <span class="message-time">${timestamp}</span>
        </div>
        <div class="message-bubble">
            <div class="message-text">${escapeHtml(data.text)}</div>
            ${createAnalysisHTML(emotion, entities, aspectSentiment)}
        </div>
    `;

  container.appendChild(messageDiv);

  // Scroll to bottom
  container.scrollTop = container.scrollHeight;
}

// Create Analysis HTML
function createAnalysisHTML(emotion, entities, aspectSentiment) {
  let html = '<div class="message-analysis">';

  // Emotion
  html += `
        <div class="analysis-item">
            <span class="analysis-icon">😊</span>
            <span class="analysis-label">Emotion:</span>
            <span class="emotion-badge emotion-${emotion}">${emotion}</span>
        </div>
    `;

  // Entities
  if (entities && entities.length > 0) {
    html += `
            <div class="analysis-item">
                <span class="analysis-icon">🏷️</span>
                <span class="analysis-label">Entities:</span>
                <div class="analysis-value">
        `;
    entities.forEach((entity) => {
      html += `<span class="entity-tag">${escapeHtml(entity.text)} (${
        entity.label
      })</span>`;
    });
    html += "</div></div>";
  }

  // Aspect Sentiment
  if (aspectSentiment && Object.keys(aspectSentiment).length > 0) {
    html += `
            <div class="analysis-item">
                <span class="analysis-icon">💭</span>
                <span class="analysis-label">Sentiment:</span>
                <div class="analysis-value">
        `;
    for (const [aspect, sentiment] of Object.entries(aspectSentiment)) {
      const icon =
        sentiment === "positive"
          ? "👍"
          : sentiment === "negative"
          ? "👎"
          : "😐";
      html += `
                <span class="aspect-item">
                    <span class="sentiment-icon sentiment-${sentiment}">${icon}</span>
                    ${escapeHtml(aspect)}
                </span>
            `;
    }
    html += "</div></div>";
  }

  html += "</div>";
  return html;
}

// Display System Message
function displaySystemMessage(text) {
  const container = document.getElementById("messagesContainer");

  const messageDiv = document.createElement("div");
  messageDiv.className = "system-message";
  messageDiv.textContent = text;

  container.appendChild(messageDiv);
  container.scrollTop = container.scrollHeight;
}

// Clear Messages
function clearMessages() {
  const container = document.getElementById("messagesContainer");
  container.innerHTML = `
        <div class="text-center text-muted p-5">
            <i class="bi bi-chat-square-dots" style="font-size: 3rem;"></i>
            <p class="mt-3">No messages yet. Start chatting!</p>
        </div>
    `;
}

// Update Connection Status
function updateConnectionStatus(status, type) {
  const statusEl = document.getElementById("connectionStatus");
  statusEl.textContent = status;
  statusEl.className = `badge bg-${type}`;
}

// Update Message Count
function updateMessageCount() {
  document.getElementById("messageCount").textContent = messageCount;
}

// Initialize Charts
function initializeCharts() {
  // Emotion Chart (Pie)
  const emotionCtx = document.getElementById("emotionChart").getContext("2d");
  charts.emotion = new Chart(emotionCtx, {
    type: "pie",
    data: {
      labels: [],
      datasets: [
        {
          data: [],
          backgroundColor: [
            "#ff6384",
            "#36a2eb",
            "#ffce56",
            "#4bc0c0",
            "#9966ff",
            "#ff9f40",
            "#c9cbcf",
          ],
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: true,
      plugins: {
        legend: {
          position: "bottom",
        },
        title: {
          display: false,
        },
      },
    },
  });

  // Entity Chart (Bar)
  const entityCtx = document.getElementById("entityChart").getContext("2d");
  charts.entity = new Chart(entityCtx, {
    type: "bar",
    data: {
      labels: [],
      datasets: [
        {
          label: "Mentions",
          data: [],
          backgroundColor: "#36a2eb",
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: true,
      scales: {
        y: {
          beginAtZero: true,
          ticks: {
            precision: 0,
          },
        },
      },
      plugins: {
        legend: {
          display: false,
        },
      },
    },
  });

  // Sentiment Chart (Doughnut)
  const sentimentCtx = document
    .getElementById("sentimentChart")
    .getContext("2d");
  charts.sentiment = new Chart(sentimentCtx, {
    type: "doughnut",
    data: {
      labels: ["Positive", "Negative", "Neutral"],
      datasets: [
        {
          data: [0, 0, 0],
          backgroundColor: ["#4bc0c0", "#ff6384", "#c9cbcf"],
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: true,
      plugins: {
        legend: {
          position: "bottom",
        },
      },
    },
  });
}

// Update Analytics
function updateAnalytics(data) {
  console.log("Updating analytics with data:", data);

  // Update emotion chart
  if (data.emotion_distribution) {
    const emotions = Object.keys(data.emotion_distribution);
    const counts = Object.values(data.emotion_distribution);

    charts.emotion.data.labels = emotions;
    charts.emotion.data.datasets[0].data = counts;
    charts.emotion.update();
  }

  // Update entity chart
  if (data.top_entities) {
    const entities = data.top_entities.map((e) => e.entity);
    const counts = data.top_entities.map((e) => e.count);

    charts.entity.data.labels = entities;
    charts.entity.data.datasets[0].data = counts;
    charts.entity.update();
  }

  // Update sentiment chart
  if (data.sentiment_distribution) {
    charts.sentiment.data.datasets[0].data = [
      data.sentiment_distribution.positive || 0,
      data.sentiment_distribution.negative || 0,
      data.sentiment_distribution.neutral || 0,
    ];
    charts.sentiment.update();
  }

  // Update summary
  const summaryHTML = `
        <div class="row text-center">
            <div class="col-6 mb-3">
                <h4 class="text-primary">${data.message_count || 0}</h4>
                <small class="text-muted">Total Messages</small>
            </div>
            <div class="col-6 mb-3">
                <h4 class="text-success">${
                  Object.keys(data.emotion_distribution || {}).length
                }</h4>
                <small class="text-muted">Emotions Detected</small>
            </div>
            <div class="col-6">
                <h4 class="text-info">${(data.top_entities || []).length}</h4>
                <small class="text-muted">Unique Entities</small>
            </div>
            <div class="col-6">
                <h4 class="text-warning">${data.room || "N/A"}</h4>
                <small class="text-muted">Current Room</small>
            </div>
        </div>
        <hr>
        <small class="text-muted">Last updated: ${new Date(
          data.timestamp
        ).toLocaleTimeString()}</small>
    `;

  document.getElementById("analyticsSummary").innerHTML = summaryHTML;
}

// Refresh Analytics
function refreshAnalytics() {
  if (!username || !currentRoom) {
    console.log("Not connected, skipping analytics refresh");
    return;
  }

  console.log("Requesting analytics for room:", currentRoom);
  socket.emit("get_analytics", { room: currentRoom });
}

// Utility Functions
function escapeHtml(text) {
  const div = document.createElement("div");
  div.textContent = text;
  return div.innerHTML;
}

// Auto-refresh analytics every 10 seconds when on analytics tab
setInterval(function () {
  const analyticsTab = document.getElementById("analytics-tab");
  if (analyticsTab.classList.contains("active") && username && currentRoom) {
    refreshAnalytics();
  }
}, 10000);

console.log("✅ App initialized successfully");
