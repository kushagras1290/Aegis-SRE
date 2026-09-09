import networkx as nx

from packages.correlation.scoring import CorrelationContext, correlation_score
from packages.detection.robust import robust_zscore
from packages.rca.graph import rank_causes
from packages.remediation.executor import InMemoryActionAdapter, RemediationExecutor
from packages.remediation.models import ActionName, RemediationAction


def test_flagship_failure_to_safe_remediation() -> None:
    anomaly = robust_zscore([0.28, 0.30, 0.31, 0.29, 0.30], 2.4)
    assert anomaly.anomalous
    assert correlation_score(CorrelationContext(30, 1, True, True, 0.8)) > 0.8

    graph = nx.DiGraph([("postgres", "checkout"), ("checkout", "gateway")])
    candidates = rank_causes(
        graph,
        "gateway",
        {"postgres": 0.99, "checkout": 0.6},
        {"postgres": 0.7, "checkout": 1.0},
    )
    assert candidates[0].resource == "postgres"

    adapter = InMemoryActionAdapter()
    executor = RemediationExecutor(adapter, enabled=True)
    action = RemediationAction(
        action=ActionName.ROLLBACK_DEPLOYMENT,
        service="checkout",
        environment="production",
    )
    result = executor.execute(
        action,
        idempotency_key="incident:plan:0",
        approved=True,
    )
    assert result.status == "succeeded"
    assert adapter.mutations == 1
