from __future__ import annotations

from dataclasses import dataclass, field

from packages.agents.tools import READ_ONLY_TOOLS


@dataclass(frozen=True, slots=True)
class IncidentContext:
    incident_id: str
    summary: str
    affected_services: tuple[str, ...]
    evidence_ids: tuple[str, ...] = field(default_factory=tuple)


class InvestigatorBoundary:
    """Deterministic capability boundary exposed to an AI investigator."""

    @property
    def allowed_tools(self) -> frozenset[str]:
        return READ_ONLY_TOOLS

    def assert_tool_allowed(self, tool_name: str) -> None:
        if tool_name not in READ_ONLY_TOOLS:
            raise PermissionError(f"tool is not available to investigator: {tool_name}")
