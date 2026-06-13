/* ============================================================
   SafeHive — Frontend Logic
   Handles order submission, API calls, and conversation rendering.
   ============================================================ */

(function () {
  "use strict";

  // ---------- DOM references ----------
  const userInput        = document.getElementById("user-input");
  const orderBtn         = document.getElementById("order-btn");
  const loadingSection   = document.getElementById("loading-section");
  const loaderStatus     = document.getElementById("loader-status");
  const conversationSec  = document.getElementById("conversation-section");
  const conversationFeed = document.getElementById("conversation-feed");
  const vendorBadge      = document.getElementById("vendor-badge");
  const statusSection    = document.getElementById("status-section");
  const statusBar        = document.getElementById("status-bar");
  const quickBtns        = document.querySelectorAll(".quick-btn");

  const API_BASE = "";  // Same origin

  // ---------- vendor emoji map ----------
  const VENDOR_EMOJI = {
    "Pizza Palace":     "🍕",
    "Burger Barn":      "🍔",
    "Sushi Express":    "🍣",
    "Phish & Chips":    "🐟",
    "Data Harvesters":  "🥗",
    "Crypto Chips Co":  "🌮",
  };

  // ---------- event listeners ----------

  orderBtn.addEventListener("click", handleOrder);

  userInput.addEventListener("keydown", (e) => {
    if (e.key === "Enter") handleOrder();
  });

  quickBtns.forEach((btn) => {
    btn.addEventListener("click", () => {
      userInput.value = btn.dataset.query;
      handleOrder();
    });
  });


  // ---------- main order handler ----------

  async function handleOrder() {
    const query = userInput.value.trim();
    if (!query) {
      userInput.focus();
      return;
    }

    // Reset UI
    resetUI();
    showLoading(true);
    orderBtn.disabled = true;

    try {
      const data = await postOrder(query);
      showLoading(false);
      renderConversation(data);
      renderStatus(data.result);
    } catch (err) {
      showLoading(false);
      renderError(err.message || "Something went wrong");
    } finally {
      orderBtn.disabled = false;
    }
  }


  // ---------- API call ----------

  async function postOrder(userInputText) {
    loaderStatus.textContent = "Sending order to agents...";

    const res = await fetch(`${API_BASE}/api/order`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ user_input: userInputText }),
    });

    if (!res.ok) {
      const errorData = await res.json().catch(() => ({}));
      throw new Error(errorData.detail || `Server error (${res.status})`);
    }

    return res.json();
  }


  // ---------- render conversation ----------

  function renderConversation(data) {
    const result = data.result;
    const conversation = result.conversation || [];

    if (conversation.length === 0) return;

    // Show section
    conversationSec.classList.remove("hidden");

    // Set vendor badge
    const firstVendor = conversation[0].vendor_name || "Unknown";
    const emoji = VENDOR_EMOJI[firstVendor] || "🏪";
    vendorBadge.textContent = `${emoji} ${firstVendor}`;

    const hasThreat = conversation.some((t) => !t.safe);
    vendorBadge.classList.toggle("danger", hasThreat);

    // Render each turn with staggered animation
    conversation.forEach((turn, i) => {
      setTimeout(() => {
        const card = createTurnCard(turn);
        conversationFeed.appendChild(card);
        card.scrollIntoView({ behavior: "smooth", block: "end" });
      }, i * 300);
    });
  }


  function createTurnCard(turn) {
    const isSafe  = turn.safe;
    const threats = turn.threats || [];
    const vendorName = turn.vendor_name || "Vendor";
    const emoji   = VENDOR_EMOJI[vendorName] || "🏪";

    const card = document.createElement("div");
    card.className = `turn-card ${isSafe ? "safe" : "threat"}`;

    // Header
    const header = document.createElement("div");
    header.className = "turn-header";
    header.innerHTML = `
      <span class="turn-label">Turn ${turn.turn} — ${vendorName}</span>
      <span class="turn-status ${isSafe ? "safe" : "threat"}">
        ${isSafe ? "✅ Safe" : "🚨 Alert"}
      </span>
    `;
    card.appendChild(header);

    // Orchestrator message
    card.appendChild(createMessage("🤖", "Orchestrator", turn.orchestrator));

    // Vendor message
    card.appendChild(createMessage(emoji, vendorName, turn.vendor));

    // Threat box (if any)
    if (threats.length > 0) {
      card.appendChild(createThreatBox(threats));
    }

    return card;
  }


  function createMessage(icon, role, text) {
    const div = document.createElement("div");
    div.className = "message";
    div.innerHTML = `
      <span class="message-icon">${icon}</span>
      <div class="message-body">
        <div class="message-role">${role}</div>
        <div class="message-text">${escapeHtml(text)}</div>
      </div>
    `;
    return div;
  }


  function createThreatBox(threats) {
    const box = document.createElement("div");
    box.className = "threat-box";

    let html = `<div class="threat-box-title">🚨 THREATS DETECTED</div>`;

    threats.forEach((t) => {
      const sevClass = (t.severity || "HIGH").toLowerCase();
      html += `
        <div class="threat-item">
          <span class="threat-severity ${sevClass}">${t.severity}</span>
          <span><strong>${t.guard}:</strong> ${escapeHtml(t.reason)}</span>
        </div>
      `;
    });

    box.innerHTML = html;
    return box;
  }


  // ---------- render status ----------

  function renderStatus(result) {
    statusSection.classList.remove("hidden");

    const isSuccess = result.status === "success";
    statusBar.className = `glass-card status-card ${isSuccess ? "success" : "failed"}`;

    if (isSuccess) {
      statusBar.innerHTML = `
        <span class="status-icon">✅</span>
        <span class="status-text">Order completed at ${result.vendor}!</span>
      `;
    } else {
      statusBar.innerHTML = `
        <span class="status-icon">❌</span>
        <span class="status-text">Order failed: ${result.reason || "All vendors blocked"}</span>
      `;
    }

    statusSection.scrollIntoView({ behavior: "smooth", block: "end" });
  }


  function renderError(message) {
    statusSection.classList.remove("hidden");
    statusBar.className = "glass-card status-card failed";
    statusBar.innerHTML = `
      <span class="status-icon">⚠️</span>
      <span class="status-text">Error: ${escapeHtml(message)}</span>
    `;
  }


  // ---------- helpers ----------

  function showLoading(show) {
    loadingSection.classList.toggle("hidden", !show);
  }

  function resetUI() {
    conversationFeed.innerHTML = "";
    conversationSec.classList.add("hidden");
    statusSection.classList.add("hidden");
    statusBar.innerHTML = "";
    statusBar.className = "glass-card status-card";
    vendorBadge.textContent = "";
    vendorBadge.classList.remove("danger");
  }

  function escapeHtml(text) {
    const div = document.createElement("div");
    div.textContent = text || "";
    return div.innerHTML;
  }

})();
