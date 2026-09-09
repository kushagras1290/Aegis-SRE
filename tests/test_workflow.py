from apps.temporal_worker.workflows import IncidentWorkflowState, WorkflowStage, next_stage


def test_workflow_skips_ai_when_unavailable() -> None:
    state = IncidentWorkflowState("inc", WorkflowStage.DETERMINISTIC_RCA)
    assert next_stage(state, ai_available=False).stage == WorkflowStage.PLAN_REMEDIATION


def test_workflow_uses_ai_when_available() -> None:
    state = IncidentWorkflowState("inc", WorkflowStage.DETERMINISTIC_RCA)
    assert next_stage(state, ai_available=True).stage == WorkflowStage.AI_INVESTIGATION


def test_workflow_waits_without_approval() -> None:
    state = IncidentWorkflowState("inc", WorkflowStage.WAIT_FOR_APPROVAL, approved=False)
    assert next_stage(state, ai_available=True).stage == WorkflowStage.WAIT_FOR_APPROVAL


def test_workflow_executes_after_approval() -> None:
    state = IncidentWorkflowState("inc", WorkflowStage.WAIT_FOR_APPROVAL, approved=True)
    assert next_stage(state, ai_available=True).stage == WorkflowStage.EXECUTE_REMEDIATION
