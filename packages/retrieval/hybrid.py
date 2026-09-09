from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class RetrievalHit:
    document_id: str
    organization_id: str
    score: float


def reciprocal_rank_fusion(
    dense: list[RetrievalHit],
    sparse: list[RetrievalHit],
    *,
    organization_id: str,
    k: int = 60,
    limit: int = 10,
) -> list[RetrievalHit]:
    if limit < 1:
        raise ValueError("limit must be positive")
    scores: dict[str, float] = {}
    seen: dict[str, RetrievalHit] = {}
    for ranking in (dense, sparse):
        tenant_ranking = [hit for hit in ranking if hit.organization_id == organization_id]
        for rank, hit in enumerate(tenant_ranking, start=1):
            scores[hit.document_id] = scores.get(hit.document_id, 0.0) + 1.0 / (k + rank)
            seen[hit.document_id] = hit
    ordered = sorted(scores.items(), key=lambda item: item[1], reverse=True)[:limit]
    return [
        RetrievalHit(document_id, organization_id, score)
        for document_id, score in ordered
        if document_id in seen
    ]
