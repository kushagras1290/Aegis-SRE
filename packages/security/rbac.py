from enum import StrEnum
class Role(StrEnum): VIEWER='VIEWER'; ENGINEER='ENGINEER'; SRE='SRE'; INCIDENT_COMMANDER='INCIDENT_COMMANDER'; ADMIN='ADMIN'; SECURITY_AUDITOR='SECURITY_AUDITOR'
_PERMS={
 Role.VIEWER:{'incident:read','evidence:read'},
 Role.ENGINEER:{'incident:read','incident:update','evidence:read','remediation:propose'},
 Role.SRE:{'incident:read','incident:update','evidence:read','remediation:propose','remediation:approve'},
 Role.INCIDENT_COMMANDER:{'incident:read','incident:update','evidence:read','remediation:propose','remediation:approve','remediation:execute'},
 Role.ADMIN:{'*'},
 Role.SECURITY_AUDITOR:{'incident:read','audit:read','policy:read'},
}
def allowed(role:Role,permission:str)->bool: return '*' in _PERMS[role] or permission in _PERMS[role]
