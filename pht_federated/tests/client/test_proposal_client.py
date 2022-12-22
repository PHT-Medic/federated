# flake8: noqa

import uuid

import pytest
from fastapi.testclient import TestClient

from pht_federated.aggregator.api.dependencies import get_db
from pht_federated.aggregator.app import app
from pht_federated.aggregator.schemas.proposal import (Proposal,
                                                       ProposalCreate,
                                                       ProposalUpdate)
from pht_federated.client.resources import ProposalClient
from pht_federated.tests.aggregator.test_db import override_get_db

app.dependency_overrides[get_db] = override_get_db

api_client = TestClient(app)


@pytest.fixture
def proposal_client():

    client = ProposalClient(api_client, schema=Proposal, prefix="/api/proposal")
    assert client is not None
    return client


def test_create(proposal_client):

    create_id = uuid.uuid4()
    create_msg = ProposalCreate(name="Test Proposal", id=create_id)
    proposal = proposal_client.create(create_msg)

    assert proposal.id == create_id
    assert proposal.name == "Test Proposal"


def test_get(proposal_client):

    create_id = uuid.uuid4()
    create_msg = ProposalCreate(name="Test Proposal", id=create_id)
    proposal = proposal_client.create(create_msg)

    proposal = proposal_client.get(create_id)
    assert proposal.id == create_id
    assert proposal.name == "Test Proposal"


def test_get_multi(proposal_client):
    create_id = uuid.uuid4()
    create_msg = ProposalCreate(name="Test Proposal", id=create_id)
    proposal = proposal_client.create(create_msg)

    proposals = proposal_client.get_multi()
    assert len(proposals) >= 1


def test_update(proposal_client):
    create_id = uuid.uuid4()
    create_msg = ProposalCreate(name="Test Proposal", id=create_id)
    proposal = proposal_client.create(create_msg)

    proposal = proposal_client.update(create_id, ProposalUpdate(name="New Name"))
    assert proposal.id == create_id
    assert proposal.name == "New Name"


def test_delete(proposal_client):
    create_id = uuid.uuid4()
    create_msg = ProposalCreate(name="Test Proposal", id=create_id)
    proposal = proposal_client.create(create_msg)

    proposal = proposal_client.delete(create_id)
    assert proposal.id == create_id
    assert proposal.name == "Test Proposal"

    with pytest.raises(Exception):
        proposal = proposal_client.get(create_id)
