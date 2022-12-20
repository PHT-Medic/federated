import abc

import requests
import pendulum
# todo use httpx

from pht_federated.protocols.secure_aggregation.models import client_messages, server_messages


class ProtocolClient:
    def __init__(self, aggregator_url: str, auth_url: str = None, client_id: str = None, client_secret: str = None):
        self.client_secret = client_secret
        self.client_id = client_id
        self.token_url = auth_url
        self.aggregator_url = aggregator_url

        self.token = None
        self.token_expiration = None

        self._headers = None

        assert self.aggregator_url

    @property
    def headers(self) -> dict:
        token = self._get_token()
        if self._headers:
            return {**self._headers, "Authorization": f"Bearer {token}"}

        return {"Authorization": f"Bearer {token}"}



    def register(self, key_broadcast: client_messages.ClientKeyBroadCast, aggregation_id: str = None):
        pass




