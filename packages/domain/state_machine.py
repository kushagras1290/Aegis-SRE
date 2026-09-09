from packages.domain.models import Incident, IncidentStatus, IncidentTransition

class InvalidIncidentTransition(ValueError): pass

_ALLOWED: dict[IncidentStatus,set[IncidentStatus]]={
    IncidentStatus.DETECTED:{IncidentStatus.TRIAGED},
    IncidentStatus.TRIAGED:{IncidentStatus.INVESTIGATING},
    IncidentStatus.INVESTIGATING:{IncidentStatus.NEEDS_HUMAN,IncidentStatus.CAUSE_IDENTIFIED},
    IncidentStatus.NEEDS_HUMAN:{IncidentStatus.INVESTIGATING,IncidentStatus.CAUSE_IDENTIFIED},
    IncidentStatus.CAUSE_IDENTIFIED:{IncidentStatus.REMEDIATION_PROPOSED},
    IncidentStatus.REMEDIATION_PROPOSED:{IncidentStatus.AWAITING_APPROVAL},
    IncidentStatus.AWAITING_APPROVAL:{IncidentStatus.REJECTED,IncidentStatus.REMEDIATING},
    IncidentStatus.REMEDIATING:{IncidentStatus.REMEDIATION_FAILED,IncidentStatus.VERIFYING},
    IncidentStatus.REMEDIATION_FAILED:{IncidentStatus.AWAITING_APPROVAL,IncidentStatus.NEEDS_HUMAN},
    IncidentStatus.VERIFYING:{IncidentStatus.STILL_DEGRADED,IncidentStatus.RESOLVED},
    IncidentStatus.STILL_DEGRADED:{IncidentStatus.INVESTIGATING,IncidentStatus.AWAITING_APPROVAL},
    IncidentStatus.RESOLVED:{IncidentStatus.POSTMORTEM_COMPLETE},
    IncidentStatus.POSTMORTEM_COMPLETE:{IncidentStatus.CLOSED},
    IncidentStatus.REJECTED:{IncidentStatus.NEEDS_HUMAN},
    IncidentStatus.CLOSED:set(),
}

def transition(incident:Incident,target:IncidentStatus,*,actor:str,reason:str)->IncidentTransition:
    if target not in _ALLOWED[incident.status]:
        raise InvalidIncidentTransition(f'{incident.status} -> {target} is not allowed')
    previous=incident.status
    incident.status=target
    incident.version+=1
    return IncidentTransition(incident_id=incident.id,from_status=previous,to_status=target,actor=actor,reason=reason)
