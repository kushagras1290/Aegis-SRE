import pytest
from packages.domain.models import Incident,IncidentStatus
from packages.domain.state_machine import InvalidIncidentTransition,transition
def incident(): return Incident(organization_id='org',environment='prod',title='checkout degraded')
def test_valid_transition():
 i=incident(); t=transition(i,IncidentStatus.TRIAGED,actor='u',reason='ack'); assert i.status==IncidentStatus.TRIAGED and i.version==1 and t.from_status==IncidentStatus.DETECTED
def test_invalid_transition():
 i=incident();
 with pytest.raises(InvalidIncidentTransition): transition(i,IncidentStatus.RESOLVED,actor='u',reason='nope')
@pytest.mark.parametrize('target',[IncidentStatus.RESOLVED,IncidentStatus.CLOSED,IncidentStatus.REMEDIATING,IncidentStatus.POSTMORTEM_COMPLETE])
def test_detected_cannot_skip(target):
 with pytest.raises(InvalidIncidentTransition): transition(incident(),target,actor='u',reason='x')
