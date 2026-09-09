# Production mutation gate

Production remediation remains disabled until all items pass in staging:

- [ ] RBAC and tenant isolation tested
- [ ] OPA policy tests pass
- [ ] approval and two-person rules tested where required
- [ ] idempotency and reconciliation tested under retries
- [ ] audit completeness verified
- [ ] kill switch tested
- [ ] rollback tested
- [ ] backup restore exercise completed
- [ ] load and chaos tests completed
- [ ] Kubernetes least privilege and NetworkPolicy verified
