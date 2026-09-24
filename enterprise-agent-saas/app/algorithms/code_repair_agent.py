class CodeRepairAgent:
    """Simple defensive sanitizer for suspicious code-like payloads."""

    blocked_tokens = ["__import__", "os.system", "subprocess", "eval(", "exec("]

    def sanitize(self, text: str) -> str:
        sanitized = text
        for token in self.blocked_tokens:
            sanitized = sanitized.replace(token, "[blocked]")
        return sanitized
