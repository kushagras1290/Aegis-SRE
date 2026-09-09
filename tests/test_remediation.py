from concurrent.futures import ThreadPoolExecutor
import pytest
from packages.remediation.executor import ApprovalRequired,InMemoryActionAdapter,RemediationDisabled,RemediationExecutor
from packages.remediation.models import ActionName,RemediationAction
def action(env='production'): return RemediationAction(action=ActionName.ROLLBACK_DEPLOYMENT,service='checkout',environment=env)
def test_kill_switch():
 with pytest.raises(RemediationDisabled): RemediationExecutor(InMemoryActionAdapter()).execute(action(),idempotency_key='k',approved=True)
def test_prod_approval():
 with pytest.raises(ApprovalRequired): RemediationExecutor(InMemoryActionAdapter(),enabled=True).execute(action(),idempotency_key='k',approved=False)
def test_nonprod_can_run_without_approval(): assert RemediationExecutor(InMemoryActionAdapter(),enabled=True).execute(action('staging'),idempotency_key='k',approved=False).status=='succeeded'
def test_idempotent_concurrently():
 adapter=InMemoryActionAdapter(); ex=RemediationExecutor(adapter,enabled=True)
 with ThreadPoolExecutor(max_workers=16) as pool: results=list(pool.map(lambda _: ex.execute(action(),idempotency_key='same',approved=True),range(40)))
 assert adapter.mutations==1 and len({r.idempotency_key for r in results})==1
