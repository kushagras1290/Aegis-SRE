"""Temporal boundary contract.

The actual Temporal SDK wiring is optional in local/unit environments. Workflow code must remain
pure and deterministic; all network, storage, LLM, and infrastructure operations belong in
activities.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class WorkflowStage(StrEnum):
    COLLECT_EVIDENCE = "collect_evidence"
    DETERMINISTIC_RCA = "deterministic_rca"
    AI_INVESTIGATION = "ai_investigation"
    PLAN_REMEDIATION = "plan_remediation"
    WAIT_FOR_APPROVAL = "wait_for_approval"
    EXECUTE_REMEDIATION = "execute_remediation"
    VERIFY_RECOVERY = "verify_recovery"
    CLOSE_INCIDENT = "close_incident"


@dataclass(frozen=True, slots=True)
class IncidentWorkflowState:
    incident_id: str
    stage: WorkflowStage = WorkflowStage.COLLECT_EVIDENCE
    approved: bool = False


def next_stage(state: IncidentWorkflowState, *, ai_available: bool) -> IncidentWorkflowState:
    transition = {
        WorkflowStage.COLLECT_EVIDENCE: WorkflowStage.DETERMINISTIC_RCA,
        WorkflowStage.DETERMINISTIC_RCA: (
            WorkflowStage.AI_INVESTIGATION
            if ai_available
            else WorkflowStage.PLAN_REMEDIATION
        ),
        WorkflowStage.AI_INVESTIGATION: WorkflowStage.PLAN_REMEDIATION,
        WorkflowStage.PLAN_REMEDIATION: WorkflowStage.WAIT_FOR_APPROVAL,
        WorkflowStage.WAIT_FOR_APPROVAL: (
            WorkflowStage.EXECUTE_REMEDIATION if state.approved else WorkflowStage.WAIT_FOR_APPROVAL
        ),
        WorkflowStage.EXECUTE_REMEDIATION: WorkflowStage.VERIFY_RECOVERY,
        WorkflowStage.VERIFY_RECOVERY: WorkflowStage.CLOSE_INCIDENT,
        WorkflowStage.CLOSE_INCIDENT: WorkflowStage.CLOSE_INCIDENT,
    }
    return IncidentWorkflowState(state.incident_id, transition[state.stage], state.approved)
