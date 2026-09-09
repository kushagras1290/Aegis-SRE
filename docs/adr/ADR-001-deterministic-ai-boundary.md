# ADR-001: Deterministic safety boundary

## Decision
AI components may analyse, rank, retrieve, summarise, and recommend. They never receive arbitrary mutation credentials or unrestricted shell/Kubernetes tools. Infrastructure mutation is performed only through a typed server-side action registry after deterministic authorization and policy evaluation.

## Consequences
LLM failure cannot disable incident detection or deterministic RCA. Prompt injection cannot directly grant infrastructure permissions.
