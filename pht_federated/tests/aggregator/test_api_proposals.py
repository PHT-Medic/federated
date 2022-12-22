from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from pht_federated.aggregator.api.dependencies import get_db
from pht_federated.aggregator.app import app
from pht_federated.tests.aggregator.test_db import override_get_db

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


@pytest.fixture
def proposal_id():
    return str(uuid4())


def test_proposal_create(proposal_id):

    data = {"id": proposal_id, "name": "Test Proposal"}
    print("data: {}".format(data))
    response = client.post("/api/proposal", json=data)
    assert response.status_code == 200, response.text

    # duplicate id should fail
    response = client.post("/api/proposal", json=data)
    print("response: {}".format(data))
    assert response.status_code == 400, response.text


def test_get_many_proposals(proposal_id):
    data = {"id": proposal_id, "name": "Test Proposal"}
    response = client.post("/api/proposal", json=data)

    response = client.get("/api/proposal")
    assert response.status_code == 200, response.text
    assert len(response.json()) >= 1


def test_get_one_proposal(proposal_id):
    data = {"id": proposal_id, "name": "Test Proposal"}
    response = client.post("/api/proposal", json=data)

    response = client.get(f"/api/proposal/{proposal_id}")
    assert response.status_code == 200, response.text
    assert response.json()["id"] == proposal_id

    # non-existent id should fail
    response = client.get(f"/api/proposal/{str(uuid4())}")
    assert response.status_code == 404, response.text


def test_proposal_update(proposal_id):
    data = {"id": proposal_id, "name": "Test Proposal"}
    response = client.post("/api/proposal", json=data)

    response = client.put(
        f"/api/proposal/{proposal_id}", json={"name": "Updated Proposal"}
    )
    assert response.status_code == 200, response.text

    response = client.get(f"/api/proposal/{proposal_id}")
    assert response.status_code == 200, response.text
    assert response.json()["name"] == "Updated Proposal"

    # test update with non-existent id
    response = client.put(
        f"/api/proposal/{str(uuid4())}", json={"name": "Updated Proposal"}
    )
    assert response.status_code == 404, response.text


def test_proposal_delete(proposal_id):
    data = {"id": proposal_id, "name": "Test Proposal"}
    response = client.post("/api/proposal", json=data)

    response = client.delete(f"/api/proposal/{proposal_id}")
    assert response.status_code == 200, response.text

    # test delete with non-existent id
    response = client.delete(f"/api/proposal/{str(uuid4())}")
    assert response.status_code == 404, response.text
