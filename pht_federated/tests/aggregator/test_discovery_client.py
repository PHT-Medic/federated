from pht_federated.aggregator.clients.discovery_client import discovery_client
from uuid import uuid4

PROPOSAL_ID_NUMERIC = uuid4()
PROPOSAL_ID_MIXED = uuid4()
SELECTED_FEATURES = "age,sex,bmi"


def test_post_proposal():
    result = discovery_client.post_proposal(proposal_id=PROPOSAL_ID_MIXED)
    result = discovery_client.post_proposal(proposal_id=PROPOSAL_ID_NUMERIC)
    print("Result : {}".format(result.json()))


def test_post_discovery_statistics():
    result = discovery_client.post_discovery_statistics(proposal_id=PROPOSAL_ID_MIXED)
    result = discovery_client.post_discovery_statistics(proposal_id=PROPOSAL_ID_MIXED)
    result = discovery_client.post_discovery_statistics(proposal_id=PROPOSAL_ID_MIXED)
    result = discovery_client.post_discovery_statistics(proposal_id=PROPOSAL_ID_NUMERIC)
    result = discovery_client.post_discovery_statistics(proposal_id=PROPOSAL_ID_NUMERIC)
    result = discovery_client.post_discovery_statistics(proposal_id=PROPOSAL_ID_NUMERIC)
    print("Result : {}".format(result.json()))

def test_get_aggregated_discovery_results():
    result = discovery_client.get_aggregated_discovery_results(proposal_id=PROPOSAL_ID_MIXED)
    print("Result : {}".format(result))

def test_get_aggregated_discovery_results_query():
    result = discovery_client.get_aggregated_discovery_results(proposal_id=PROPOSAL_ID_NUMERIC, query=SELECTED_FEATURES)
    print("Result : {}".format(result))

def test_delete_discovery_statistics():
    result = discovery_client.delete_discovery_statistics(proposal_id=PROPOSAL_ID_MIXED)
    print("Result : {}".format(result.json()))


