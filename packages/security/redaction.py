import re
_PATTERNS=[
 re.compile(r'(?i)(authorization:\s*bearer\s+)[A-Za-z0-9._~+/-]+'),
 re.compile(r'(?i)(api[_-]?key[=: ]+)[A-Za-z0-9._-]{8,}'),
 re.compile(r'(?i)(password[=: ]+)[^\s,;]+'),
]
def redact(text:str)->str:
    for p in _PATTERNS: text=p.sub(lambda m:m.group(1)+'[REDACTED]',text)
    return text
