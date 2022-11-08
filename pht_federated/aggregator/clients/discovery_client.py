import requests
import os
from typing import Union, List
from uuid import uuid4

PROPOSAL_ID_MIXED = uuid4()

class DiscoveryClient:

    def __init__(self, api_url: str = None, username: str = None, password: str = None):
        # Setup and verify connection parameters either based on arguments or .env vars

        self.api_url = api_url if api_url else os.getenv("AGGREGATOR_API_URL")
        if not self.api_url.startswith("http://"):
            self.api_url = "http://" + self.api_url
        if not self.api_url.endswith("/api/proposal"):
            self.api_url = self.api_url + "/api/proposal"

        print("SELF API URL : {}".format(self.api_url))

    def post_proposal(self, proposal_id: uuid4 = None):
        if not proposal_id:
            proposal_id = int(os.getenv("PROPOSAL_ID"))
        assert proposal_id

        endpoint = f"/{proposal_id}"
        requests_post_proposal_url = self.api_url + endpoint
        #print("REQUESTS POST PROPOSAL URL : {}".format(requests_post_proposal_url))
        results = requests.post(requests_post_proposal_url)

        return results

    def post_discovery_statistics(self, create_msg: dict, proposal_id: uuid4 = None):
        if not proposal_id:
            proposal_id = int(os.getenv("PROPOSAL_ID"))
        assert proposal_id

        endpoint = f"/{proposal_id}/discovery"
        requests_post_discovery_url = self.api_url + endpoint
        #print("REQUESTS POST DISCOVERY URL : {}".format(requests_post_discovery_url))
        results = requests.post(requests_post_discovery_url, json=create_msg)

        return results
    def get_aggregated_discovery_results(self, proposal_id: uuid4 = None, query: Union[str, None] = None) -> dict:
        if not proposal_id:
            proposal_id = int(os.getenv("PROPOSAL_ID"))
        assert proposal_id

        if not query:
            endpoint = f"/{proposal_id}/discovery"
        else:
            endpoint = f"/{proposal_id}/discovery?query={query}"

        requests_get_url = self.api_url + endpoint
        #print("REQUESTS GET URL : {}".format(requests_get_url))
        results = requests.get(requests_get_url)

        return results

    def delete_proposal(self, proposal_id: uuid4 = None):
        if not proposal_id:
            proposal_id = int(os.getenv("PROPOSAL_ID"))
        assert proposal_id

        endpoint = f"/{proposal_id}"
        requests_delete_proposal_url = self.api_url + endpoint
        #print("REQUESTS DELETE PROPOSAL URL : {}".format(requests_delete_proposal_url))
        results = requests.delete(requests_delete_proposal_url)

        return results

    def delete_discovery_statistics(self, proposal_id: uuid4 = None):
        if not proposal_id:
            proposal_id = int(os.getenv("PROPOSAL_ID"))
        assert proposal_id

        endpoint = f"/{proposal_id}/discovery"
        requests_delete_discovery_url = self.api_url + endpoint
        #print("REQUESTS DELETE DISCOVERY URL : {}".format(requests_delete_discovery_url))
        results = requests.delete(requests_delete_discovery_url)

        return results




discovery_client = DiscoveryClient(api_url="http://127.0.0.1:8000")

