# flake8: noqa
import time
import uuid

import pytest
from fastapi.testclient import TestClient

from pht_federated.aggregator.api.dependencies import get_db
from pht_federated.aggregator.app import app
from pht_federated.protocols.secure_aggregation.client.client_protocol import (
    ClientProtocol,
)
from pht_federated.tests.aggregator.test_db import override_get_db

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


def setup_protocol_with_registration():
    # create a protocol
    data = {"name": "Test Protocol"}
    response = client.post("/api/protocol", json=data)
    assert response.status_code == 200, response.text

    protocol_id = response.json()["id"]

    client_protocol = ClientProtocol()

    client_keys = []

    for _ in range(5):
        keys, broadcast = client_protocol.setup()
        client_keys.append(keys)
        response = client.post(
            f"/api/protocol/{protocol_id}/register", json=broadcast.dict()
        )
        assert response.status_code == 200, response.text

    return protocol_id, client_keys


@pytest.fixture
def proposal_id():
    response = client.post("/api/proposal", json={"name": "Protocol test"})
    return response.json()["id"]


@pytest.fixture
def discovery_id(proposal_id):
    response = client.post(
        f"/api/proposal/{proposal_id}/discoveries",
        json={"query": {"name": "Test Discovery"}},
    )
    return response.json()["id"]


def test_create_protocol(proposal_id, discovery_id):
    # create a protocol
    data = {"name": "Test Protocol"}
    response = client.post("/api/protocol", json=data)
    assert response.status_code == 200, response.text

    # create a protocol with a proposal id
    data = {"name": "Test Protocol Proposal", "proposal_id": proposal_id}
    response = client.post("/api/protocol", json=data)
    assert response.status_code == 200, response.text
    assert response.json()["proposal_id"] == proposal_id

    # create a protocol with a discovery id
    data = {"name": "Test Protocol Discovery", "discovery_id": discovery_id}
    response = client.post("/api/protocol", json=data)
    assert response.status_code == 200, response.text
    assert response.json()["discovery_id"] == discovery_id

    # create a protocol with invalid proposal id
    data = {"name": "Test Protocol Proposal", "proposal_id": str(uuid.uuid4())}
    response = client.post("/api/protocol", json=data)
    assert response.status_code == 404, response.text

    # create a protocol with invalid discovery id
    data = {"name": "Test Protocol Discovery", "discovery_id": 999999}
    response = client.post("/api/protocol", json=data)
    assert response.status_code == 404, response.text


def test_get_many_protocols(proposal_id, discovery_id):
    # create a protocol
    data = {"name": "Test Protocol"}
    response = client.post("/api/protocol", json=data)
    assert response.status_code == 200, response.text

    # create a protocol with a proposal id
    data = {"name": "Test Protocol Proposal", "proposal_id": proposal_id}
    response = client.post("/api/protocol", json=data)
    assert response.status_code == 200, response.text
    assert response.json()["proposal_id"] == proposal_id

    # create a second protocol with a proposal id
    data = {"name": "Test Protocol Proposal 2", "proposal_id": proposal_id}
    response = client.post("/api/protocol", json=data)
    assert response.status_code == 200, response.text
    assert response.json()["proposal_id"] == proposal_id

    # create a protocol with a discovery id
    data = {"name": "Test Protocol Discovery", "discovery_id": discovery_id}
    response = client.post("/api/protocol", json=data)
    assert response.status_code == 200, response.text
    assert response.json()["discovery_id"] == discovery_id

    # get all protocols
    response = client.get("/api/protocol")
    assert response.status_code == 200, response.text
    assert len(response.json()) >= 3

    # get all protocols for a proposal
    response = client.get(f"/api/protocol", params={"proposal_id": proposal_id})
    assert response.status_code == 200, response.text
    assert len(response.json()) >= 2

    # get all protocols for a discovery
    response = client.get(f"/api/protocol", params={"discovery_id": discovery_id})
    assert response.status_code == 200, response.text
    assert len(response.json()) >= 1

    # invalid discovery
    response = client.get(f"/api/protocol", params={"discovery_id": 999999})
    assert response.status_code == 404, response.text

    # invalid proposal
    response = client.get(f"/api/protocol", params={"proposal_id": str(uuid.uuid4())})
    assert response.status_code == 404, response.text


def test_get_one_protocol():
    # create a protocol
    data = {"name": "Test Protocol"}
    response = client.post("/api/protocol", json=data)
    assert response.status_code == 200, response.text
    protocol_id = response.json()["id"]

    # get the protocol
    response = client.get(f"/api/protocol/{protocol_id}")
    assert response.status_code == 200, response.text
    assert response.json()["id"] == protocol_id

    # invalid protocol
    response = client.get(f"/api/protocol/{uuid.uuid4()}")
    assert response.status_code == 404, response.text


def test_update_protocol(proposal_id, discovery_id):
    data = {"name": "Test Protocol"}
    response = client.post("/api/protocol", json=data)
    assert response.status_code == 200, response.text

    protocol_id = response.json()["id"]

    # update the protocol

    data = {"name": "Test Protocol Updated"}
    response = client.put(f"/api/protocol/{protocol_id}", json=data)
    assert response.status_code == 200, response.text
    assert response.json()["name"] == "Test Protocol Updated"

    # update the protocol with a proposal id
    data = {"name": "Test Protocol Updated", "proposal_id": proposal_id}
    response = client.put(f"/api/protocol/{protocol_id}", json=data)
    assert response.status_code == 200, response.text
    assert response.json()["proposal_id"] == proposal_id

    # update the protocol with a discovery id
    data = {"name": "Test Protocol Updated", "discovery_id": discovery_id}
    response = client.put(f"/api/protocol/{protocol_id}", json=data)
    assert response.status_code == 200, response.text
    assert response.json()["discovery_id"] == discovery_id

    # invalid protocol
    data = {"name": "Test Protocol Updated"}
    response = client.put(f"/api/protocol/{uuid.uuid4()}", json=data)
    assert response.status_code == 404, response.text

    # invalid proposal
    data = {"name": "Test Protocol Updated", "proposal_id": str(uuid.uuid4())}
    response = client.put(f"/api/protocol/{protocol_id}", json=data)
    assert response.status_code == 404, response.text

    # invalid discovery
    data = {"name": "Test Protocol Updated", "discovery_id": 999999}
    response = client.put(f"/api/protocol/{protocol_id}", json=data)
    assert response.status_code == 404, response.text


def test_protocol_delete():
    # create a protocol
    data = {"name": "Test Protocol"}
    response = client.post("/api/protocol", json=data)
    assert response.status_code == 200, response.text

    protocol_id = response.json()["id"]

    # delete the protocol
    response = client.delete(f"/api/protocol/{protocol_id}")
    assert response.status_code == 200, response.text

    # invalid protocol
    response = client.delete(f"/api/protocol/{uuid.uuid4()}")
    assert response.status_code == 404, response.text


def test_register_for_protocol():
    # create a protocol
    data = {"name": "Test Protocol"}
    response = client.post("/api/protocol", json=data)
    assert response.status_code == 200, response.text

    protocol_id = response.json()["id"]

    client_protocol = ClientProtocol()
    keys, broadcast = client_protocol.setup()

    # register for the protocol
    response = client.post(
        f"/api/protocol/{protocol_id}/register", json=broadcast.dict()
    )
    print(response.text)
    assert response.status_code == 200, response.text

    # invalid protocol
    response = client.post(
        f"/api/protocol/{uuid.uuid4()}/register", json=broadcast.dict()
    )
    assert response.status_code == 404, response.text

    keys_2, broadcast_2 = client_protocol.setup()
    response = client.post(
        f"/api/protocol/{protocol_id}/register", json=broadcast_2.dict()
    )
    assert response.status_code == 200, response.text

    assert response.json()["currently_registered"] == 2


def test_get_protocol_settings():
    # create a protocol
    data = {"name": "Test Protocol"}
    response = client.post("/api/protocol", json=data)
    assert response.status_code == 200, response.text

    protocol_id = response.json()["id"]

    # get the protocol settings
    response = client.get(f"/api/protocol/{protocol_id}/settings")
    assert response.status_code == 200, response.text
    print(response.json())

    # invalid protocol
    response = client.get(f"/api/protocol/{uuid.uuid4()}/settings")
    assert response.status_code == 404, response.text


def test_update_protocol_settings():
    # create a protocol
    data = {"name": "Test Protocol"}
    response = client.post("/api/protocol", json=data)
    assert response.status_code == 200, response.text

    protocol_id = response.json()["id"]

    # update the protocol settings
    data = {"min_participants": 5}
    response = client.put(f"/api/protocol/{protocol_id}/settings", json=data)
    assert response.status_code == 200, response.text
    assert response.json()["min_participants"] == 5

    # invalid protocol
    data = {"name": "Test Protocol Updated"}
    response = client.put(f"/api/protocol/{uuid.uuid4()}/settings", json=data)
    assert response.status_code == 404, response.text


def test_protocol_advance():
    # create a protocol
    data = {"name": "Test Advance Protocol"}
    response = client.post("/api/protocol", json=data)
    assert response.status_code == 200, response.text

    protocol_id = response.json()["id"]

    # error not enough participants
    response = client.post(f"/api/protocol/{protocol_id}/advance")
    assert response.status_code == 400, response.text

    # invalid protocol
    response = client.post(f"/api/protocol/{uuid.uuid4()}/advance")
    assert response.status_code == 404, response.text

    client_protocol = ClientProtocol()
    keys, broadcast = client_protocol.setup()
    response = client.post(
        f"/api/protocol/{protocol_id}/register", json=broadcast.dict()
    )
    assert response.status_code == 200, response.text

    # error not enough participants
    response = client.post(f"/api/protocol/{protocol_id}/advance")
    assert response.status_code == 400, response.text

    for _ in range(4):
        keys, broadcast = client_protocol.setup()
        response = client.post(
            f"/api/protocol/{protocol_id}/register", json=broadcast.dict()
        )
        assert response.status_code == 200, response.text

    response = client.post(f"/api/protocol/{protocol_id}/advance")
    assert response.status_code == 200, response.text
    assert response.json()["round_status"]["step"] == 1

    keys, broadcast = client_protocol.setup()

    response = client.post(
        f"/api/protocol/{protocol_id}/register", json=broadcast.dict()
    )
    print(response.text)


def test_protocol_auto_advance():
    # create a protocol
    data = {"name": "Test Auto Advance Protocol"}
    response = client.post("/api/protocol", json=data)
    assert response.status_code == 200, response.text

    protocol_id = response.json()["id"]

    # set  auto advance
    data = {"auto_advance": True}
    response = client.put(f"/api/protocol/{protocol_id}/settings", json=data)
    assert response.status_code == 200, response.text
    assert response.json()["auto_advance"] == True

    client_protocol = ClientProtocol()

    for _ in range(6):
        keys, broadcast = client_protocol.setup()
        response = client.post(
            f"/api/protocol/{protocol_id}/register", json=broadcast.dict()
        )
        assert response.status_code == 200, response.text

    status = client.get(f"/api/protocol/{protocol_id}/status").json()
    assert status["round_status"]["step"] == 1
    print(status)


def test_get_protocol_status():
    data = {"name": "Test Protocol"}
    response = client.post("/api/protocol", json=data)
    assert response.status_code == 200, response.text

    protocol_id = response.json()["id"]

    client_protocol = ClientProtocol()
    keys, broadcast = client_protocol.setup()
    response = client.post(
        f"/api/protocol/{protocol_id}/register", json=broadcast.dict()
    )
    assert response.status_code == 200, response.text

    response = client.get(f"/api/protocol/{protocol_id}/status")
    assert response.status_code == 200, response.text

    # invalid protocol
    response = client.get(f"/api/protocol/{uuid.uuid4()}/status")
    assert response.status_code == 404, response.text


def test_share_keys():
    protocol_id, client_keys = setup_protocol_with_registration()

    # advance to the next round
    response = client.post(f"/api/protocol/{protocol_id}/advance")

    client_protocol = ClientProtocol()

    key_broadcast = client.get(f"/api/protocol/{protocol_id}/keyBroadcasts").json()

    client_id = "user-1"
    seed, key_shares = client_protocol.process_key_broadcast(
        client_id, client_keys[0], key_broadcast, 3
    )

    # share keys
    response = client.post(
        f"/api/protocol/{protocol_id}/shareKeys", json=key_shares.dict()
    )
