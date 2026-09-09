import networkx as nx

from packages.agents.model_gateway import ModelGateway
from packages.detection.robust import robust_zscore
from packages.rca.graph import rank_causes


class FailedProvider:
    def complete(self, prompt: str) -> str:
        raise TimeoutError("provider unavailable")


def test_llm_outage_does_not_disable_detection_or_deterministic_rca() -> None:
    try:
        ModelGateway([FailedProvider()]).complete("investigate")
    except RuntimeError:
        pass
    else:
        raise AssertionError("model gateway should fail after all providers fail")

    assert robust_zscore([1.0, 1.1, 0.9, 1.0], 4.0).anomalous
    graph = nx.DiGraph([("db", "api")])
    assert rank_causes(graph, "api", {"db": 1.0})[0].resource == "db"
