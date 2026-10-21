import re
import os
import joblib
from typing import Tuple, List, Dict, Any

class RegexFilter:
    def __init__(self):
        # Comprehensive catalog of regex patterns for sensitive data
        self.patterns = {
            "CNIC": r"\b\d{5}-\d{7}-\d{1}\b",
            "Email": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
            "Password_Keyword": r"(?i)(password|passwd|pwd|secret|auth_token)\s*(?:[:=]|\bis\b)\s*\S+",
            "API_Key": r"\b(?:sk-[a-zA-Z0-9]{20,60}|gh[pousr]_[A-Za-z0-9_]{36,255}|AKIA[0-9A-Z]{16})\b",
            "JWT_Token": r"\beyJ[a-zA-Z0-9_-]{10,}\.[a-zA-Z0-9_-]{10,}\.[a-zA-Z0-9_-]{10,}\b",
            "Credit_Card": r"\b(?:\d{4}[ -]?){3}\d{4}\b",
            "Phone_Number": r"\b(?:\+92|0|92)[0-9]{10}\b", # Pakistan specific mobile numbers
            "Private_IP": r"\b(?:10\.\d{1,3}\.\d{1,3}\.\d{1,3}|192\.168\.\d{1,3}\.\d{1,3}|172\.(?:1[6-9]|2\d|3[01])\.\d{1,3}\.\d{1,3})\b",
            "Bank_IBAN": r"\bPK\d{2}[A-Z]{4}\d{16}\b",
        }
        # Toggles for each pattern
        self.active_rules = {k: True for k in self.patterns.keys()}

    def set_rule_status(self, rule_name: str, enabled: bool):
        if rule_name in self.active_rules:
            self.active_rules[rule_name] = enabled

    def detect(self, text: str) -> List[dict]:
        raw_findings = []
        for label, pattern in self.patterns.items():
            if not self.active_rules.get(label, True):
                continue
            matches = re.finditer(pattern, text)
            for match in matches:
                raw_findings.append({
                    "label": label,
                    "value": match.group(),
                    "start": match.start(),
                    "end": match.end(),
                    "type": "regex"
                })

        # Resolve overlapping regex spans: keep higher priority / longer match
        # Priority order: CNIC > API_Key > JWT_Token > Credit_Card > Phone_Number > Password_Keyword > Email > Private_IP > Bank_IBAN
        priority_map = {
            "CNIC": 10,
            "API_Key": 9,
            "JWT_Token": 8,
            "Credit_Card": 7,
            "Bank_IBAN": 6,
            "Password_Keyword": 5,
            "Email": 4,
            "Phone_Number": 3,
            "Private_IP": 2
        }

        raw_findings.sort(key=lambda x: (x["start"], -priority_map.get(x["label"], 1)))
        resolved_findings = []
        last_end = -1
        for finding in raw_findings:
            if finding["start"] >= last_end:
                resolved_findings.append(finding)
                last_end = finding["end"]
            else:
                # Overlap detected: compare priority
                if resolved_findings:
                    prev = resolved_findings[-1]
                    if priority_map.get(finding["label"], 0) > priority_map.get(prev["label"], 0):
                        resolved_findings[-1] = finding
                        last_end = finding["end"]

        return resolved_findings

    def redact(self, text: str, findings: List[dict]) -> str:
        # Sort regex findings by start index in reverse to preserve original indices
        regex_findings = [f for f in findings if f.get("type") == "regex"]
        sorted_findings = sorted(regex_findings, key=lambda x: x['start'], reverse=True)
        redacted_text = text
        for finding in sorted_findings:
            label = finding['label']
            start = finding['start']
            end = finding['end']
            redacted_text = redacted_text[:start] + f"[REDACTED_{label}]" + redacted_text[end:]
        return redacted_text


class AIFilter:
    def __init__(self):
        self.model = None
        self.vectorizer = None
        self.load_model()

    def load_model(self):
        # Search candidate paths for the trained model
        cur_dir = os.path.dirname(os.path.abspath(__file__))
        repo_root = os.path.dirname(cur_dir)
        candidate_dirs = [
            os.path.join(repo_root, "models"),
            os.path.join(cur_dir, "models"),
            os.path.join(cur_dir, "..", "models"),
            "models"
        ]

        for c_dir in candidate_dirs:
            m_path = os.path.join(c_dir, "sensitivity_model.pkl")
            v_path = os.path.join(c_dir, "vectorizer.pkl")
            if os.path.exists(m_path) and os.path.exists(v_path):
                try:
                    self.model = joblib.load(m_path)
                    self.vectorizer = joblib.load(v_path)
                    print(f"[AIFilter] Successfully loaded ML sensitivity model from {m_path}")
                    return True
                except Exception as e:
                    print(f"[AIFilter] Warning: Error loading model from {m_path}: {e}")
        return False

    def predict_sensitivity(self, text: str) -> float:
        # 1. Scikit-learn ML model prediction
        if self.model and self.vectorizer:
            try:
                X = self.vectorizer.transform([text])
                probs = self.model.predict_proba(X)
                ml_score = float(probs[0][1])
                return round(ml_score, 4)
            except Exception as e:
                print(f"[AIFilter] ML prediction error: {e}")

        # 2. Resilient heuristic contextual semantic score fallback
        text_lower = text.lower()
        contextual_secret_terms = [
            ("confidential", 0.45),
            ("strictly confidential", 0.85),
            ("internal only", 0.60),
            ("restricted", 0.40),
            ("proprietary", 0.50),
            ("trade secret", 0.85),
            ("salary", 0.40),
            ("compensation", 0.35),
            ("financial projection", 0.65),
            ("q4 revenue", 0.70),
            ("quarterly earnings", 0.60),
            ("database password", 0.90),
            ("connection string", 0.75),
            ("root password", 0.90),
            ("secret key", 0.80),
            ("source code leak", 0.75),
            ("customer records", 0.60),
            ("vulnerability report", 0.70),
            ("zero day", 0.75),
            ("private encryption key", 0.90),
        ]

        score = 0.0
        for term, weight in contextual_secret_terms:
            if term in text_lower:
                score = max(score, weight) + 0.1 * (score > 0)
        return min(round(score, 4), 0.99)


from injection import injection_guard

class FirewallFilter:
    def __init__(self):
        self.regex_filter = RegexFilter()
        self.ai_filter = AIFilter()
        self.injection_guard = injection_guard
        # Configurable thresholds
        self.config = {
            "warn_threshold": 0.65,
            "block_threshold": 0.85,
            "max_findings_block": 4,
            "enable_ai_filter": True,
            "enable_regex_filter": True,
            "enable_injection_filter": True,
            "injection_threshold": 0.75
        }
        # Role policies
        self.role_policies = {
            "Admin": {"block_threshold": 0.95, "max_findings_block": 10, "injection_threshold": 0.85},
            "Developer": {"block_threshold": 0.88, "max_findings_block": 6, "injection_threshold": 0.80},
            "Finance": {"block_threshold": 0.75, "max_findings_block": 3, "injection_threshold": 0.70},
            "HR": {"block_threshold": 0.75, "max_findings_block": 3, "injection_threshold": 0.70},
            "Employee": {"block_threshold": 0.85, "max_findings_block": 4, "injection_threshold": 0.75},
        }

    def update_config(self, new_config: Dict[str, Any]):
        self.config.update(new_config)

    def process(self, text: str, role: str = "Employee") -> Tuple[str, List[dict], bool, float, str, float]:
        """
        Process text through multi-tier inspection:
        1. Prompt Injection & Jailbreak (OWASP LLM01)
        2. Deterministic Regex Heuristics
        3. Contextual ML Sensitivity Scorer
        Returns:
            redacted_text: Sanitized or blocked string
            findings: List of detected entities / threat signatures
            is_blocked: Boolean decision
            ai_score: Sensitivity probability [0.0 - 1.0]
            action: "PASSED", "REDACTED", or "BLOCKED"
            injection_score: Injection attack probability [0.0 - 1.0]
        """
        findings = []
        role_policy = self.role_policies.get(role, self.role_policies["Employee"])
        inj_thresh = role_policy.get("injection_threshold", self.config["injection_threshold"])
        block_threshold = role_policy.get("block_threshold", self.config["block_threshold"])
        max_findings = role_policy.get("max_findings_block", self.config["max_findings_block"])

        # 1. Prompt Injection & Jailbreak Inspection (First Line of Defense)
        injection_score = 0.0
        if self.config.get("enable_injection_filter", True):
            inj_res = self.injection_guard.analyze(text)
            injection_score = inj_res["injection_score"]
            if inj_res["findings"]:
                findings.extend(inj_res["findings"])

            if injection_score >= inj_thresh:
                return (
                    "[REQUEST BLOCKED BY AI FIREWALL: Malicious Prompt Injection or Jailbreak Attempt (OWASP LLM01)]",
                    findings,
                    True,
                    0.0,
                    "BLOCKED",
                    injection_score
                )

        # 2. Regex Heuristic Pass
        if self.config.get("enable_regex_filter", True):
            findings.extend(self.regex_filter.detect(text))

        # 3. AI Contextual Sensitivity Pass
        ai_score = 0.0
        if self.config.get("enable_ai_filter", True):
            ai_score = self.ai_filter.predict_sensitivity(text)
            warn_th = self.config.get("warn_threshold", 0.65)
            if ai_score >= warn_th:
                findings.append({
                    "label": "AI_High_Sensitivity",
                    "value": f"Contextual Secret (Score: {ai_score:.2f})",
                    "score": ai_score,
                    "start": 0,
                    "end": len(text),
                    "type": "ai"
                })

        is_blocked = False
        action = "PASSED"

        # Hard blocking decision based on DLP sensitivity or excessive findings
        if ai_score >= block_threshold or len(findings) >= max_findings:
            is_blocked = True
            action = "BLOCKED"
            redacted_text = "[REQUEST BLOCKED BY AI FIREWALL: High sensitivity corporate data leak violation]"
        elif len(findings) > 0:
            action = "REDACTED"
            redacted_text = self.regex_filter.redact(text, findings)
        else:
            action = "PASSED"
            redacted_text = text

        return redacted_text, findings, is_blocked, ai_score, action, injection_score

# Global firewall instance
firewall = FirewallFilter()

