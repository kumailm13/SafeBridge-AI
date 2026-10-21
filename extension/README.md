# AI Firewall: Enterprise Browser Extension (Endpoint DLP)

## 📌 Overview
This browser extension runs silently on employee endpoints (managed Google Chrome and Microsoft Edge browsers). It intercepts prompts when users interact with public AI services (`chatgpt.com`, `claude.ai`, `gemini.google.com`) and performs sub-15ms real-time DLP inspection via the AI Firewall Gateway.

---

## ⚡ How to Load the Extension in Chrome / Edge (Developer & Demo Mode)

1. Open **Google Chrome** or **Microsoft Edge**.
2. Navigate to: `chrome://extensions/` (or `edge://extensions/`).
3. Enable **Developer mode** toggle in the top-right corner.
4. Click **Load unpacked**.
5. Select the `extension` folder inside this repository:
   `c:\Users\line\Desktop\FYP\ai\extension`
6. Navigate to `https://chatgpt.com` or `https://claude.ai`.
7. You will see the floating **AI Firewall Active** badge in the bottom-right corner!

---

## 🏢 Enterprise Mass Deployment (10,000+ Employees)

In corporate environments, IT and SecOps teams deploy this extension silently without requiring manual user installation:

1. **Google Workspace Admin Console**:
   - Go to **Devices** > **Chrome** > **Apps & Extensions** > **Users & Browsers**.
   - Add Extension by ID / Host in the Chrome Web Store private enterprise registry.
   - Installation Policy: **Force Install + Pin to Taskbar**.

2. **Microsoft Intune (Windows & macOS Enterprise)**:
   - Create a Configuration Profile > Administrative Templates > Google Chrome / Microsoft Edge.
   - Configure **"Configure the list of force-installed apps and extensions"**.
   - Push to all corporate devices managed by the organization.
