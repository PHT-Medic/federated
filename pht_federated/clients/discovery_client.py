import requests
import os
from typing import Union
from uuid import uuid4
from requests.models import Response
from loguru import logger
from pht_federated.aggregator.api.schemas.dataset_statistics import DiscoveryStatistics
from pht_federated.aggregator.api.schemas.proposals import Proposals
from pht_federated.aggregator.api.schemas.discovery import DiscoverySummary


class DiscoveryClient:

    def __init__(self, api_url: str = None):
        """
            Setup and verify connection parameters either based on arguments or .env vars
        """

        self.api_url = api_url if api_url else os.getenv("AGGREGATOR_API_URL")
        if not self.api_url.startswith("http://"):
            self.api_url = "http://" + self.api_url
        if not self.api_url.endswith("/api/proposal"):
            self.api_url = self.api_url + "/api/proposal"

        logger.info("Establishing connection to API url : {}".format(self.api_url))

    def post_proposal(self, proposal_id: uuid4 = None) -> Proposals:
        """
        Sending POST request to create a proposal entry in the database with defined proposal_id
        :param proposal_id: uuid4 value that identifies proposal
        :return: result body of POST request
        """
        endpoint = f"/{proposal_id}"
        requests_post_proposal_url = self.api_url + endpoint
        request = requests.post(requests_post_proposal_url)
        request.raise_for_status()

        result = request.json()
        result = Proposals(**result)

        return result

    def post_discovery_statistics(self, statistics_create: dict, proposal_id: uuid4 = None) -> DiscoveryStatistics:
        """
        Sending POST request to create a DiscoveryStatistics entry in the database connected to proposal_id
        :param create_msg: json body of DiscoveryStatistics object
        :param proposal_id: uuid4 value that identifies corresponding proposal
        :return: result body of POST request
        """
        endpoint = f"/{proposal_id}/discovery"
        requests_post_discovery_url = self.api_url + endpoint
        request = requests.post(requests_post_discovery_url, json=statistics_create)
        request.raise_for_status()

        result = request.json()
        result = DiscoveryStatistics(**result)

        return result

    def get_aggregated_discovery_results(self, proposal_id: uuid4 = None,
                                         features: Union[str, None] = None) -> DiscoverySummary:
        """
        Sending GET request to get a aggregated DiscoverySummary object over objects in database for corresponding
        proposal_id
        :param proposal_id: uuid4 value that identifies corresponding proposal
        :param query: optional comma seperated list of selected features to filter
        :return: result body of GET request
        """
        if not features:
            endpoint = f"/{proposal_id}/discovery"
        else:
            endpoint = f"/{proposal_id}/discovery?query={features}"

        requests_get_url = self.api_url + endpoint
        request = requests.get(requests_get_url)
        request.raise_for_status()

        result = request.json()
        result = DiscoverySummary(**result)

        return result

    def delete_discovery_statistics(self, proposal_id: uuid4 = None) -> int:
        """
        Sending DELETE request to delete a DiscoveryStatistics object for corresponding proposal_id
        :param proposal_id: uuid4 value that identifies corresponding proposal
        :return: result body of DELETE request
        """
        endpoint = f"/{proposal_id}/discovery"
        requests_delete_discovery_url = self.api_url + endpoint
        request = requests.delete(requests_delete_discovery_url)
        request.raise_for_status()

        result = request.json()

        return result
