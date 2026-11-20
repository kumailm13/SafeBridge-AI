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
                    id="dept_cs",
                    name="Department of Computer Science",
                    slug="cs-dept",
                    plan="Faculty & Student AI Portal",
                    employee_count=1850,
                    monthly_budget_tokens=25000000,
                    tokens_consumed=7420000
                ),
                Organization(
                    id="dept_se",
                    name="Department of Software Engineering",
                    slug="se-dept",
                    plan="FYP & Research Gateway",
                    employee_count=1200,
                    monthly_budget_tokens=18000000,
                    tokens_consumed=4950000
                ),
                Organization(
                    id="dept_ece",
                    name="Department of Electrical & Computer Eng.",
                    slug="ece-dept",
                    plan="Robotics & Hardware Lab",
                    employee_count=890,
                    monthly_budget_tokens=12000000,
                    tokens_consumed=2640000
                ),
                Organization(
                    id="dept_reg",
                    name="Registrar & Student Affairs",
                    slug="registrar",
                    plan="Admissions & Identity Records",
                    employee_count=280,
                    monthly_budget_tokens=6000000,
                    tokens_consumed=1680000
                ),
                Organization(
                    id="dept_exam",
                    name="Examination & Controller Office",
                    slug="examination",
                    plan="Confidential Exam Security",
                    employee_count=110,
                    monthly_budget_tokens=4000000,
                    tokens_consumed=820000
                ),
                Organization(
                    id="dept_fin",
                    name="Finance & Accounts Office",
                    slug="finance",
                    plan="Fee Verification & Payroll Guard",
                    employee_count=95,
                    monthly_budget_tokens=3000000,
                    tokens_consumed=540000
                )
            ]
            db.add_all(sample_orgs)

            # Seed sample API keys
            sample_keys = [
                TenantApiKey(
                    id="key_cs",
                    key="fw_live_comsats_cs_8f2910ba",
                    org_id="dept_cs",
                    department="Computer Science",
                    name="CS Faculty & Student AI Portal"
                ),
                TenantApiKey(
                    id="key_se",
                    key="fw_live_comsats_se_6e1194ac",
                    org_id="dept_se",
                    department="Software Engineering",
                    name="SE FYP & Research Gateway"
                ),
                TenantApiKey(
                    id="key_ece",
                    key="fw_live_comsats_ece_9d3412ea",
                    org_id="dept_ece",
                    department="Electrical & Computer Eng.",
                    name="Robotics & Embedded AI Lab"
                ),
                TenantApiKey(
                    id="key_reg",
                    key="fw_live_comsats_reg_4d1290fe",
                    org_id="dept_reg",
                    department="Registrar Office",
                    name="Student Records & Admissions Guard"
                ),
                TenantApiKey(
                    id="key_exam",
                    key="fw_live_comsats_exam_5c8290ba",
                    org_id="dept_exam",
                    department="Examination Office",
                    name="Confidential Exam Moderation Guard"
                ),
                TenantApiKey(
                    id="key_fin",
                    key="fw_live_comsats_fin_7a39109c",
                    org_id="dept_fin",
                    department="Finance & Accounts",
                    name="Fee Audit & Payroll Protection"
                )
            ]
            db.add_all(sample_keys)
            db.commit()

        # Seed initial audit logs if empty
        if db.query(AuditLog).count() == 0:
            sample_logs = [
                AuditLog(
                    timestamp=datetime.datetime.utcnow() - datetime.timedelta(hours=5),
                    org_id="dept_cs",
                    department="Engineering",
                    user="faculty@isb.comsats.edu.pk",
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
                    org_id="dept_cs",
                    department="HR",
                    user="cs_chair@isb.comsats.edu.pk",
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
                    org_id="dept_exam",
                    department="Finance",
                    user="examiner@isb.comsats.edu.pk",
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
