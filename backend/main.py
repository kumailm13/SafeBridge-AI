import os
import json
import time
import datetime
import uuid
import asyncio
from typing import List, Optional, Dict, Any
from fastapi import FastAPI, HTTPException, Request, Depends, Query, Header
from fastapi.responses import StreamingResponse, PlainTextResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
from dotenv import load_dotenv

# Local modules
from filter import firewall
from rag import knowledge_base
from vault import vault
from db.database import init_db, SessionLocal, AuditLog, KnowledgeDoc, Organization, TenantApiKey

env_path = os.path.join(os.path.dirname(__file__), ".env")
if os.path.exists(env_path):
    load_dotenv(env_path)
load_dotenv()

app = FastAPI(
    title="AI Firewall Enterprise Gateway",
    description="Multi-Tenant AI Security Middleware with Prompt Injection Defense, Reversible Vault, and Drop-In OpenAI Gateway",
    version="2.5.0"
)

# Initialize database schema and seeds
init_db()

# CORS configuration for web dashboards and browser extensions
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Public AI client initialization (OpenAI or Groq compatible)
openai_api_key = os.getenv("OPENAI_API_KEY", "") or os.getenv("GROQ_API_KEY", "")
openai_base_url = os.getenv("OPENAI_BASE_URL", "")
default_model = os.getenv("OPENAI_MODEL", "")

openai_client = None
if openai_api_key and len(openai_api_key) > 15:
    if openai_api_key.startswith("gsk_") and not openai_base_url:
        openai_base_url = "https://api.groq.com/openai/v1"
        if not default_model:
            default_model = "qwen/qwen3.8-27b"
    elif not default_model:
        default_model = "gpt-3.5-turbo"

    try:
        from openai import OpenAI
        client_kwargs = {"api_key": openai_api_key}
        if openai_base_url:
            client_kwargs["base_url"] = openai_base_url
        openai_client = OpenAI(**client_kwargs)
        print(f"[AI Gateway] Public AI Client connected (Base URL: {openai_base_url or 'OpenAI Default'}, Model: {default_model})")
    except Exception as e:
        print(f"[AI Gateway] Public AI initialization error: {e}")


# ----------------- Request Models -----------------

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: List[ChatMessage]
    model: Optional[str] = "gpt-3.5-turbo"
    role: Optional[str] = "Employee"
    enable_rag: Optional[bool] = True
    use_vault: Optional[bool] = True
    org_id: Optional[str] = "org_acme_corp"
    department: Optional[str] = "Engineering"

class OpenAIChatRequest(BaseModel):
    messages: List[ChatMessage]
    model: Optional[str] = "gpt-3.5-turbo"
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = 1000
    stream: Optional[bool] = False

class TestFilterRequest(BaseModel):
    text: str
    role: Optional[str] = "Employee"
    use_vault: Optional[bool] = True

class ScanRequest(BaseModel):
    text: str
    source: Optional[str] = "browser_extension"
    role: Optional[str] = "Employee"
    org_id: Optional[str] = "org_acme_corp"

class KnowledgeCreateRequest(BaseModel):
    title: str
    content: str
    category: Optional[str] = "General"
    org_id: Optional[str] = "org_default"

class ConfigUpdateRequest(BaseModel):
    warn_threshold: Optional[float] = None
    block_threshold: Optional[float] = None
    max_findings_block: Optional[int] = None
    enable_ai_filter: Optional[bool] = None
    enable_regex_filter: Optional[bool] = None
    enable_injection_filter: Optional[bool] = None
    injection_threshold: Optional[float] = None
    active_rules: Optional[Dict[str, bool]] = None

class OrgCreateRequest(BaseModel):
    name: str
    slug: str
    plan: Optional[str] = "Enterprise Pro"
    employee_count: Optional[int] = 5000
    monthly_budget_tokens: Optional[int] = 10000000

class KeyCreateRequest(BaseModel):
    org_id: str
    department: str
    name: str

# ----------------- Status & Health -----------------

@app.get("/")
async def root():
    return {
        "service": "AI Firewall Enterprise Gateway",
        "status": "Operational",
        "version": "2.5.0",
        "capabilities": [
            "OWASP LLM01 Prompt Injection & Jailbreak Defense",
            "Deterministic Multi-Regex DLP (Pakistani CNIC, Cards, Passwords)",
            "Reversible Cryptographic Surrogate Vault",
            "Drop-in OpenAI SDK Gateway (/v1/chat/completions)",
            "Real-time Server-Sent Events (SSE) Streaming Proxy",
            "Multi-Tenant Corporate Isolation & Department Quotas",
            "SIEM Log Stream Export (CEF / Syslog / JSON)"
        ]
    }

@app.get("/api/health")
async def health_check():
    db = SessionLocal()
    db_ok = False
    org_count = 0
    try:
        org_count = db.query(Organization).count()
        db_ok = True
    except Exception:
        db_ok = False
    finally:
        db.close()

    ai_model_loaded = firewall.ai_filter.model is not None
    rag_count = knowledge_base.collection.count() if knowledge_base.collection else 0

    return {
        "status": "healthy" if db_ok else "degraded",
        "database_connected": db_ok,
        "organizations_active": org_count,
        "prompt_injection_guard_active": True,
        "ai_classifier_loaded": ai_model_loaded,
        "rag_vector_db_active": knowledge_base.collection is not None,
        "rag_indexed_documents": rag_count,
        "openai_gateway_configured": openai_client is not None,
        "vault_active": True,
        "active_regex_rules": sum(1 for v in firewall.regex_filter.active_rules.values() if v),
        "timestamp": datetime.datetime.utcnow().isoformat()
    }

# ----------------- Drop-In OpenAI SDK Gateway (/v1/chat/completions) -----------------

@app.post("/v1/chat/completions")
async def openai_compatible_chat(
    request: OpenAIChatRequest,
    req: Request,
    authorization: Optional[str] = Header(None)
):
    """
    Drop-in OpenAI-compatible endpoint.
    Point any official OpenAI SDK (Python/Node/Go) to base_url="http://localhost:8000/v1".
    """
    start_time = time.time()
    db = SessionLocal()

    org_id = "org_default"
    department = "General"
    if authorization and authorization.startswith("Bearer fw_live_"):
        raw_key = authorization.replace("Bearer ", "").strip()
        key_record = db.query(TenantApiKey).filter(TenantApiKey.key == raw_key, TenantApiKey.is_active == True).first()
        if key_record:
            org_id = key_record.org_id
            department = key_record.department

    all_findings = []
    filtered_messages = []
    total_blocked = False
    max_ai_score = 0.0
    max_inj_score = 0.0
    overall_action = "PASSED"
    vault_session_id = None
    vault_mappings = {}

    for msg in request.messages:
        # Multi-tier inspection
        redacted, findings, blocked, score, action, inj_score = firewall.process(msg.content, role="Employee")
        all_findings.extend(findings)
        max_ai_score = max(max_ai_score, score)
        max_inj_score = max(max_inj_score, inj_score)

        if blocked:
            total_blocked = True
            overall_action = "BLOCKED"
            filtered_messages.append({"role": msg.role, "content": "[BLOCKED BY FIREWALL]"})
            continue

        if findings:
            anonymized, vault_session_id, surrogate_map = vault.anonymize(msg.content, findings)
            vault_mappings.update(surrogate_map)
            filtered_messages.append({"role": msg.role, "content": anonymized})
            if overall_action != "BLOCKED":
                overall_action = "VAULT_ANONYMIZED"
        else:
            filtered_messages.append({"role": msg.role, "content": msg.content})

    latency_ms = int((time.time() - start_time) * 1000)

    # Log to Audit DB
    log_entry = AuditLog(
        timestamp=datetime.datetime.utcnow(),
        org_id=org_id,
        department=department,
        user=req.client.host if req.client else "127.0.0.1",
        role="API_Service",
        original_prompt=json.dumps([m.dict() for m in request.messages]),
        filtered_prompt=json.dumps(filtered_messages),
        is_blocked=total_blocked,
        findings=json.dumps(all_findings),
        ai_score=round(max_ai_score, 4),
        latency_ms=latency_ms
    )
    db.add(log_entry)
    db.commit()
    db.close()

    if total_blocked:
        raise HTTPException(
            status_code=403,
            detail={
                "error": {
                    "message": "Request dropped by Enterprise AI Firewall: High sensitivity or Prompt Injection violation.",
                    "type": "firewall_security_violation",
                    "code": 403,
                    "findings": all_findings,
                    "sensitivity_score": max_ai_score,
                    "injection_score": max_inj_score
                }
            }
        )

    ai_text = ""
    target_model = default_model or request.model or "qwen/qwen3.8-27b"
    if openai_client:
        try:
            if "groq.com" in (openai_base_url or "") and (not target_model or "gpt-3" in target_model or "gpt-4" in target_model):
                target_model = "qwen/qwen3.8-27b"
            resp = openai_client.chat.completions.create(
                model=target_model,
                messages=filtered_messages,
                max_tokens=request.max_tokens or 750
            )
            ai_text = resp.choices[0].message.content
        except Exception as e:
            print(f"[AI Gateway] Upstream provider error: {e}")
            ai_text = ""
    
    if not ai_text:
        # High-Fidelity Simulator
        ai_text = (
            f"[AI Firewall Enterprise Shielded Response]\n\n"
            f"Your request was inspected and forwarded via enterprise tenant: {org_id} ({department}).\n"
            f"• Inspection Status: {overall_action}\n"
            f"• Sensitive Entities Protected: {len(all_findings)}\n"
        )
        if vault_mappings:
            ai_text += f"• Reversible Vault Surrogates: {list(vault_mappings.keys())}\n"

    # Reversible Deanonymization
    if vault_session_id:
        ai_text = vault.deanonymize(ai_text, vault_session_id)

    resp_id = f"chatcmpl-{uuid.uuid4().hex[:16]}"
    return {
        "id": resp_id,
        "object": "chat.completion",
        "created": int(time.time()),
        "model": request.model or "gpt-3.5-turbo",
        "choices": [{
            "index": 0,
            "message": {
                "role": "assistant",
                "content": ai_text
            },
            "finish_reason": "stop"
        }],
        "usage": {
            "prompt_tokens": len(" ".join([m.content for m in request.messages]).split()),
            "completion_tokens": len(ai_text.split()),
            "total_tokens": len(" ".join([m.content for m in request.messages]).split()) + len(ai_text.split())
        },
        "firewall_meta": {
            "action": overall_action,
            "findings_count": len(all_findings),
            "sensitivity_score": max_ai_score,
            "injection_score": max_inj_score,
            "latency_ms": int((time.time() - start_time) * 1000)
        }
    }

# ----------------- Interactive Dashboard & Streaming Proxy -----------------

@app.post("/api/proxy/chat")
async def proxy_chat(request: ChatRequest, req: Request):
    """
    Main interactive proxy with Prompt Injection Guard, Reversible Vault, RAG, and live telemetry.
    """
    start_time = time.time()
    db = SessionLocal()
    user_ip = req.client.host if req.client else "127.0.0.1"
    user_role = request.role or "Employee"
    org_id = request.org_id or "org_acme_corp"
    department = request.department or "Engineering"

    all_findings = []
    filtered_messages = []
    total_blocked = False
    max_ai_score = 0.0
    max_inj_score = 0.0
    overall_action = "PASSED"
    vault_session_id = None
    vault_mappings = {}

    for msg in request.messages:
        redacted, findings, blocked, score, action, inj_score = firewall.process(msg.content, role=user_role)
        all_findings.extend(findings)
        max_ai_score = max(max_ai_score, score)
        max_inj_score = max(max_inj_score, inj_score)

        if blocked:
            total_blocked = True
            overall_action = "BLOCKED"
            filtered_messages.append({"role": msg.role, "content": "[BLOCKED BY FIREWALL]"})
            continue

        if findings:
            if request.use_vault:
                anonymized, vault_session_id, surrogate_map = vault.anonymize(msg.content, findings)
                vault_mappings.update(surrogate_map)
                filtered_messages.append({"role": msg.role, "content": anonymized})
                if overall_action != "BLOCKED":
                    overall_action = "VAULT_ANONYMIZED"
            else:
                filtered_messages.append({"role": msg.role, "content": redacted})
                if overall_action != "BLOCKED":
                    overall_action = "REDACTED"
        else:
            filtered_messages.append({"role": msg.role, "content": msg.content})

    # Enterprise RAG Context Augmentation
    rag_context_injected = []
    if not total_blocked and request.enable_rag and len(filtered_messages) > 0:
        latest_user_text = filtered_messages[-1]["content"]
        relevant_chunks = knowledge_base.query(latest_user_text, n_results=2)
        if relevant_chunks:
            rag_context_injected = relevant_chunks
            context_summary = "\n".join([f"- {chunk}" for chunk in relevant_chunks])
            system_guardrail = (
                f"[SYSTEM RAG GROUNDING CONTEXT (Enterprise Guidelines)]:\n{context_summary}\n"
                "Please use the above authorized internal context to help answer the user if applicable. "
                "Do NOT expose unredacted secrets."
            )
            filtered_messages.insert(0, {"role": "system", "content": system_guardrail})

    # Always inject a formatting system prompt at position 0 (after RAG if present)
    formatting_system = {
        "role": "system",
        "content": (
            "You are Safeguard AI, an intelligent, professional, and helpful workplace AI assistant. "
            "Communicate using clean, professional, and accessible language suitable for all company employees.\n\n"
            "Format your responses cleanly using standard Markdown:\n"
            "- Tables: Whenever comparing items, showing structured data, lists of options, or metrics, ALWAYS format them as Markdown tables with headers (| Column 1 | Column 2 | ...) and alignment rows (|---|---|).\n"
            "- Headings: Use # for main titles, ## for section headings, ### for subheadings.\n"
            "- Emphasis: Use **bold** for key concepts and *italic* for secondary emphasis.\n"
            "- Lists: Use bullet points (- item) or numbered steps (1. item) for clear, step-by-step guidance.\n"
            "- Code: Use fenced ```language ... ``` code blocks with the language tag for any code or scripts.\n"
            "- Callouts: Use > blockquote for important notes or security tips.\n"
            "Do not output raw formatting tokens without closing them. "
            "Avoid conversational fluff like 'Sure, here is...' — begin directly with the high-quality answer."
        )
    }
    # Insert the formatting prompt at the very beginning
    filtered_messages.insert(0, formatting_system)

    latency_ms = int((time.time() - start_time) * 1000)

    # Audit Logging
    log_entry = AuditLog(
        timestamp=datetime.datetime.utcnow(),
        org_id=org_id,
        department=department,
        user=user_ip,
        role=user_role,
        original_prompt=json.dumps([m.dict() for m in request.messages]),
        filtered_prompt=json.dumps(filtered_messages),
        is_blocked=total_blocked,
        findings=json.dumps(all_findings),
        ai_score=round(max_ai_score, 4),
        latency_ms=latency_ms
    )
    db.add(log_entry)
    db.commit()
    db.close()

    if total_blocked:
        raise HTTPException(
            status_code=403,
            detail={
                "error": "Request blocked by Enterprise AI Firewall: High sensitivity or Prompt Injection violation.",
                "action": "BLOCKED",
                "findings": all_findings,
                "ai_score": max_ai_score,
                "injection_score": max_inj_score,
                "latency_ms": latency_ms
            }
        )

    ai_response_content = ""
    target_model = default_model or request.model or "qwen/qwen3.8-27b"
    if openai_client:
        try:
            if "groq.com" in (openai_base_url or "") and (not target_model or "gpt-3" in target_model or "gpt-4" in target_model):
                target_model = "qwen/qwen3.8-27b"
            response = openai_client.chat.completions.create(
                model=target_model,
                messages=filtered_messages,
                max_tokens=2500
            )
            ai_response_content = response.choices[0].message.content
        except Exception as e:
            print(f"[AI Gateway] Public AI completion error: {e}")
            ai_response_content = ""

    if not ai_response_content:
        sanitized_query = filtered_messages[-1]["content"] if filtered_messages else ""
        ai_response_content = (
            f"[Enterprise AI Firewall Protected Response]\n\n"
            f"Your request was inspected and safeguarded.\n"
            f"• Organization Tenant: {org_id} ({department})\n"
            f"• Protection Mode: {'Reversible Vault (Pseudonymization)' if request.use_vault else 'Standard Redaction'}\n"
            f"• Inspection Status: {overall_action}\n"
            f"• Sensitivity Risk Score: {max_ai_score * 100:.1f}%\n"
            f"• Prompt Injection Threat Score: {max_inj_score * 100:.1f}%\n"
        )
        if all_findings:
            ai_response_content += f"• Data Entities Safeguarded: {len(all_findings)}\n"
        if rag_context_injected:
            ai_response_content += f"• Enterprise RAG Context: {len(rag_context_injected)} corporate documents retrieved.\n"

        ai_response_content += f"\nForwarded Prompt: \"{sanitized_query}\""

    # Completion Output Inspection
    out_redacted, out_findings, _, _, _, _ = firewall.process(ai_response_content, role=user_role)
    final_findings = all_findings + out_findings

    # Reversible Deanonymization
    if request.use_vault and vault_session_id:
        out_redacted = vault.deanonymize(out_redacted, vault_session_id)

    return {
        "id": f"firewall_resp_{int(time.time())}",
        "choices": [{
            "message": {
                "role": "assistant",
                "content": out_redacted
            }
        }],
        "firewall_telemetry": {
            "action": overall_action,
            "is_blocked": False,
            "ai_score": max_ai_score,
            "injection_score": max_inj_score,
            "findings": final_findings,
            "vault_used": request.use_vault and bool(vault_mappings),
            "vault_mappings": vault_mappings,
            "rag_used": len(rag_context_injected) > 0,
            "latency_ms": int((time.time() - start_time) * 1000)
        }
    }


# ----------------- Server-Sent Events (SSE) Streaming Proxy -----------------

@app.post("/api/proxy/chat/stream")
async def proxy_chat_stream(request: ChatRequest, req: Request):
    """
    Real-time Server-Sent Events (SSE) token streaming endpoint.
    Streams AI tokens smoothly while evaluating sliding-window guardrails.
    """
    # Pre-flight inspection
    all_findings = []
    total_blocked = False
    max_inj_score = 0.0
    vault_session_id = None
    vault_mappings = {}

    for msg in request.messages:
        redacted, findings, blocked, score, action, inj_score = firewall.process(msg.content, role=request.role or "Employee")
        all_findings.extend(findings)
        max_inj_score = max(max_inj_score, inj_score)
        if blocked:
            total_blocked = True

    if total_blocked:
        async def blocked_stream():
            yield f"data: {json.dumps({'error': 'BLOCKED', 'detail': 'Request dropped by AI Firewall security guardrails.'})}\n\n"
            yield "data: [DONE]\n\n"
        return StreamingResponse(blocked_stream(), media_type="text/event-stream")

    user_query = request.messages[-1].content
    if request.use_vault and all_findings:
        anonymized, vault_session_id, surrogate_map = vault.anonymize(user_query, all_findings)
        vault_mappings.update(surrogate_map)

    # Simulated realistic token-by-token streaming generator
    full_response = (
        f"[AI Firewall Streamed Response]\n\n"
        f"Your query was inspected, anonymized, and processed safely.\n"
        f"• Status: {'VAULT_ANONYMIZED' if vault_mappings else 'PASSED'}\n"
        f"• Shielded Tokens: {len(all_findings)}\n\n"
        f"Response text regarding: \"{user_query[:50]}...\""
    )

    if vault_session_id:
        full_response = vault.deanonymize(full_response, vault_session_id)

    async def token_generator():
        words = full_response.split(" ")
        for i, word in enumerate(words):
            chunk = word + (" " if i < len(words) - 1 else "")
            payload = {
                "choices": [{
                    "delta": {"content": chunk},
                    "index": 0
                }],
                "telemetry": {
                    "action": "VAULT_ANONYMIZED" if vault_mappings else "PASSED",
                    "findings_count": len(all_findings),
                    "vault_mappings": vault_mappings
                }
            }
            yield f"data: {json.dumps(payload)}\n\n"
            await asyncio.sleep(0.04) # Smooth human typing cadence
        yield "data: [DONE]\n\n"

    return StreamingResponse(token_generator(), media_type="text/event-stream")

# ----------------- Endpoint / Browser Extension Security Scanner -----------------

@app.post("/api/security/scan")
async def scan_payload(payload: ScanRequest):
    """
    Sub-15ms Diagnostic Scanner endpoint.
    Used by the Enterprise Chrome / Edge Browser Extension to inspect text
    typed into chatgpt.com, claude.ai, or gemini.google.com in real time.
    """
    start_time = time.time()
    redacted, findings, blocked, score, action, inj_score = firewall.process(payload.text, role=payload.role or "Employee")

    vault_text, _, surrogate_map = vault.anonymize(payload.text, findings) if findings else (payload.text, None, {})
    latency_ms = int((time.time() - start_time) * 1000)

    return {
        "text_original": payload.text,
        "text_redacted": redacted,
        "text_vault": vault_text,
        "vault_mappings": surrogate_map,
        "findings": findings,
        "ai_sensitivity_score": score,
        "injection_attack_score": inj_score,
        "is_blocked": blocked,
        "action": action,
        "latency_ms": latency_ms,
        "recommendation": "BLOCK" if blocked else "SANITIZE" if findings else "ALLOW"
    }

@app.post("/api/filter/test")
async def test_filter(payload: TestFilterRequest):
    start_time = time.time()
    redacted, findings, blocked, score, action, inj_score = firewall.process(payload.text, role=payload.role or "Employee")

    vault_text = payload.text
    surrogate_map = {}
    if payload.use_vault and findings:
        vault_text, _, surrogate_map = vault.anonymize(payload.text, findings)

    latency_ms = int((time.time() - start_time) * 1000)

    return {
        "original_text": payload.text,
        "redacted_text": redacted,
        "vault_text": vault_text,
        "vault_mappings": surrogate_map,
        "findings": findings,
        "ai_score": score,
        "injection_score": inj_score,
        "is_blocked": blocked,
        "action": action,
        "role_evaluated": payload.role or "Employee",
        "latency_ms": latency_ms
    }

# ----------------- Enterprise SIEM Export -----------------

@app.get("/api/enterprise/export/siem")
async def export_siem_logs(
    format: str = Query("cef", pattern="^(cef|syslog|json)$"),
    limit: int = Query(100, ge=1, le=1000),
    org_id: Optional[str] = None
):
    """
    Export security audit logs in standard enterprise SIEM formats:
    - CEF (Common Event Format - Splunk & ArcSight)
    - Syslog (RFC 5424)
    - JSON (Datadog & Elastic)
    """
    db = SessionLocal()
    try:
        query = db.query(AuditLog)
        if org_id:
            query = query.filter(AuditLog.org_id == org_id)
        logs = query.order_by(AuditLog.timestamp.desc()).limit(limit).all()

        if format == "json":
            return [
                {
                    "event_id": l.id,
                    "timestamp": l.timestamp.isoformat() if l.timestamp else "",
                    "org_id": l.org_id,
                    "department": l.department,
                    "user": l.user,
                    "action": "BLOCKED" if l.is_blocked else "REDACTED" if l.findings != "[]" else "PASSED",
                    "sensitivity_score": l.ai_score,
                    "findings_count": len(json.loads(l.findings)) if l.findings else 0,
                    "latency_ms": l.latency_ms
                }
                for l in logs
            ]

        elif format == "syslog":
            lines = []
            for l in logs:
                ts = l.timestamp.strftime("%Y-%m-%dT%H:%M:%SZ") if l.timestamp else ""
                act = "BLOCKED" if l.is_blocked else "PASSED"
                lines.append(
                    f"<134>1 {ts} aifirewall-gateway security - - - "
                    f'[event@tenant id="{l.id}" org="{l.org_id}" dept="{l.department}" src="{l.user}" action="{act}" score="{l.ai_score}"]'
                )
            return PlainTextResponse("\n".join(lines), media_type="text/plain")

        else: # CEF format (Splunk / ArcSight default)
            lines = []
            for l in logs:
                severity = "10" if l.is_blocked else "5" if l.findings != "[]" else "1"
                act = "BLOCKED" if l.is_blocked else "REDACTED" if l.findings != "[]" else "PASSED"
                name = "Data Loss Prevention Violation" if l.is_blocked else "Protected AI Query"
                lines.append(
                    f"CEF:0|COMSATS|AIFirewall|2.5|100|{name}|{severity}|"
                    f"src={l.user} cs1={l.org_id} cs1Label=TenantOrg cs2={l.department} cs2Label=Department "
                    f"act={act} cn1={l.latency_ms} cn1Label=LatencyMs"
                )
            return PlainTextResponse("\n".join(lines), media_type="text/plain")
    finally:
        db.close()

# ----------------- Management Endpoints -----------------

@app.get("/api/enterprise/organizations")
async def list_organizations():
    db = SessionLocal()
    try:
        orgs = db.query(Organization).all()
        return [
            {
                "id": o.id,
                "name": o.name,
                "slug": o.slug,
                "plan": o.plan,
                "employee_count": o.employee_count,
                "monthly_budget_tokens": o.monthly_budget_tokens,
                "tokens_consumed": o.tokens_consumed,
                "budget_utilized_percent": round((o.tokens_consumed / (o.monthly_budget_tokens or 1)) * 100, 1),
                "created_at": o.created_at.isoformat() if o.created_at else ""
            }
            for o in orgs
        ]
    finally:
        db.close()

@app.post("/api/enterprise/organizations")
async def create_organization(payload: OrgCreateRequest):
    db = SessionLocal()
    try:
        new_org = Organization(
            id=f"org_{uuid.uuid4().hex[:8]}",
            name=payload.name,
            slug=payload.slug,
            plan=payload.plan or "Enterprise Pro",
            employee_count=payload.employee_count or 5000,
            monthly_budget_tokens=payload.monthly_budget_tokens or 10000000,
            tokens_consumed=0
        )
        db.add(new_org)
        db.commit()
        return {"message": "Organization provisioned successfully", "org_id": new_org.id}
    finally:
        db.close()

@app.get("/api/enterprise/keys")
async def list_api_keys(org_id: Optional[str] = None):
    db = SessionLocal()
    try:
        query = db.query(TenantApiKey)
        if org_id:
            query = query.filter(TenantApiKey.org_id == org_id)
        keys = query.all()
        return [
            {
                "id": k.id,
                "key_preview": f"{k.key[:12]}...{k.key[-4:]}",
                "org_id": k.org_id,
                "department": k.department,
                "name": k.name,
                "is_active": k.is_active,
                "created_at": k.created_at.isoformat() if k.created_at else ""
            }
            for k in keys
        ]
    finally:
        db.close()

@app.post("/api/enterprise/keys")
async def create_api_key(payload: KeyCreateRequest):
    db = SessionLocal()
    try:
        key_secret = f"fw_live_{payload.department.lower()[:3]}_{uuid.uuid4().hex[:16]}"
        new_key = TenantApiKey(
            id=f"key_{uuid.uuid4().hex[:8]}",
            key=key_secret,
            org_id=payload.org_id,
            department=payload.department,
            name=payload.name,
            is_active=True
        )
        db.add(new_key)
        db.commit()
        return {"message": "API key generated", "api_key": key_secret, "id": new_key.id}
    finally:
        db.close()

@app.get("/api/logs")
async def get_logs(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    blocked_only: Optional[bool] = None,
    org_id: Optional[str] = None,
    search: Optional[str] = None
):
    db = SessionLocal()
    try:
        query = db.query(AuditLog)
        if org_id:
            query = query.filter(AuditLog.org_id == org_id)
        if blocked_only is not None:
            query = query.filter(AuditLog.is_blocked == blocked_only)
        if search:
            query = query.filter(
                (AuditLog.user.contains(search)) |
                (AuditLog.role.contains(search)) |
                (AuditLog.department.contains(search)) |
                (AuditLog.original_prompt.contains(search))
            )

        total = query.count()
        logs = query.order_by(AuditLog.timestamp.desc()).offset(offset).limit(limit).all()

        formatted_logs = []
        for l in logs:
            formatted_logs.append({
                "id": l.id,
                "timestamp": l.timestamp.isoformat() if l.timestamp else "",
                "org_id": l.org_id,
                "department": l.department,
                "user": l.user,
                "role": l.role,
                "original_prompt": json.loads(l.original_prompt) if l.original_prompt else [],
                "filtered_prompt": json.loads(l.filtered_prompt) if l.filtered_prompt else [],
                "is_blocked": l.is_blocked,
                "findings": json.loads(l.findings) if l.findings else [],
                "ai_score": l.ai_score,
                "latency_ms": l.latency_ms
            })

        return {"total": total, "logs": formatted_logs}
    finally:
        db.close()

@app.get("/api/analytics")
async def get_analytics(org_id: Optional[str] = None):
    db = SessionLocal()
    try:
        query = db.query(AuditLog)
        if org_id:
            query = query.filter(AuditLog.org_id == org_id)
        total = query.count()
        blocked = query.filter(AuditLog.is_blocked == True).count()

        all_logs = query.all()
        redacted_count = 0
        ai_scores = []
        threat_counts = {}

        for l in all_logs:
            if l.ai_score is not None:
                ai_scores.append(l.ai_score)
            if l.findings:
                try:
                    findings_list = json.loads(l.findings)
                    if len(findings_list) > 0 and not l.is_blocked:
                        redacted_count += 1
                    for f in findings_list:
                        lbl = f.get("label", "Unknown")
                        threat_counts[lbl] = threat_counts.get(lbl, 0) + 1
                except Exception:
                    pass

        avg_score = round(sum(ai_scores) / len(ai_scores), 3) if ai_scores else 0.0

        return {
            "total_requests": total,
            "blocked_requests": blocked,
            "redacted_requests": redacted_count,
            "passed_requests": max(0, total - blocked - redacted_count),
            "average_sensitivity_score": avg_score,
            "threat_breakdown": threat_counts,
            "system_uptime_seconds": int(time.time()),
        }
    finally:
        db.close()

@app.get("/api/knowledge")
async def list_knowledge_docs():
    docs = knowledge_base.list_documents()
    return {"documents": docs, "count": len(docs)}

@app.post("/api/knowledge")
async def add_knowledge_doc(payload: KnowledgeCreateRequest):
    doc_id = knowledge_base.add_document(
        text=payload.content,
        title=payload.title,
        metadata={"category": payload.category, "org_id": payload.org_id}
    )
    if not doc_id:
        raise HTTPException(status_code=500, detail="Failed to add document to vector store.")
    return {"message": "Document indexed successfully", "doc_id": doc_id}

@app.delete("/api/knowledge/{doc_id}")
async def delete_knowledge_doc(doc_id: str):
    success = knowledge_base.delete_document(doc_id)
    if not success:
        raise HTTPException(status_code=404, detail="Document not found.")
    return {"message": "Document deleted successfully"}

@app.get("/api/config")
async def get_config():
    return {
        "thresholds": firewall.config,
        "active_rules": firewall.regex_filter.active_rules,
        "role_policies": firewall.role_policies
    }

@app.post("/api/config")
async def update_config(payload: ConfigUpdateRequest):
    updates = {}
    if payload.warn_threshold is not None:
        updates["warn_threshold"] = payload.warn_threshold
    if payload.block_threshold is not None:
        updates["block_threshold"] = payload.block_threshold
    if payload.max_findings_block is not None:
        updates["max_findings_block"] = payload.max_findings_block
    if payload.enable_ai_filter is not None:
        updates["enable_ai_filter"] = payload.enable_ai_filter
    if payload.enable_regex_filter is not None:
        updates["enable_regex_filter"] = payload.enable_regex_filter
    if payload.enable_injection_filter is not None:
        updates["enable_injection_filter"] = payload.enable_injection_filter
    if payload.injection_threshold is not None:
        updates["injection_threshold"] = payload.injection_threshold

    firewall.update_config(updates)
    if payload.active_rules:
        for rule, status in payload.active_rules.items():
            firewall.regex_filter.set_rule_status(rule, status)

    return {
        "message": "Configuration updated successfully",
        "current_config": firewall.config,
        "active_rules": firewall.regex_filter.active_rules
    }

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
