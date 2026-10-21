import re
import uuid
import time
from typing import Dict, Tuple, List, Any

class ReversibleVault:
    """
    Enterprise De-identification & Re-identification Vault.
    Replaces sensitive personal and organizational data with structured surrogate tokens
    (@PSEUDO_ENTITY_ID) prior to LLM forwarding, and transparently decodes the surrogates
    when the AI completion returns.
    """
    def __init__(self, ttl_seconds: int = 3600):
        # In-memory session store (In production: backed by Redis Cluster)
        self.sessions: Dict[str, Dict[str, Any]] = {}
        self.ttl_seconds = ttl_seconds

    def cleanup_expired(self):
        now = time.time()
        expired = [sid for sid, data in self.sessions.items() if now - data["created_at"] > self.ttl_seconds]
        for sid in expired:
            del self.sessions[sid]

    def anonymize(self, text: str, findings: List[dict]) -> Tuple[str, str, Dict[str, str]]:
        """
        Replaces detected entities with reversible surrogate tokens.
        Returns:
            anonymized_text: Prompt with surrogates
            session_id: Unique reference to deanonymize the response
            surrogate_map: Dictionary of surrogate -> original value
        """
        self.cleanup_expired()
        session_id = f"vlt_{uuid.uuid4().hex[:12]}"
        
        # Sort findings in reverse order of appearance to preserve string offsets
        regex_findings = [f for f in findings if f.get("type") == "regex"]
        sorted_findings = sorted(regex_findings, key=lambda x: x["start"], reverse=True)

        surrogate_to_real: Dict[str, str] = {}
        real_to_surrogate: Dict[str, str] = {}
        entity_counters: Dict[str, int] = {}

        anonymized_text = text
        for finding in sorted_findings:
            label = finding["label"]
            original_val = finding["value"]
            start = finding["start"]
            end = finding["end"]

            # Reuse existing surrogate if the identical value occurred multiple times
            if original_val in real_to_surrogate:
                surrogate = real_to_surrogate[original_val]
            else:
                entity_counters[label] = entity_counters.get(label, 0) + 1
                surrogate = f"@PSEUDO_{label}_{entity_counters[label]}"
                real_to_surrogate[original_val] = surrogate
                surrogate_to_real[surrogate] = original_val

            anonymized_text = anonymized_text[:start] + surrogate + anonymized_text[end:]

        # Persist session mapping
        self.sessions[session_id] = {
            "created_at": time.time(),
            "mappings": surrogate_to_real
        }

        return anonymized_text, session_id, surrogate_to_real

    def deanonymize(self, text: str, session_id: str) -> str:
        """
        Restores original entities from surrogate tokens in the LLM response.
        """
        session = self.sessions.get(session_id)
        if not session:
            return text

        mappings = session.get("mappings", {})
        deanonymized_text = text

        for surrogate, original_val in mappings.items():
            deanonymized_text = deanonymized_text.replace(surrogate, original_val)

        return deanonymized_text

    def get_session_mappings(self, session_id: str) -> Dict[str, str]:
        return self.sessions.get(session_id, {}).get("mappings", {})

# Global vault instance
vault = ReversibleVault()
