import requests
import os
from typing import Union, List




class DiscoveryClient:

    def __init__(self, api_url: str = None, username: str = None, password: str = None):
        # Setup and verify connection parameters either based on arguments or .env vars

        self.api_url = api_url if api_url else os.getenv("AGGREGATOR_API_URL")
        if not self.api_url.startswith("https://"):
            self.api_url = "https://" + self.api_url
        if not self.api_url.endswith("/api/v2.0"):
            self.api_url = self.api_url + "/api/v2.0"

        # self.url = self.url.rstrip("/") + "/api/v2.0"

        #self.username = username if username else os.getenv("HARBOR_USER")
        #assert self.username

        #self.password = password if password else os.getenv("HARBOR_PW")
        #assert self.password

    def get_aggregated_discovery_results(self, proposal_id: int = None) -> dict:
        if not proposal_id:
            proposal_id = int(os.getenv("PROPOSAL_ID"))
        assert proposal_id

        endpoint = f"/{proposal_id}/discovery"
        r = requests.get(self.api_url + endpoint)
        results = r.json()
        print(results)

        return results



discovery_client = DiscoveryClient()
discovery_client.get_aggregated_discovery_results()