from fastapi.testclient import TestClient

from apps.api.main import create_app
from packages.config import Settings


client = TestClient(create_app(Settings(env="test", incident_store="memory")))


def create(org: str = "o") -> dict[str, object]:
    response = client.post(
        "/api/v1/incidents",
        json={
            "organization_id": org,
            "environment": "production",
            "title": "checkout latency",
        },
    )
    assert response.status_code == 201
    return response.json()


def test_health() -> None:
    assert client.get("/health/live").json() == {"status": "ok"}


def test_create_get() -> None:
    incident = create()
    response = client.get(f"/api/v1/incidents/{incident['id']}?organization_id=o")
    assert response.status_code == 200


def test_tenant_isolation_404() -> None:
    incident = create("a")
    response = client.get(f"/api/v1/incidents/{incident['id']}?organization_id=b")
    assert response.status_code == 404


def test_invalid_transition_409() -> None:
    incident = create()
    response = client.post(
        f"/api/v1/incidents/{incident['id']}/transition?organization_id=o",
        json={"target": "RESOLVED", "actor": "u", "reason": "skip", "expected_version": 0},
    )
    assert response.status_code == 409


def test_valid_transition_and_timeline() -> None:
    incident = create()
    response = client.post(
        f"/api/v1/incidents/{incident['id']}/transition?organization_id=o",
        json={"target": "TRIAGED", "actor": "u", "reason": "ack", "expected_version": 0},
    )
    assert response.status_code == 200
    assert response.json()["version"] == 1
    timeline = client.get(f"/api/v1/incidents/{incident['id']}/timeline?organization_id=o")
    assert timeline.status_code == 200
    assert timeline.json()[0]["to_status"] == "TRIAGED"


def test_stale_version_conflicts() -> None:
    incident = create()
    first = client.post(
        f"/api/v1/incidents/{incident['id']}/transition?organization_id=o",
        json={"target": "TRIAGED", "actor": "u", "reason": "ack", "expected_version": 0},
    )
    assert first.status_code == 200
    second = client.post(
        f"/api/v1/incidents/{incident['id']}/transition?organization_id=o",
        json={"target": "INVESTIGATING", "actor": "u", "reason": "start", "expected_version": 0},
    )
    assert second.status_code == 409


def test_list_is_bounded_and_cursor_paginated() -> None:
    for _ in range(3):
        create("page-org")
    first = client.get("/api/v1/incidents?organization_id=page-org&limit=2")
    assert first.status_code == 200
    body = first.json()
    assert len(body["items"]) == 2
    assert body["next_cursor"] is not None
    second = client.get("/api/v1/incidents", params={"organization_id": "page-org", "limit": 2, "cursor": body["next_cursor"]})
    assert second.status_code == 200
    assert len(second.json()["items"]) == 1
