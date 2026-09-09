from packages.remediation.executor import ExecutionResult, RemediationExecutor
from packages.remediation.models import RemediationAction


def process_remediation(
    executor: RemediationExecutor,
    action: RemediationAction,
    *,
    idempotency_key: str,
    approved: bool,
) -> ExecutionResult:
    return executor.execute(
        action,
        idempotency_key=idempotency_key,
        approved=approved,
    )
