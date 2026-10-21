// AI Firewall - Enterprise Content Script
// Intercepts employee keystrokes on ChatGPT, Claude, and Gemini to prevent data exfiltration in real time.

(function () {
  const GATEWAY_URL = "http://localhost:8000/api/security/scan";
  let scanTimeout = null;
  let lastScanResult = null;

  // 1. Inject Floating Status Badge into the web page
  const badge = document.createElement("div");
  badge.className = "ai-firewall-badge";
  badge.innerHTML = `
    <div class="ai-firewall-pulse"></div>
    <span>AI Firewall Active (Acme Corp)</span>
  `;
  document.body.appendChild(badge);

  badge.addEventListener("click", () => {
    alert("AI Firewall Enterprise Gateway v2.5\nStatus: Active & Enforced\nTenant: Acme Corporation Global\nReversible Vault: Enabled\nProtected: ChatGPT, Claude, Gemini");
  });

  // 2. Identify Chat Input Elements across ChatGPT, Claude, and Gemini
  function getChatInput() {
    return (
      document.querySelector("#prompt-textarea") ||
      document.querySelector("textarea") ||
      document.querySelector("div[contenteditable='true']")
    );
  }

  // 3. Debounced Scanner
  async function performScan(text) {
    if (!text || text.trim().length < 5) {
      updateBadge("passed", "AI Firewall Active (Acme Corp)");
      return;
    }

    try {
      const response = await fetch(GATEWAY_URL, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          text: text,
          source: "browser_extension",
          role: "Employee",
          org_id: "org_acme_corp"
        })
      });

      if (response.ok) {
        const result = await response.json();
        lastScanResult = result;

        if (result.is_blocked) {
          updateBadge("blocked", `⛔ Blocked: ${result.action}`);
        } else if (result.findings && result.findings.length > 0) {
          const topFinding = result.findings[0].label;
          updateBadge("warning", `⚠️ Detected: ${topFinding} (${result.findings.length})`);
        } else {
          updateBadge("passed", "AI Firewall: Clean Prompt");
        }
      }
    } catch (e) {
      // Local heuristic fallback if backend offline
      if (/\b\d{5}-\d{7}-\d{1}\b/.test(text)) {
        updateBadge("warning", "⚠️ Sensitive: CNIC Detected");
      } else {
        updateBadge("passed", "AI Firewall Active (Local)");
      }
    }
  }

  function updateBadge(state, label) {
    badge.className = `ai-firewall-badge ${state}`;
    badge.querySelector("span").textContent = label;
  }

  // 4. Attach Listeners to Chat Input
  function attachListeners() {
    const input = getChatInput();
    if (!input || input.__aiFirewallAttached) return;

    input.__aiFirewallAttached = true;

    input.addEventListener("input", (e) => {
      const text = input.value || input.innerText || "";
      clearTimeout(scanTimeout);
      scanTimeout = setTimeout(() => performScan(text), 300);
    });

    input.addEventListener("keydown", (e) => {
      if (e.key === "Enter" && !e.shiftKey) {
        if (lastScanResult && lastScanResult.is_blocked) {
          e.preventDefault();
          e.stopPropagation();
          alert("⛔ [AI Firewall Security Violation]\n\nYour message was blocked from sending because it contains sensitive corporate credentials or an adversarial prompt injection attempt.\n\nPlease remove confidential data before proceeding.");
        }
      }
    });
  }

  // Poll for dynamically rendered single-page application inputs
  setInterval(attachListeners, 1000);
  console.log("[AI Firewall] Enterprise Browser Extension Guardrail Loaded.");
})();
