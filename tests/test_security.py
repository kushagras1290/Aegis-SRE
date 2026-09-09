from packages.security.redaction import redact
from packages.security.rbac import Role,allowed
def test_redacts_bearer(): assert 'secret-token' not in redact('Authorization: Bearer secret-token')
def test_redacts_password(): assert '[REDACTED]' in redact('password=hunter2')
def test_viewer_cannot_approve(): assert not allowed(Role.VIEWER,'remediation:approve')
def test_commander_executes(): assert allowed(Role.INCIDENT_COMMANDER,'remediation:execute')
def test_admin_all(): assert allowed(Role.ADMIN,'anything:at-all')
