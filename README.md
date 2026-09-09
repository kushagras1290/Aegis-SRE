# Aegis SRE

Aegis SRE is an AI-native incident response platform for **telemetry ingestion, anomaly detection, incident correlation, deterministic root-cause analysis, evidence-grounded AI investigation, policy-gated remediation, recovery verification, and postmortems**.

The core safety rule is simple: **probabilistic AI can analyse and recommend; deterministic code owns authorization, policy, workflow invariants, idempotency, and infrastructure mutation.**

## Current implementation

This repository implements the production architecture baseline as a working monorepo with:

- typed incident domain model and deterministic state machine
- versioned event envelopes
- MAD/robust-z, EWMA, and CUSUM detection primitives
- incident correlation scoring
- NetworkX topology and RCA scoring
- read-only AI investigation tool registry
- RBAC, redaction, and remediation kill switch
- typed remediation registry, approvals, and concurrency-safe idempotent executor
- transaction-bound at-least-once event consumer semantics
- provider-failover model gateway with redaction and budgets
- tenant-scoped hybrid retrieval/RRF primitives
- SQL-backed incident persistence with immutable transition timeline
- FastAPI incident API with optimistic concurrency and cursor pagination
- Redpanda/OTel/Temporal/Qdrant/ClickHouse/Postgres/Redis/MinIO local infrastructure definitions
- OPA remediation policy and tests
- protobuf telemetry/anomaly contracts
- synthetic flagship incident simulator
- Next.js operator UI skeleton
- CI, static security checks, container build, Helm, and Terraform foundations

External-service adapters are intentionally split from deterministic business logic so detection and RCA remain available during AI-provider failures.

## Architecture

```text
OTel -> Redpanda -> detector -> correlator -> incident
                                   |
                                   v
                          deterministic RCA
                                   |
                                   v
                             Temporal workflow
                            /                 \
                    AI investigator       planner
                         read-only            |
                              \               v
                               -----> OPA policy
                                          |
                                      approval gate
                                          |
                                          v
                                 typed executor
                                          |
                                      verifier
```

## Repository layout

```text
apps/
  api/
  web/
  telemetry_ingestor/
  detector_worker/
  correlator_worker/
  rca_worker/
  temporal_worker/
  ai_worker/
  remediation_worker/
packages/
  domain/
  contracts/
  db/
  detection/
  correlation/
  rca/
  agents/
  security/
  remediation/
  observability/
  retrieval/
schemas/protobuf/
infra/{docker,otel,redpanda,grafana,prometheus,opa,kubernetes,helm,terraform}/
tests/ + tests/{contract,e2e,load,chaos}/
```

## Prerequisites

- Python 3.14.x
- Node.js 22+
- `pnpm` 10+
- Docker Engine + Compose v2 for integration infrastructure
- optional: `opa`, `kubectl`, `helm`, `terraform`

## Bootstrap

```bash
make bootstrap
cp .env.example .env
make test
```

For full local infrastructure:

```bash
make infra-up
make migrate
make dev-api
```

Web UI:

```bash
pnpm --dir apps/web install --no-frozen-lockfile
pnpm --dir apps/web dev
```

## Verification

Fast checks:

```bash
make verify
```

Full environment checks:

```bash
make verify-full
```

The full gate includes unit/contract/E2E tests, OPA tests, frontend type/build checks, security scanners, image builds, and integration tests against real dependencies.

## Production safety defaults

- `AEGIS_AUTOREMEDIATION_ENABLED=false` by default.
- production write operations require deterministic policy approval.
- the AI investigator has no mutation tools.
- unsupported actions are rejected by the action registry.
- shell execution, secret mutation, and namespace deletion are prohibited actions.
- event consumers are designed for at-least-once delivery with durable idempotency records.
- tenant identifiers are server-validated and included in storage/query contracts.
- secrets are not committed; production deployments should use workload identity + a secrets manager.

## Local infrastructure

`docker-compose.yml` starts:

- PostgreSQL
- Redis
- Redpanda
- ClickHouse
- Qdrant
- Temporal
- OpenTelemetry Collector
- Prometheus
- Grafana
- MinIO
- OPA

## Demo scenario

```bash
make demo
```

The simulator models a checkout deployment that causes PostgreSQL connection pressure, then exercises detection, correlation, RCA ranking, policy-gated rollback, idempotency, and verification.

## Status

The repository is designed as a production-grade implementation baseline. Real production mutation must remain disabled until the production gate in `docs/operations/production-gate.md` is completed against a staging cluster with real external services and restore/chaos tests.
