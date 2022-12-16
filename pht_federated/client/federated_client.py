import httpx
import pendulum
import warnings

from pht_federated.client.discovery_client import DiscoveryClient
from pht_federated.client.protocol_clients import ProtocolClient
from pht_federated.client.resources.proposal import ProposalClient


class Client:
    proposals: ProposalClient
    discoveries: DiscoveryClient
    protocols: ProtocolClient

    def __init__(
            self,
            aggregator_url: str,
            token_url: str = None,
            username: str = None,
            password: str = None,
            robot_id: str = None,
            robot_secret: str = None,
            headers: dict = None,
            client: httpx.Client = None,
    ):

        self.aggregator_url = self._check_add_http_https(aggregator_url)

        if not self.aggregator_url.endswith("/api"):
            warnings.warn("Aggregator url should end with /api. Appending /api")
            self.aggregator_url += "/api"

        if not self.aggregator_url:
            raise Exception("No aggregator url provided")

        self.token_url = token_url
        self.username = username
        self.password = password
        self.robot_id = robot_id
        self.robot_secret = robot_secret

        self._headers = headers
        self.token = None
        self.token_expiration = None

        if client:
            self.http = client
        else:
            self.http = self.setup_http()

    @property
    def headers(self) -> dict:
        token = self._get_token()
        if self._headers:
            return {**self._headers, "Authorization": f"Bearer {token}"}

        return {"Authorization": f"Bearer {token}"}


    def setup_clients(self):
        self.http.headers.update(self.headers)
        self.proposals = ProposalClient(self, prefix="/proposal")


    def setup_http(self):
        self.http = httpx.Client(
            headers=self.headers,
            base_url=self.aggregator_url,
        )

    def _get_token(self):
        if not self.token or self.token_expiration < pendulum.now():
            if self.username and self.password:
                r = httpx.post(self.token_url, data={"username": self.username, "password": self.password})
            elif self.robot_id and self.robot_secret:

                r = httpx.post(self.token_url, data={"id": self.robot_id, "secret": self.robot_secret})
            else:
                raise Exception("No credentials provided")

            try:
                r.raise_for_status()
            except Exception as e:
                print(r.text)
                raise e
            r = r.json()
            self.token = r["access_token"]
            self.token_expiration = pendulum.now().add(seconds=r["expires_in"])

        return self.token

    @staticmethod
    def _check_add_http_https(url):
        if url.startswith("http://") or url.startswith("https://"):
            return url
        return f"http://{url}"

