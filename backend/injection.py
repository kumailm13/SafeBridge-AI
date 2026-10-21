import re
import base64
import binascii
from typing import Tuple, List, Dict, Any

class PromptInjectionDetector:
    """
    Advanced Heuristic & Signature Engine for OWASP LLM01: Prompt Injection & Jailbreak Defense.
    Detects attempts to bypass system constraints, jailbreak prompts (DAN, ChaosBot),
    exfiltrate hidden system prompts, or smuggle payloads via delimiter/base64 obfuscation.
    """
    def __init__(self):
        # Known Jailbreak and System Override Signatures
        self.jailbreak_patterns = [
            (r"(?i)\bignore\s+(all\s+)?(previous|prior|above)\s+(instructions|prompts|directives|rules)\b", 0.95, "Instruction Override"),
            (r"(?i)\bdisregard\s+(all\s+)?(previous|prior|above)\s+(instructions|rules|guidelines)\b", 0.95, "Instruction Override"),
            (r"(?i)\byou\s+are\s+now\s+(in\s+developer\s+mode|dan|chaosbot|unfiltered|jailbroken)\b", 0.95, "Persona / Jailbreak Hijack"),
            (r"(?i)\bdo\s+anything\s+now\b", 0.90, "DAN Jailbreak Signature"),
            (r"(?i)\bact\s+as\s+(an\s+unfiltered|an\s+unrestricted|a\s+rogue)\s+(ai|model|assistant)\b", 0.90, "Unrestricted Persona Request"),
            (r"(?i)\bpretend\s+you\s+have\s+no\s+(rules|guidelines|ethical|safety|filters)\b", 0.88, "Constraint Bypass"),
            (r"(?i)\bfrom\s+now\s+on,\s+you\s+(must|will)\s+answer\s+without\s+any\s+(restrictions|filters)\b", 0.92, "Constraint Bypass"),
        ]

        # System Prompt Extraction & Exfiltration Signatures
        self.exfiltration_patterns = [
            (r"(?i)\b(repeat|print|output|display|show|reveal)\s+(the\s+)?(system\s+prompt|initial\s+instructions|system\s+instructions|system\s+message)\b", 0.92, "System Prompt Exfiltration"),
            (r"(?i)\bwhat\s+(is|are)\s+(your\s+)?(system\s+prompt|initial\s+instructions|hidden\s+rules)\b", 0.85, "System Prompt Probing"),
            (r"(?i)\bverbatim\s+repeat\s+(the\s+)?words\s+above\b", 0.88, "Verbatim Exfiltration"),
            (r"(?i)\boutput\s+everything\s+above\s+this\s+line\b", 0.88, "Context Extraction"),
        ]

        # Delimiter & Context Boundary Smuggling
        self.smuggling_patterns = [
            (r"(?i)(<\s*system\s*>|<\s*\/system\s*>|\[\s*system\s*\])", 0.85, "System Delimiter Smuggling"),
            (r"(?i)(###\s*(instruction|system|override)\s*:)", 0.82, "Markdown Header Injection"),
            (r"(?i)(assistant\s*:\s*sure,\s*i\s+can\s+bypass)", 0.90, "Few-Shot Response Forgery"),
        ]

    def deobfuscate(self, text: str) -> Tuple[str, List[Dict[str, Any]]]:
        """
        Normalizes leetspeak, decodes base64 strings, and strips zero-width Unicode characters.
        """
        obfuscation_findings = []
        cleaned = text

        # 1. Strip zero-width and invisible unicode characters
        invisible_chars = ['\u200b', '\u200c', '\u200d', '\ufeff', '\u00ad']
        has_invisibles = any(c in cleaned for c in invisible_chars)
        if has_invisibles:
            for c in invisible_chars:
                cleaned = cleaned.replace(c, '')
            obfuscation_findings.append({
                "type": "obfuscation",
                "label": "Zero_Width_Unicode",
                "detail": "Hidden zero-width spaces stripped from prompt."
            })

        # 2. Check for Base64 payload smuggling
        # Matches base64 sequences of 20+ chars
        b64_matches = re.finditer(r"\b[A-Za-z0-9+/]{24,}={0,2}\b", cleaned)
        for match in b64_matches:
            candidate = match.group()
            try:
                decoded_bytes = base64.b64decode(candidate, validate=True)
                decoded_str = decoded_bytes.decode('utf-8', errors='ignore')
                # If decoded string contains printable english words
                if len(decoded_str) > 10 and any(w in decoded_str.lower() for w in ["ignore", "password", "system", "dan", "prompt", "secret", "cnic"]):
                    obfuscation_findings.append({
                        "type": "obfuscation",
                        "label": "Base64_Payload_Smuggling",
                        "detail": f"Decoded smuggled payload: '{decoded_str[:60]}...'",
                        "decoded_payload": decoded_str
                    })
                    cleaned += f" [DECODED_BASE64: {decoded_str}]"
            except Exception:
                pass

        # 3. Normalized Spacing (e.g. 'i g n o r e   a l l' -> 'ignore all')
        spaced_words = re.finditer(r"\b([a-zA-Z]\s){4,}[a-zA-Z]\b", cleaned)
        for match in spaced_words:
            raw_spaced = match.group()
            collapsed = raw_spaced.replace(" ", "")
            if collapsed.lower() in ["ignore", "password", "system", "prompt", "bypass"]:
                obfuscation_findings.append({
                    "type": "obfuscation",
                    "label": "Character_Spacing_Evasion",
                    "detail": f"De-spaced word '{raw_spaced}' -> '{collapsed}'"
                })
                cleaned = cleaned.replace(raw_spaced, collapsed)

        return cleaned, obfuscation_findings

    def analyze(self, text: str) -> Dict[str, Any]:
        """
        Evaluates the input text against jailbreak, prompt injection, and exfiltration patterns.
        Returns:
            injection_score: Threat score [0.0 - 1.0]
            is_malicious: True if injection_score >= 0.75
            findings: List of matched attack signatures
            normalized_text: Deobfuscated text
        """
        normalized_text, obfuscation_findings = self.deobfuscate(text)
        findings = list(obfuscation_findings)
        max_score = 0.0

        all_rules = (
            self.jailbreak_patterns +
            self.exfiltration_patterns +
            self.smuggling_patterns
        )

        for pattern, weight, category in all_rules:
            matches = re.finditer(pattern, normalized_text)
            for m in matches:
                findings.append({
                    "type": "injection",
                    "label": category,
                    "value": m.group(),
                    "score": weight,
                    "start": m.start(),
                    "end": m.end()
                })
                max_score = max(max_score, weight)

        # Base64 smuggling automatically raises injection score
        for ob in obfuscation_findings:
            if ob.get("label") == "Base64_Payload_Smuggling":
                max_score = max(max_score, 0.90)

        is_malicious = max_score >= 0.75

        return {
            "injection_score": round(max_score, 4),
            "is_malicious": is_malicious,
            "findings": findings,
            "normalized_text": normalized_text
        }

# Global instance
injection_guard = PromptInjectionDetector()
