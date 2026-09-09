from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import networkx as nx

from packages.correlation.scoring import CorrelationContext, correlation_score
from packages.detection.robust import robust_zscore
from packages.rca.graph import rank_causes
from packages.remediation.executor import InMemoryActionAdapter, RemediationExecutor
from packages.remediation.models import ActionName, RemediationAction


def main() -> None:
    baseline = [0.30, 0.31, 0.29, 0.30, 0.32, 0.28, 0.31]
    anomaly = robust_zscore(baseline, 2.4)
    score = correlation_score(CorrelationContext(45, 1, True, True, 0.83))

    graph = nx.DiGraph()
    graph.add_edges_from(
        [
            ("postgres", "checkout"),
            ("checkout", "gateway"),
            ("redis", "checkout"),
        ]
    )
    ranked = rank_causes(
        graph,
        "gateway",
        {"postgres": 0.99, "checkout": 0.76, "redis": 0.10},
        {"checkout": 1.0, "postgres": 0.6},
    )

    adapter = InMemoryActionAdapter()
    executor = RemediationExecutor(adapter, enabled=True)
    action = RemediationAction(
        action=ActionName.ROLLBACK_DEPLOYMENT,
        service="checkout",
        environment="production",
        parameters={"to_version": "2.18.4"},
    )
    first = executor.execute(
        action,
        idempotency_key="INC-4821:plan-1:0",
        approved=True,
    )
    second = executor.execute(
        action,
        idempotency_key="INC-4821:plan-1:0",
        approved=True,
    )
    assert first == second
    assert adapter.mutations == 1

    print(
        f"anomaly={anomaly.anomalous} correlation={score:.3f} "
        f"root_cause={ranked[0].resource} remediation={first.status} "
        f"mutations={adapter.mutations}"
    )


if __name__ == "__main__":
    main()
