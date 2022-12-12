from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from pht_federated.aggregator.app import app
from pht_federated.aggregator.api.dependencies import get_db
from pht_federated.tests.aggregator.test_db import override_get_db

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


@pytest.fixture
def proposal_id():
    return str(uuid4())



def test_proposal_create(proposal_id):
    response = client.post("/api/proposal",
                           data={
                               "name": "Test Proposal",
                               "id": proposal_id,
                           }
                           )
    assert response.status_code == 200, response.text