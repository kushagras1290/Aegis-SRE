from concurrent.futures import ThreadPoolExecutor

from packages.remediation.executor import InMemoryActionAdapter, RemediationExecutor
from packages.remediation.models import ActionName, RemediationAction


def test_duplicate_execution_storm_produces_one_mutation() -> None:
    adapter = InMemoryActionAdapter()
    executor = RemediationExecutor(adapter, enabled=True)
    action = RemediationAction(
        action=ActionName.RESTART_POD,
        service="checkout",
        environment="production",
    )
    with ThreadPoolExecutor(max_workers=20) as pool:
        results = list(
            pool.map(
                lambda _: executor.execute(
                    action,
                    idempotency_key="same-key",
                    approved=True,
                ),
                range(100),
            )
        )
    assert adapter.mutations == 1
    assert all(result.status == "succeeded" for result in results)
