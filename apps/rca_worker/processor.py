from __future__ import annotations

import networkx as nx

from packages.rca.graph import Candidate, rank_causes


def process_rca(
    graph: nx.DiGraph,
    affected: str,
    anomaly: dict[str, float],
    change: dict[str, float] | None = None,
) -> list[Candidate]:
    return rank_causes(graph, affected, anomaly, change)
