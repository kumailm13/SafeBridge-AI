import os
import json
import datetime
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, Text, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Base directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOGS_DIR = os.path.join(BASE_DIR, "logs")
os.makedirs(LOGS_DIR, exist_ok=True)

DB_PATH = os.path.join(LOGS_DIR, "firewall.db")
DB_URL = f"sqlite:///{DB_PATH}"

engine = create_engine(DB_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class Organization(Base):
    __tablename__ = "organizations"

    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    slug = Column(String, unique=True, index=True)
    plan = Column(String, default="Enterprise")
    employee_count = Column(Integer, default=5000)
    monthly_budget_tokens = Column(Integer, default=10000000)
    tokens_consumed = Column(Integer, default=1420500)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class TenantApiKey(Base):
    __tablename__ = "tenant_api_keys"

    id = Column(String, primary_key=True, index=True)
    key = Column(String, unique=True, index=True)
    org_id = Column(String, index=True)
    department = Column(String, default="Engineering")
    name = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    org_id = Column(String, default="org_default", index=True)
    department = Column(String, default="General")
    user = Column(String, default="127.0.0.1")
    role = Column(String, default="Employee")
    original_prompt = Column(Text)
    filtered_prompt = Column(Text)
    is_blocked = Column(Boolean, default=False)
    findings = Column(Text)
    ai_score = Column(Float, default=0.0)
    latency_ms = Column(Integer, default=0)

class KnowledgeDoc(Base):
    __tablename__ = "knowledge_docs"

    id = Column(String, primary_key=True, index=True)
    org_id = Column(String, default="org_default", index=True)
    title = Column(String)
    content = Column(Text)
    doc_metadata = Column(Text, default="{}")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class FirewallSetting(Base):
    __tablename__ = "firewall_settings"

    key = Column(String, primary_key=True, index=True)
    value = Column(Text)

def init_db():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        # Seed default organizations if table is empty
        if db.query(Organization).count() == 0:
            sample_orgs = [
                Organization(
                    id="org_acme_corp",
                    name="Acme Corporation Global",
                    slug="acme-global",
                    plan="Enterprise Sovereign",
                    employee_count=12500,
                    monthly_budget_tokens=50000000,
                    tokens_consumed=14205000
                ),
                Organization(
                    id="org_fintech_bank",
                    name="Apex FinTech & Banking",
                    slug="apex-fintech",
                    plan="Enterprise Pro",
                    employee_count=4800,
                    monthly_budget_tokens=20000000,
                    tokens_consumed=6720100
                ),
                Organization(
                    id="org_comsats",
                    name="COMSATS University System",
                    slug="comsats-isb",
                    plan="Academic Enterprise",
                    employee_count=3200,
                    monthly_budget_tokens=15000000,
                    tokens_consumed=3890200
                )
            ]
            db.add_all(sample_orgs)

            # Seed sample API keys
            sample_keys = [
                TenantApiKey(
                    id="key_1",
                    key="fw_live_acme_eng_8f2910ba",
                    org_id="org_acme_corp",
                    department="Engineering",
                    name="Engineering CI/CD Pipeline Gateway"
                ),
                TenantApiKey(
                    id="key_2",
                    key="fw_live_acme_hr_99c311fe",
                    org_id="org_acme_corp",
                    department="HR & Operations",
                    name="People Operations Internal Assistant"
                ),
                TenantApiKey(
                    id="key_3",
                    key="fw_live_fintech_71b902ad",
                    org_id="org_fintech_bank",
                    department="SecOps & Risk",
                    name="Compliance Screening Proxy"
                )
            ]
            db.add_all(sample_keys)
            db.commit()

        # Seed initial audit logs if empty
        if db.query(AuditLog).count() == 0:
            sample_logs = [
                AuditLog(
                    timestamp=datetime.datetime.utcnow() - datetime.timedelta(hours=5),
                    org_id="org_acme_corp",
                    department="Engineering",
                    user="dev-lead-41@acme.com",
                    role="Developer",
                    original_prompt=json.dumps([{"role": "user", "content": "How do I optimize our distributed Redis cluster?"}]),
                    filtered_prompt=json.dumps([{"role": "user", "content": "How do I optimize our distributed Redis cluster?"}]),
                    is_blocked=False,
                    findings=json.dumps([]),
                    ai_score=0.08,
                    latency_ms=42
                ),
                AuditLog(
                    timestamp=datetime.datetime.utcnow() - datetime.timedelta(hours=2),
                    org_id="org_acme_corp",
                    department="HR",
                    user="hr-rep-12@acme.com",
                    role="Employee",
                    original_prompt=json.dumps([{"role": "user", "content": "Please verify candidate CNIC 61101-1234567-1 and email candidate@isb.edu.pk."}]),
                    filtered_prompt=json.dumps([{"role": "user", "content": "Please verify candidate CNIC @PSEUDO_CNIC_1 and email @PSEUDO_Email_1."}]),
                    is_blocked=False,
                    findings=json.dumps([
                        {"label": "CNIC", "value": "61101-1234567-1", "start": 25, "end": 40},
                        {"label": "Email", "value": "candidate@isb.edu.pk", "start": 51, "end": 72}
                    ]),
                    ai_score=0.34,
                    latency_ms=68
                ),
                AuditLog(
                    timestamp=datetime.datetime.utcnow() - datetime.timedelta(minutes=30),
                    org_id="org_fintech_bank",
                    department="Finance",
                    user="trader-88@apexfintech.com",
                    role="Finance",
                    original_prompt=json.dumps([{"role": "user", "content": "Export unannounced Q4 margin balances and root password admin_secret_999."}]),
                    filtered_prompt=json.dumps([{"role": "user", "content": "[BLOCKED BY FIREWALL] High sensitivity financial secret."}]),
                    is_blocked=True,
                    findings=json.dumps([
                        {"label": "Password_Keyword", "value": "password admin_secret_999", "start": 51, "end": 76},
                        {"label": "AI_High_Sensitivity", "value": "Contextual Secret", "score": 0.94, "start": 0, "end": 76}
                    ]),
                    ai_score=0.94,
                    latency_ms=31
                )
            ]
            db.add_all(sample_logs)
            db.commit()
    except Exception as e:
        print(f"Error seeding DB: {e}")
    finally:
        db.close()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
