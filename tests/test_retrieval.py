import pytest

from packages.retrieval.hybrid import RetrievalHit, reciprocal_rank_fusion


def test_rrf_fuses_and_filters_tenant() -> None:
    dense = [
        RetrievalHit("a", "org", 0.9),
        RetrievalHit("secret", "other", 1.0),
        RetrievalHit("b", "org", 0.8),
    ]
    sparse = [RetrievalHit("b", "org", 12), RetrievalHit("a", "org", 10)]
    result = reciprocal_rank_fusion(dense, sparse, organization_id="org")
    assert {item.document_id for item in result} == {"a", "b"}
    assert all(item.organization_id == "org" for item in result)


def test_rrf_rejects_zero_limit() -> None:
    with pytest.raises(ValueError):
        reciprocal_rank_fusion([], [], organization_id="org", limit=0)
