from __future__ import annotations
from dataclasses import dataclass
from threading import Lock
from packages.remediation.models import RemediationAction
class RemediationDisabled(RuntimeError): pass
class ApprovalRequired(PermissionError): pass
@dataclass(frozen=True,slots=True)
class ExecutionResult:
    idempotency_key:str; status:str; mutation_count:int
class InMemoryActionAdapter:
    def __init__(self)->None: self.mutations=0
    def execute(self,action:RemediationAction)->None: self.mutations+=1
class RemediationExecutor:
    def __init__(self,adapter:InMemoryActionAdapter,*,enabled:bool=False)->None:
        self.adapter=adapter; self.enabled=enabled; self._done:dict[str,ExecutionResult]={}; self._lock=Lock()
    def execute(self,action:RemediationAction,*,idempotency_key:str,approved:bool)->ExecutionResult:
        if not self.enabled: raise RemediationDisabled('remediation kill switch is off')
        if action.environment=='production' and not approved: raise ApprovalRequired('production action requires approval')
        with self._lock:
            if idempotency_key in self._done: return self._done[idempotency_key]
            self.adapter.execute(action)
            result=ExecutionResult(idempotency_key,'succeeded',self.adapter.mutations)
            self._done[idempotency_key]=result
            return result
