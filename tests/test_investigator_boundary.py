import pytest

from apps.ai_worker.investigator import InvestigatorBoundary


def test_investigator_has_only_read_tools() -> None:
    boundary = InvestigatorBoundary()
    assert "query_logs" in boundary.allowed_tools
    assert "rollback_deployment" not in boundary.allowed_tools
    with pytest.raises(PermissionError):
        boundary.assert_tool_allowed("rollback_deployment")
