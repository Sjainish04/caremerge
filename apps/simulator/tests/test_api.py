"""HTTP tests for the simulator API: guards, turns, confirmations, inbox, reminders."""

import pytest
from fastapi.testclient import TestClient

from caremerge_simulator.api.routes import create_app
from caremerge_simulator.api.security import TOKEN_HEADER
from caremerge_simulator.host import SimulatorHost
from caremerge_simulator.settings import SimulatorSettings

TOKEN = "test-token"
BASE = "http://127.0.0.1:8765"
QUESTION = "When should the temporary hold of Medication A for the procedure end?"


@pytest.fixture
def client(host: SimulatorHost, settings: SimulatorSettings) -> TestClient:
    return TestClient(create_app(host, settings, token=TOKEN), base_url=BASE)


@pytest.fixture
def auth() -> dict[str, str]:
    return {TOKEN_HEADER: TOKEN}


def test_session_token_is_served_without_a_token(client: TestClient) -> None:
    assert client.get("/api/session").json() == {"token": TOKEN}


def test_private_routes_need_the_token(client: TestClient, auth: dict[str, str]) -> None:
    assert client.get("/api/health").status_code == 401
    assert client.get("/api/health", headers={TOKEN_HEADER: "wrong"}).status_code == 401
    health = client.get("/api/health", headers=auth).json()
    assert health == {"addon_reachable": True, "model_tools": 5, "orchestrator": "keyword"}


def test_foreign_origins_and_hosts_are_refused(client: TestClient, auth: dict[str, str]) -> None:
    evil = {**auth, "Origin": "https://evil.example"}
    assert client.get("/api/session", headers={"Origin": "https://evil.example"}).status_code == 403
    assert client.get("/api/health", headers=evil).status_code == 403
    assert client.get("/api/health", headers={**auth, "Origin": BASE}).status_code == 200
    rebinding = TestClient(client.app, base_url="http://attacker.example")
    assert rebinding.get("/api/session").status_code == 400


def test_dev_origin_is_allowed_only_when_configured(
    host: SimulatorHost, settings: SimulatorSettings, auth: dict[str, str]
) -> None:
    dev = settings.model_copy(update={"dev_origins": ("http://localhost:5173",)})
    dev_client = TestClient(create_app(host, dev, token=TOKEN), base_url=BASE)
    headers = {**auth, "Origin": "http://localhost:5173"}
    assert dev_client.get("/api/health", headers=headers).status_code == 200


def test_the_demo_flow_over_http(client: TestClient, auth: dict[str, str]) -> None:
    inbox = client.get("/api/inbox", headers=auth).json()
    assert [v["visit_id"] for v in inbox["visits"]] == ["visit-1", "visit-2", "visit-3"]
    arrived = client.post("/api/inbox/visit-2", headers=auth).json()
    assert arrived["speech"].endswith("is ready to review.")
    assert arrived["card"]["tool"] == "add_visit"
    said = {"text": "What's new from my visit with Dr. Lee?"}
    updates = client.post("/api/turn", json=said, headers=auth).json()
    assert updates["card"]["tool"] == "visit_updates"
    assert [i["summary"] for i in updates["card"]["data"]["items"]] == [
        "your procedure on Wednesday, October 28",
        "a hold on Medication A starting Sunday, October 25",
    ]
    pending = updates["pending"]
    confirmed = client.post(
        f"/api/confirmations/{pending['pending_id']}", json={"answer": "yes"}, headers=auth
    ).json()
    assert confirmed["speech"] == "Added to your care plan."
    proposal = client.post(
        "/api/turn", json={"text": "Remind me to ask when the hold ends."}, headers=auth
    ).json()
    assert proposal["card"]["data"]["reminder"]["text"] == f"Ask your care team: {QUESTION}"
    stored = client.post("/api/turn", json={"text": "Yes."}, headers=auth).json()
    assert stored["speech"] == "Done. It's in your reminders."
    reminders = client.get("/api/reminders", headers=auth).json()
    assert [r["text"] for r in reminders["reminders"]] == [f"Ask your care team: {QUESTION}"]


def test_bad_requests_are_refused(client: TestClient, auth: dict[str, str]) -> None:
    assert client.post("/api/turn", json={"text": ""}, headers=auth).status_code == 422
    unknown = client.post("/api/confirmations/pend_404", json={"answer": "yes"}, headers=auth)
    assert unknown.status_code == 409
    missing = client.post("/api/inbox/visit-9", headers=auth).json()
    assert (missing["speech"], missing["error"]) == (
        "I couldn't find that in your care plan.",
        True,
    )


def test_delete_data_empties_the_ledger(client: TestClient, auth: dict[str, str]) -> None:
    client.post("/api/inbox/visit-1", headers=auth)
    deleted = client.delete("/api/data", headers=auth).json()
    assert deleted["speech"] == "Your CareMerge data is deleted."
    assert [v["added"] for v in client.get("/api/inbox", headers=auth).json()["visits"]] == [
        False,
        False,
        False,
    ]


def test_openapi_document_types_the_cards(client: TestClient) -> None:
    document = client.get("/openapi.json").json()
    assert {"/api/session", "/api/turn", "/api/confirmations/{pending_id}"} <= set(
        document["paths"]
    )
    assert "VisitUpdatesCard" in document["components"]["schemas"]
