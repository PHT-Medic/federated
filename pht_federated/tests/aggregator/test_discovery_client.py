from pht_federated.aggregator.clients.discovery_client import DiscoveryClient
from uuid import uuid4

PROPOSAL_ID_NUMERIC = uuid4()
PROPOSAL_ID_MIXED = uuid4()
SELECTED_FEATURES = "age,sex,bmi"

discovery_client = DiscoveryClient(api_url="http://127.0.0.1:8000")


def test_post_proposal():

    response_mix = discovery_client.post_proposal(proposal_id=PROPOSAL_ID_MIXED)
    response_num = discovery_client.post_proposal(proposal_id=PROPOSAL_ID_NUMERIC)

    assert response_mix.status_code == 200, response_mix.text
    assert response_num.status_code == 200, response_num.text


def test_post_discovery_statistics():

    create_msg = {
            "item_count": 50,
            "feature_count": 20,
            "column_information": [{'type': 'numeric',
                                    'title': 'PassengerId',
                                    'not_na_elements': 891,
                                    'mean': 446.0,
                                    'std': 81.5,
                                    'min': 1.0,
                                    'max': 891.0}]
        }
    response_mix1 = discovery_client.post_discovery_statistics(statistics_create=create_msg, proposal_id=PROPOSAL_ID_MIXED)
    response_mix2 = discovery_client.post_discovery_statistics(statistics_create=create_msg,proposal_id=PROPOSAL_ID_MIXED)
    response_mix3 = discovery_client.post_discovery_statistics(statistics_create=create_msg,proposal_id=PROPOSAL_ID_MIXED)
    response_num1 = discovery_client.post_discovery_statistics(statistics_create=create_msg,proposal_id=PROPOSAL_ID_NUMERIC)
    response_num2 = discovery_client.post_discovery_statistics(statistics_create=create_msg,proposal_id=PROPOSAL_ID_NUMERIC)
    response_num3 = discovery_client.post_discovery_statistics(statistics_create=create_msg,proposal_id=PROPOSAL_ID_NUMERIC)

    assert response_mix1.status_code == 200, response_mix1.text
    assert response_mix2.status_code == 200, response_mix2.text
    assert response_mix3.status_code == 200, response_mix3.text
    assert response_num1.status_code == 200, response_num1.text
    assert response_num2.status_code == 200, response_num2.text
    assert response_num3.status_code == 200, response_num3.text

def test_get_aggregated_discovery_results():

    response = discovery_client.get_aggregated_discovery_results(proposal_id=PROPOSAL_ID_MIXED)
    assert response.status_code == 200, response.text

def test_get_aggregated_discovery_results_query():

    response = discovery_client.get_aggregated_discovery_results(proposal_id=PROPOSAL_ID_NUMERIC, features=SELECTED_FEATURES)
    assert response.status_code == 200, response.text

def test_delete_discovery_statistics():

    response = discovery_client.delete_discovery_statistics(proposal_id=PROPOSAL_ID_MIXED)
    assert response.status_code == 200, response.text
