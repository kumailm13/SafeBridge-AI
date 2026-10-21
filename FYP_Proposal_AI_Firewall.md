# COMSATS University Islamabad
## Department of Computer Engineering
### Bachelor of Science in Computer Engineering (BCE) Program
---
# FINAL YEAR PROJECT (FYP) PROPOSAL

---

### **Project Information**

| **Project Title** | **AI Firewall: A Secure Middleware with Intelligent AI-Based Filtering for Safe Use of Public AI in Organizations** |
| :--- | :--- |
| **Project Domain** | Cybersecurity, Generative AI Security, Natural Language Processing (NLP), Middleware Architecture |
| **Academic Year / Session** | 2025 – 2026 / Fall 2025 – Spring 2026 |
| **Project Category** | Applied Research & System Engineering (FYP-I & FYP-II) |

---

### **Project Group Members**

| Sr. No. | Student Name | Registration / Roll No. | Email Address | Contact No. | Signature |
| :---: | :--- | :--- | :--- | :--- | :---: |
| 1. | `[Student Name 1]` | `CIIT/FA21-BCE-XXX/ISB` | `student1@isb.comsats.edu.pk` | `+92-3XX-XXXXXXX` | _________ |
| 2. | `[Student Name 2]` | `CIIT/FA21-BCE-XXX/ISB` | `student2@isb.comsats.edu.pk` | `+92-3XX-XXXXXXX` | _________ |
| 3. | `[Student Name 3]` | `CIIT/FA21-BCE-XXX/ISB` | `student3@isb.comsats.edu.pk` | `+92-3XX-XXXXXXX` | _________ |

---

### **Supervisory Team**

| Role | Name | Designation | Department | Email & Contact | Signature |
| :--- | :--- | :--- | :--- | :--- | :---: |
| **Supervisor** | `[Supervisor Name]` | `[Assistant Professor / Associate Professor / Professor]` | Computer Engineering | `email@comsats.edu.pk`<br>`+92-51-XXXXXXX` | _________ |
| **Co-Supervisor** *(Optional)* | `[Co-Supervisor Name]` | `[Lecturer / Assistant Professor]` | Computer Engineering | `email@comsats.edu.pk`<br>`+92-51-XXXXXXX` | _________ |

---

## 1. Abstract / Executive Summary
The rapid adoption of Public Generative Artificial Intelligence (GenAI) and Large Language Model (LLM) APIs—such as OpenAI ChatGPT, Anthropic Claude, and Google Gemini—has significantly augmented organizational productivity and automated complex enterprise workflows. However, direct and unmonitored employee interaction with third-party public AI services introduces severe cybersecurity and compliance risks. Critical vulnerabilities include unintentional leakage of Personally Identifiable Information (PII), national identification numbers (e.g., CNIC), proprietary source code, credentials, intellectual property, and trade secrets to external servers. Conventional remedies, such as hosting private open-source LLMs on-premises, demand prohibitive capital expenditures (CAPEX) for GPU clusters and unsustainable operational maintenance. Conversely, completely banning public AI severely cripples organizational efficiency and fosters unmanaged "Shadow AI".

This project designs and implements the **AI Firewall System**, an intelligent, low-latency security middleware and reverse proxy positioned seamlessly between enterprise users and public AI providers. The system deploys a **hybrid multi-stage threat detection engine**:
1. **Deterministic Heuristic Engine (High-Performance Regex):** Rapidly scans, identifies, and sanitizes standardized sensitive patterns (Pakistani CNIC, phone numbers, email addresses, credit cards, API keys, and system passwords).
2. **Custom Contextual Machine Learning Classifier (NLP):** Employs TF-IDF feature extraction coupled with an ensemble Random Forest classifier to detect unstructured, contextual corporate secrets (such as confidential financial projections, project code names, and proprietary technical blueprints) that evade pattern-matching heuristics.
3. **Retrieval-Augmented Generation (RAG) Boundary:** Integrates a localized Vector Database (ChromaDB) to inject organization-specific knowledge securely without exposing private data to third-party model retraining.
4. **Bidirectional Inspection & Centralized Audit Trail:** Evaluates both outbound prompts and incoming LLM completions, providing automatic redaction or policy-based request blocking, backed by a persistent SQLite/PostgreSQL audit store and an administrative React-based security telemetry dashboard.

---

## 2. Introduction & Background
Over the past two years, Generative Artificial Intelligence (GenAI) and Large Language Models (LLMs) have evolved from experimental prototypes to indispensable enterprise tools. Employees across software engineering, customer support, human resources, and financial analysis routinely leverage LLMs for code synthesis, text summarization, and strategic analysis.

Despite their utility, public AI models operate in multi-tenant cloud ecosystems where prompt inputs are ingested, processed, and potentially retained by cloud vendors for fine-tuning or logging. This creates unprecedented threat vectors:
* **Data Loss Prevention (DLP) Violations:** Employees routinely paste production database connection strings, proprietary algorithms, financial balances, customer records, and employee identity numbers into prompt fields.
* **Regulatory Non-Compliance:** Unsanitized transmissions violate international data protection frameworks (such as GDPR, HIPAA, ISO/IEC 27001) as well as national statutes like Pakistan's Prevention of Electronic Crimes Act (PECA) and Digital Personal Data Protection mandates.
* **The "Shadow AI" Dilemma:** When enterprises block public AI domains at the DNS or network level, personnel bypass restrictions via personal devices or unmonitored proxies, removing all enterprise oversight.

To reconcile the competing demands of operational productivity and ironclad data security, there is an urgent need for an **Intelligent AI Firewall Middleware** that acts as an enterprise guardrail—sanitizing outgoing prompts in real time, inspecting incoming AI responses, and keeping full governance inside the corporate perimeter.

---

## 3. Problem Statement
Public AI APIs lack native understanding of internal enterprise data boundaries, corporate confidentiality classifications, and localized regulatory identifiers (such as Pakistani CNIC and domestic phone numbers). Organizations currently face an unsustainable trade-off:
1. **Unrestricted Public AI Access:** Exposes sensitive corporate assets to external cloud logs and model training corpora with zero audit visibility or redaction capability.
2. **On-Premise Private AI Deployment:** Demands high-end enterprise GPU infrastructure (e.g., NVIDIA A100/H100 clusters) costing tens of thousands of dollars, alongside substantial engineering overhead.
3. **Outright Network Bans:** Inhibits workforce productivity, reduces institutional competitiveness, and drives unmonitored "Shadow AI" adoption.

There is currently no lightweight, cost-effective, localized, and open-architecture middleware solution specifically engineered to perform **real-time bidirectional inspection (Regex + Machine Learning)** of LLM traffic while providing localized PII scrubbing, secure RAG integration, and unified security auditing for enterprise networks.

---

## 4. Project Objectives (SMART)
The primary aim of this project is to architect, develop, validate, and deploy a secure middleware proxy system that enforces intelligent, bidirectional data loss prevention on public AI traffic.

The specific project objectives are:
1. **Develop a High-Throughput Asynchronous Reverse Proxy:** Implement a Python (FastAPI) middleware that intercepts outgoing user chat prompts and incoming AI completions with minimal latency overhead (<150 ms per request).
2. **Construct a Dual-Layer Threat Detection Engine:**
   * *Layer 1 (Deterministic Heuristic):* Engineer a regex-based parser capable of identifying and tokenizing structured data, including Pakistani CNIC (`\d{5}-\d{7}-\d{1}`), phone numbers, credit cards, emails, and credential patterns with zero false negatives for standard syntaxes.
   * *Layer 2 (Contextual AI Classifier):* Train and optimize a Scikit-learn NLP model (TF-IDF + Random Forest / Support Vector Classifier) to evaluate semantic sensitivity and proprietary content with a target classification accuracy $\ge 90\%$.
3. **Implement Bidirectional Sanitization & Policy Enforcement:** Support flexible policy actions—including dynamic token redaction (e.g., replacing CNIC with `[REDACTED_CNIC]`) and strict transaction blocking (HTTP 403 Forbidden) when sensitivity scores exceed configurable thresholds.
4. **Incorporate Secure Enterprise RAG (Retrieval-Augmented Generation):** Integrate ChromaDB vector store with OpenAI embedding models (`text-embedding-3-small`) to enable retrieval of proprietary corporate documentation without risking enterprise IP.
5. **Establish an Immutable Audit & Telemetry Dashboard:** Provide a persistent SQL logging schema capturing user identities, raw prompts, redacted versions, detected findings, and timestamps, paired with a React.js administrative dashboard for security posture visualization.

---

## 5. System Architecture & Methodology

### 5.1 High-Level Architecture Flow
The AI Firewall acts as an inline transparent reverse proxy positioned between client applications (web browsers, enterprise chat portals, terminal tools) and third-party public AI providers (OpenAI API).

```
                      +---------------------------------------+
                      |           Enterprise User             |
                      +---------------------------------------+
                                          |
                               [1] Outgoing Prompt
                                          v
                      +---------------------------------------+
                      |         AI FIREWALL MIDDLEWARE        |
                      |            (FastAPI Gateway)          |
                      +---------------------------------------+
                             |                         |
              [2] Inspect & Sanitize            [3] Query Knowledge
                             v                         v
                 +-----------------------+   +-------------------+
                 | Dual-Layer Inspection |   | Secure RAG Engine |
                 | - Regex Heuristic     |   | - ChromaDB Vector |
                 | - Scikit-Learn ML     |   | - Internal Docs   |
                 +-----------------------+   +-------------------+
                             |
                   Is Policy Violated?
                  /                  \
             YES /                    \ NO
                v                      v
        +---------------+      +-------------------------------+
        | BLOCK REQUEST |      | Redacted Prompt + RAG Context |
        |  (HTTP 403)   |      +-------------------------------+
        +---------------+                      |
                                         [4] Forward
                                               v
                                   +-----------------------+
                                   | Public AI (OpenAI API)|
                                   +-----------------------+
                                               |
                                        [5] Completion
                                               v
                      +---------------------------------------+
                      |       Output Filter & Validator       |
                      |  (Checks for Hallucinated Secrets)    |
                      +---------------------------------------+
                                          |
                                   [6] Safe Output
                                          v
                      +---------------------------------------+
                      |           Enterprise User             |
                      +---------------------------------------+
                                          |
                                  [7] Asynchronous
                                          v
                      +---------------------------------------+
                      |    Audit Database (SQLite / Postgres) |
                      |    & React Telemetry Dashboard        |
                      +---------------------------------------+
```

### 5.2 Functional Modules & Methodology

#### A. Ingestion & Reverse Proxy Layer (FastAPI)
* Exposes standard OpenAI-compatible REST endpoints (`/api/proxy/chat`).
* Handles asynchronous payload validation, client authentication, and session extraction.
* Ensures minimal latency overhead through non-blocking I/O.

#### B. Dual-Tier Inspection Pipeline
* **Tier 1: Regex Heuristic Engine:**
  * Pakistani CNIC format: `\b\d{5}-\d{7}-\d{1}\b`
  * Corporate & Personal Email addresses: `\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b`
  * Credential & API Key patterns: `(?i)(password|passwd|pwd|secret|key|bearer)\s*[:=]\s*\S+`
  * Financial Instruments: Luhn-validated Credit / Debit card patterns.
  * Domestic Telecom: Pakistani mobile numbering formats `(\+92|0|92)[0-9]{10}`.
* **Tier 2: Contextual AI Sensitivity Model:**
  * Evaluates prompts against contextual corpora (trade secrets, intellectual property, unreleased roadmaps, internal human resource memos).
  * Feature Extraction: Term Frequency-Inverse Document Frequency (TF-IDF) n-gram vectorizer.
  * Classification: Ensemble Random Forest classifier outputting a continuous sensitivity probability $S \in [0.0, 1.0]$.
  * Decision Matrix:
    * $S < 0.70$ and findings count $\le 5$: Redact detected tokens and forward.
    * $S \ge 0.70$: Tag as `AI_High_Sensitivity`.
    * $S > 0.90$ or findings count $> 5$: Hard block request and trigger security alert.

#### C. Enterprise Knowledge Retrieval (RAG Pipeline)
* Embedded Vector Store using ChromaDB.
* Uses OpenAI `text-embedding-3-small` embeddings to index localized organizational policies, SOPs, and product manuals.
* Injects contextual corporate facts into sanitized prompts to ground model responses without exposing core databases to fine-tuning pipelines.

#### D. Completion (Output) DLP Inspection
* Post-processes model responses returned by public AI.
* Verifies that the model output does not reconstruct masked PII or hallucinate restricted corporate credentials.

#### E. Audit Logging & React Management Dashboard
* Captures immutable forensic records: Client IP, Timestamp, Original Prompt (restricted access), Redacted Prompt, Detection Findings, Classification Score, and Action Taken (Allowed/Redacted/Blocked).
* Admin console created in React (Vite) offering real-time telemetry, threat alerts, user access control, and compliance reporting.

---

## 6. Literature Review & Comparative Analysis

| Feature / Metric | Direct Public AI (e.g. Raw ChatGPT) | Private Self-Hosted LLMs (e.g. Local LLaMA) | Commercial Cloud Gateways (e.g. Cloudflare / Lakera) | Proposed Project (AI Firewall) |
| :--- | :---: | :---: | :---: | :---: |
| **Data Privacy & DLP** | None (Raw data sent to cloud) | High (Data remains local) | Moderate (Cloud dependent) | **High (Local redaction + blocking)** |
| **Infrastructure Cost** | Low (Per-token billing) | Very High (Requires expensive GPUs) | High (Enterprise SaaS licensing) | **Extremely Low (Runs on standard CPU servers)** |
| **Contextual ML Filtering** | None | None | General English rules | **Customizable Hybrid (Regex + Local ML)** |
| **Localized Entities (e.g. CNIC)** | Not Supported | Not Supported | Not Supported | **Fully Supported (Pakistani & Custom PII)** |
| **Integrated Enterprise RAG** | Third-party only | Manual pipeline required | Not native | **Natively integrated via ChromaDB** |
| **Audit & Forensic Logging** | Vendor-dependent | Manual setup | SaaS hosted | **On-premise persistent SQL audit trail** |

---

## 7. Key Features & Deliverables

### 7.1 Key System Features
1. **Intelligent Inbound Filtering:** Automatically redacts or blocks PII, CNIC, passwords, and proprietary company secrets before transmission.
2. **Contextual Outbound Filtering:** Inspects AI responses to prevent accidental data exfiltration or policy violations.
3. **Custom Machine Learning Model:** Pre-trained on synthetic and curated datasets using TF-IDF and Random Forest for contextual risk classification.
4. **Localized Regulatory Compliance:** Out-of-the-box regex heuristics for Pakistani national IDs, telecom numbers, and enterprise secret tokens.
5. **Secure Internal Knowledge Integration (RAG):** ChromaDB-backed retrieval ensuring accurate, company-grounded answers without model retraining.
6. **Role-Based Access Control (RBAC):** Configurable policy tiers (e.g., Engineering, HR, Finance) with customized sensitivity thresholds.
7. **Comprehensive Audit & Analytics Dashboard:** Visual telemetry of blocked prompts, common threat categories, and user activity logs.

### 7.2 Expected Deliverables
1. **Source Code Repository:** Production-ready FastAPI middleware codebase and modular Python filtering engine.
2. **Trained ML Models:** Serialized Scikit-learn classification models (`sensitivity_model.pkl`) and vocabulary vectorizers (`vectorizer.pkl`) with training scripts.
3. **Frontend Application:** React-based administrative and monitoring dashboard.
4. **Documentation & Reports:**
   * FYP-I Documentation and Architecture Specification.
   * FYP-II Final Thesis Report adhering to CUI formatting guidelines.
   * Deployment Guide (Dockerized configuration) and User Manual.
   * Research Paper draft submitted to an IEEE/HEC-recognized conference or journal.

---

## 8. Technology Stack & Tools

| Component | Technology / Library | Rationale |
| :--- | :--- | :--- |
| **Backend Framework** | Python 3.10+, FastAPI, Uvicorn | High-concurrency asynchronous performance, auto-generated OpenAPI documentation, native Pydantic data validation. |
| **Rule-Based Engine** | Python `re` Module | Sub-millisecond deterministic pattern matching and string substitution. |
| **Machine Learning / NLP** | Scikit-learn, Pandas, NumPy, Joblib | Lightweight, robust, and highly interpretable classification with minimal memory footprint on CPU servers. |
| **Vector Database & RAG** | ChromaDB, OpenAI Embedding API | Persistent, serverless vector store for embedding-based similarity search. |
| **Relational Database** | SQLite (Dev) / PostgreSQL (Prod), SQLAlchemy | ACID-compliant structured audit logging and forensic evidence retention. |
| **Frontend Framework** | React.js (Vite), CSS3 / Vanilla CSS / Tailwind | Fast HMR, reactive state management, responsive data visualization. |
| **External AI Gateway** | OpenAI Python SDK (`gpt-3.5-turbo`, `gpt-4o-mini`) | Industry-standard enterprise LLM target. |
| **Development & Versioning** | Git, GitHub, VS Code, Postman | Collaborative version control, API testing, and continuous integration. |

---

## 9. Project Timeline & Work Breakdown Structure (WBS)

The project will be executed across two academic semesters (FYP-I and FYP-II):

```
Semester 7 (FYP-I):
[Month 1] Requirements Gathering & Literature Survey
[Month 2] Dataset Collection, Annotation & Baseline ML Model Training
[Month 3] FastAPI Middleware Architecture & Regex Filtering Engine Development
[Month 4] Integration of AI Sensitivity Model with Middleware & FYP-I Evaluation

Semester 8 (FYP-II):
[Month 5] Enterprise RAG Integration (ChromaDB) & Output Sanitization Module
[Month 6] Role-Based Access Control (RBAC) & React Security Dashboard Development
[Month 7] Comprehensive Stress Testing, Latency Optimization & Security Auditing
[Month 8] Final Documentation, Thesis Writing, and FYP-II External Defense
```

### Milestone Breakdown Table

| Phase | Milestone / Task | Expected Timeline | Deliverables |
| :---: | :--- | :---: | :--- |
| **FYP-I** | Literature Review, Requirement Analysis & SRS | Month 1 | SRS Document & Approved Proposal |
| **FYP-I** | Dataset Compilation, Feature Extraction (TF-IDF) & Model Training | Month 2 | Benchmark ML Model (`.pkl`) |
| **FYP-I** | FastAPI Reverse Proxy & Regex Filtering Engine | Month 3 | Working Ingestion Gateway |
| **FYP-I** | End-to-End Core Middleware Integration & FYP-I Defense | Month 4 | FYP-I Report & Working Demo |
| **FYP-II** | ChromaDB RAG Knowledge Base Integration | Month 5 | Vector Store Query Module |
| **FYP-II** | React Monitoring Dashboard & Audit Analytics | Month 6 | Interactive Web Dashboard |
| **FYP-II** | Security Validation (Evasion Testing), Optimization & Benchmarking | Month 7 | Test Results & Performance Metrics |
| **FYP-II** | Final Thesis Writing, Plagiarism Check & Final Defense | Month 8 | Final Book & Project Defense |

---

## 10. Hardware and Software Requirements

### Hardware Requirements
* **Development Machine:** Intel Core i5/i7 (8th Gen or higher) or AMD Ryzen 5/7, 16 GB RAM, 256 GB NVMe SSD.
* **Deployment / Testing Environment:** Local or Cloud Linux/Windows Server with at least 4 vCPUs and 8 GB RAM (No dedicated GPU required for inference).

### Software Requirements
* **Operating System:** Windows 10/11 or Ubuntu Linux 22.04 LTS.
* **Programming Runtimes:** Python 3.10+, Node.js 18+.
* **Package Managers:** `pip`, `npm`.
* **Database & Vector Store:** SQLite / PostgreSQL, ChromaDB.
* **APIs & SDKs:** OpenAI API Key (or compatible local LLM endpoint).

---

## 11. Potential Challenges and Risk Mitigation

| Identified Risk | Impact | Mitigation Strategy |
| :--- | :---: | :--- |
| **1. Latency Overhead:** Inspecting prompts may slow user-facing responses. | Medium | Utilize asynchronous non-blocking pipelines in FastAPI; keep ML model lightweight (TF-IDF + Random Forest runs in $<20$ ms on CPU). |
| **2. False Positives / Negatives:** ML classifier misidentifying benign prompts or missing novel leak formats. | High | Implement a dual-tier approach: deterministic regex guarantees standard entity detection, while ML handles semantic cues. Include configurable sensitivity thresholds. |
| **3. Adversarial Obfuscation:** Users employing leetspeak or character separation (e.g., `p a s s w 0 r d`). | Medium | Preprocess text with normalization routines, whitespace stripping, and canonical character mapping before evaluation. |
| **4. Third-Party API Rate Limits:** Public AI service interruptions or rate limit throttling. | Low | Implement robust exponential backoff retries and HTTP status code forwarding with informative user notifications. |

---

## 12. References & Academic Citations
1. OWASP Top 10 for Large Language Model Applications (2023). *Open Web Application Security Project (OWASP)*. https://owasp.org/www-project-top-10-for-large-language-model-applications/
2. Yao, Y., Duan, J., Xu, K., Cai, Y., Sun, Z., & Zhang, Y. (2024). *A Survey on Large Language Model (LLM) Security and Privacy: The Good, the Bad, and the Ugly*. IEEE Transactions on Knowledge and Data Engineering.
3. Lewis, P., et al. (2020). *Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks*. Advances in Neural Information Processing Systems (NeurIPS 2020).
4. Carlini, N., et al. (2021). *Extracting Training Data from Large Language Models*. 30th USENIX Security Symposium.
5. National Telecom & Information Technology Policy / PECA (2016). *Prevention of Electronic Crimes Act*, Ministry of Information Technology and Telecommunication, Government of Pakistan.
6. Pedregosa, F., et al. (2011). *Scikit-learn: Machine Learning in Python*. Journal of Machine Learning Research, 12, 2825-2830.
7. Tiangolo, S. (2018). *FastAPI: Modern, Fast (High-Performance), Web Framework for Building APIs with Python*. https://fastapi.tiangolo.com/

---

## 13. Project Signatures & Approval Block

### Submitted By:
| Sr. No. | Student Name | Registration No. | Signature | Date |
| :---: | :--- | :--- | :---: | :---: |
| 1. | `[Student Name 1]` | `CIIT/FA21-BCE-XXX/ISB` | ____________________ | ___ / ___ / 202X |
| 2. | `[Student Name 2]` | `CIIT/FA21-BCE-XXX/ISB` | ____________________ | ___ / ___ / 202X |
| 3. | `[Student Name 3]` | `CIIT/FA21-BCE-XXX/ISB` | ____________________ | ___ / ___ / 202X |

<br>

### Endorsed & Approved By:

**Supervisor Name & Designation:** __________________________________________________  
**Email:** ___________________________________ **Cell No:** __________________________  
**Signature:** _______________________________ **Date:** ___ / ___ / 202X  

<br>

**Co-Supervisor Name & Designation:** _______________________________________________  
**Email:** ___________________________________ **Cell No:** __________________________  
**Signature:** _______________________________ **Date:** ___ / ___ / 202X  

<br>

**FYP Committee Convener / Head of Department (HOD):**  
**Name & Designation:** ____________________________________________________________  
**Signature & Official Stamp:** _____________________________ **Date:** ___ / ___ / 202X  
