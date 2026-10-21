# AI Firewall: A Secure Middleware with Intelligent AI-Based Filtering for Safe Use of Public AI in Organizations

### COMSATS University Islamabad — Department of Computer Engineering
**Bachelor of Science in Computer Engineering (BCE) Final Year Project**

---

## 📌 Executive Overview
The **AI Firewall System** is an enterprise-grade, multi-tenant AI security middleware and reverse proxy engineered to secure thousands of employees across organizations. It provides bidirectional Data Loss Prevention (DLP), intelligent contextual ML classification, a Reversible Anonymization Vault, and a drop-in OpenAI-compatible API gateway (`/v1/chat/completions`).

Rather than spending millions on on-premises GPU clusters or enforcing restrictive network bans, companies deploy the AI Firewall as an inline gateway that intercepts, pseudonymizes, and audits employee prompts in real time with sub-50ms latency.

---

## 🏢 Enterprise SaaS Architecture (Built for Scale)

- **Drop-In OpenAI Gateway (`/v1/chat/completions`)**: Organizations point their existing Python/Node.js codebases, internal AI agents, and tools to the gateway simply by switching `base_url="https://gateway.domain.com/v1"`.
- **Reversible Vault (De-identification & Re-identification)**: Unlike destructive redacting, the vault substitutes sensitive PII with surrogate tokens (`@PSEUDO_CNIC_1`, `@PSEUDO_EMAIL_1`) before forwarding to the public LLM, and restores the real values when the completion returns to the user.
- **Multi-Tenant Corporate Isolation**: Partitioned audit logs, vector indices, and quotas per tenant (e.g., Acme Corp, Apex FinTech).
- **Departmental Token Budgets & Rate Limiting**: Track usage and enforce token limits across Engineering, HR, Finance, and Risk teams.
- **SIEM-Ready Forensic Audit Trail**: Structured event logs formatted for direct export into Splunk, Datadog, or Microsoft Sentinel.

1. **Dual-Tier Threat Inspection Engine**:
   - **Deterministic Heuristic Layer (High-Performance Regex)**: Tokenizes and redacts structured entities including:
     - 🇵🇰 Pakistani CNIC (`\d{5}-\d{7}-\d{1}`)
     - 📱 Pakistani Telecom numbers (`+92 / 03xx`)
     - 📧 Email addresses
     - 🔑 API Keys (OpenAI `sk-...`, AWS `AKIA...`, GitHub tokens)
     - 🛡️ JWT Tokens & Bearer authentication strings
     - 💳 Credit & Debit Card numbers
     - 🏢 Private Enterprise IPs (`10.x`, `192.168.x`, `172.16.x`)
     - 🏦 Pakistani Bank IBANs
   - **Contextual Machine Learning Layer (NLP)**: TF-IDF feature extraction coupled with an ensemble **Random Forest Classifier** (`models/sensitivity_model.pkl`) to evaluate semantic corporate confidentiality (unreleased roadmaps, secret code names, salaries, financial projections).

2. **Bidirectional Data Loss Prevention (DLP)**:
   - Sanitizes outgoing prompts sent to public AI.
   - Inspects incoming AI completions to prevent accidental reflection of confidential data or hallucinated credentials.

3. **Enterprise Knowledge Retrieval (RAG)**:
   - Built-in **ChromaDB Vector Database** with local semantic embeddings.
   - Injects authorized internal company policies, SOPs, and employee handbooks into user prompts without exposing company files to external AI model fine-tuning.

4. **Role-Based Access Control (RBAC)**:
   - Configurable sensitivity thresholds and permissions across **Employee**, **Developer**, **Finance**, and **Admin** profiles.

5. **Forensic Audit Logging & Telemetry**:
   - Persistent SQLite / SQLAlchemy storage capturing user IPs, original vs redacted prompts, exact detection spans, AI sensitivity scores, and latencies.

6. **Interactive React Security Dashboard**:
   - **Live Playground**: Real-time chat with side-by-side prompt diffing and risk gauges.
   - **Threat Analytics**: Key security metrics and category distributions.
   - **Forensic Audit Table**: Searchable, filterable audit records with JSON inspection drawers.
   - **Knowledge Base Manager**: Add, delete, and test indexed documents in ChromaDB.
   - **Policy Editor**: Sliders for AI sensitivity thresholds and toggles for active regex guardrails.

---

## 🏗️ System Architecture

```
User / Client App
       │
       ▼  [1] Prompt
┌────────────────────────────────────────────────────────┐
│               AI FIREWALL MIDDLEWARE                   │
│                  (FastAPI Gateway)                     │
│  ┌───────────────────────┐   ┌───────────────────────┐ │
│  │ Dual-Tier Inspection  │   │  ChromaDB Vector RAG  │ │
│  │ - Regex Heuristics    │   │  - Internal Company   │ │
│  │ - Scikit-Learn Model  │   │    SOPs & Guidelines  │ │
│  └───────────────────────┘   └───────────────────────┘ │
└──────────────────────────┬─────────────────────────────┘
                           │
                 Policy Violation?
                /                 \
         YES   /                   \   NO
              ▼                     ▼
     ┌─────────────────┐   ┌─────────────────────────────┐
     │  BLOCK REQUEST  │   │ Sanitized Prompt + Context  │
     │   (HTTP 403)    │   └──────────────┬──────────────┘
     └─────────────────┘                  │ [2] Forward
                                          ▼
                             ┌─────────────────────────┐
                             │  Public AI (OpenAI API) │
                             └────────────┬────────────┘
                                          │ [3] Response
                                          ▼
                             ┌─────────────────────────┐
                             │ Completion Output Filter│
                             └────────────┬────────────┘
                                          │ [4] Safe Output
                                          ▼
                                     User / Client
                                          │
                                          ▼ [5] Async Forensic Log
                             ┌─────────────────────────┐
                             │  Audit Database & React │
                             │   Telemetry Dashboard   │
                             └─────────────────────────┘
```

---

## 📁 Repository Structure

```
ai/
├── FYP_Proposal_AI_Firewall.md   # Official COMSATS BCE FYP Proposal Document
├── README.md                     # Project Documentation & Architecture Guide
├── run_all.bat                   # Master launcher (starts Backend + Frontend + Browser)
├── run_backend.bat               # Starts FastAPI backend on port 8000
├── run_frontend.bat              # Starts React Vite frontend on port 5173
├── models/
│   ├── sensitivity_model.pkl     # Pre-trained Scikit-learn Random Forest Model
│   └── vectorizer.pkl            # TF-IDF Feature Extractor
├── backend/
│   ├── main.py                   # FastAPI REST API & Reverse Proxy Gateway
│   ├── filter.py                 # Dual-tier inspection engine (Regex + ML Classifier)
│   ├── model.py                  # ML dataset generator, trainer, and evaluator
│   ├── rag.py                    # ChromaDB Enterprise Vector Knowledge Base
│   ├── requirements.txt          # Python dependencies
│   ├── .env.example              # Environment variables template
│   ├── db/
│   │   ├── database.py           # SQLAlchemy AuditLog & Knowledge models
│   │   └── vector_db/            # ChromaDB persistent vector database storage
│   └── logs/
│       └── firewall.db           # SQLite forensic audit database
└── frontend/
    ├── package.json              # React 18, Vite, Lucide Icons, Axios
    ├── vite.config.js            # Vite build configuration
    ├── index.html                # Entry HTML document
    └── src/
        ├── App.jsx               # Main Dashboard Application (Playground, Logs, RAG, Rules)
        ├── index.css             # Cybersecurity Dark Theme & Glassmorphism Design
        └── main.jsx              # Application bootstrap
```

---

## ⚡ Quick Start Instructions

### Option 1: One-Click Master Launcher (Recommended)
Simply double-click:
```cmd
run_all.bat
```
This automatically starts both the backend API and frontend dashboard, and opens `http://localhost:5173` in your default browser.

---

### Option 2: Manual Terminal Launch

#### Step 1: Start Backend (Port 8000)
```powershell
.\.venv\Scripts\python.exe -m uvicorn main:app --app-dir backend --host 127.0.0.1 --port 8000 --reload
```
API Documentation will be live at: `http://localhost:8000/docs`

#### Step 2: Start Frontend (Port 5173)
```powershell
cd frontend
npm.cmd run dev
```
Open `http://localhost:5173` in your browser.

---

## 🎯 FYP Committee Demonstration Scenarios

Use the **Test Scenarios** buttons in the Playground for 1-click verification during your presentation:

1. **Pakistani CNIC & Personal Email Leak**:
   - *Prompt*: `"Please verify customer CNIC 61101-1234567-1 and email user@isb.comsats.edu.pk in NADRA."`
   - *Verdict*: **`REDACTED`**
   - *Result*: `[REDACTED_CNIC]` and `[REDACTED_Email]` masked in real time.

2. **API Key & Database Credential Exfiltration**:
   - *Prompt*: `"Here is our secret database password admin_secret_999 and OpenAI key sk-abcdef12345678901234567890."`
   - *Verdict*: **`BLOCKED` (HTTP 403)**
   - *Result*: Blocked immediately; forensic alert logged.

3. **Contextual Financial & Salary Disclosure (ML Detection)**:
   - *Prompt*: `"Strictly confidential: Q4 executive salaries are Kumail 950k and Ali 850k. Do not disclose."`
   - *Verdict*: **`BLOCKED` / `REDACTED`**
   - *Result*: Evaluated by Scikit-learn NLP sensitivity classifier with $>90\%$ risk probability.

4. **Internal Corporate Guidelines (Enterprise RAG)**:
   - *Prompt*: `"What is the official company policy regarding AI usage and employee expense reimbursements?"`
   - *Verdict*: **`PASSED`**
   - *Result*: Vector database retrieves internal SOPs to answer accurately.

5. **Safe Development Query**:
   - *Prompt*: `"Write an asynchronous Python function using FastAPI and Pydantic to validate user requests."`
   - *Verdict*: **`PASSED`**
   - *Result*: 0% risk score, sub-100ms response time.
