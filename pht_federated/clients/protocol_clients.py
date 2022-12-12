import abc

import requests
import pendulum
# todo use httpx

from pht_federated.protocol.models import client_messages, server_messages


class ProtocolClient(abc.ABC):
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

    def _get_token(self):
        if not self.token or self.token_expiration < pendulum.now():
            if self.username and self.password:
                r = requests.post(self.auth_url, data={"username": self.username, "password": self.password})
            elif self.robot_id and self.robot_secret:

                r = requests.post(self.auth_url, data={"id": self.robot_id, "secret": self.robot_secret})
            else:
                raise Exception("No credentials provided")

            try:
                r.raise_for_status()
            except requests.exceptions.HTTPError as e:
                print(r.text)
                raise e
            r = r.json()
            self.token = r["access_token"]
            self.token_expiration = pendulum.now().add(seconds=r["expires_in"])

        return self.token


