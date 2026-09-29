import re
INJECTION_PATTERNS=[r"ignore.*previous",r"disregard.*system",r"reveal.*prompt",r"you are now",r"jailbreak",r"system prompt",r"override"]
def check_injection(text):
    tl=text.lower()
    for pat in INJECTION_PATTERNS:
        if re.search(pat,tl):
            return True,0.95,pat
    return False,0.0,"Clean"
def get_blocked_message():
    return {"title":"PROMPT INJECTION BLOCKED 🛡️ PECA-Guard AI Firewall","message":"Security Violation Detected. Your input contained instructions attempting to override system behavior. Please submit valid PECA query.","code":"SEC-001-PECA-GUARD"}
