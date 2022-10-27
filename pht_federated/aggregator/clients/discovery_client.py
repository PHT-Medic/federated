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
        if not self.api_url.endswith("/api/v2.0"):
            self.api_url = self.api_url + "/api/v2.0"

        print("Self.api_url : {}".format(self.api_url))

        # self.url = self.url.rstrip("/") + "/api/v2.0"

        #self.username = username if username else os.getenv("HARBOR_USER")
        #assert self.username

        #self.password = password if password else os.getenv("HARBOR_PW")
        #assert self.password

    def get_aggregated_discovery_results(self, proposal_id: uuid4 = None, query: Union[str, None] = None) -> dict:
        if not proposal_id:
            proposal_id = int(os.getenv("PROPOSAL_ID"))
        assert proposal_id

        print("Query : {}".format(query))

        if not query:
            endpoint = f"/{proposal_id}/discovery"
        else:
            endpoint = f"/{proposal_id}/discovery?query={query}"

        requests_get_url = self.api_url + endpoint
        print("Requests_Get_Url : {}".format(requests_get_url))
        r = requests.get(requests_get_url)
        results = r.json()
        print("Results : {}".format(results))

        return results


    def post_discovery(self, proposal_id: uuid4 = None):

        if not proposal_id:
            proposal_id = int(os.getenv("PROPOSAL_ID"))
        assert proposal_id

        endpoint = f"/{proposal_id}/discovery"
        requests_post_discovery_url = self.api_url + endpoint
        print("PROPOSAL ID : {}".format(proposal_id))
        print("Requests_Post_Discovery_Url : {}".format(requests_post_discovery_url))
        r = requests.post(requests_post_discovery_url, json={
            "item_count": 50,
            "feature_count": 20,
            "column_information": {}
        })
        results = r.json()
        print("Results : {}".format(results))

        return results

    def post_proposal(self, proposal_id: uuid4 = None):

        if not proposal_id:
            proposal_id = int(os.getenv("PROPOSAL_ID"))
        assert proposal_id

        endpoint = f"/{proposal_id}/proposal"
        requests_post_proposal_url = self.api_url + endpoint
        print("PROPOSAL ID : {}".format(proposal_id))
        print("Requests_Post_Proposal_Url : {}".format(requests_post_proposal_url))
        r = requests.post(requests_post_proposal_url)
        results = r.json()
        print("Results : {}".format(results))

        return results



discovery_client = DiscoveryClient(api_url="http://127.0.0.1:8000")
discovery_client.post_proposal(proposal_id=PROPOSAL_ID_MIXED)
discovery_client.post_discovery(proposal_id=PROPOSAL_ID_MIXED)
discovery_client.get_aggregated_discovery_results(proposal_id=PROPOSAL_ID_MIXED)