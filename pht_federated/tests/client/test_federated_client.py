import pytest

from pht_federated.client.federated_client import Client
def test_init():
    client = Client("http://localhost:8000")
    assert client.aggregator_url == "http://localhost:8000/api"

    client = Client("localhost:8000/api")
    assert client.aggregator_url == "http://localhost:8000/api"

    with pytest.raises(Exception):
        client = Client()

