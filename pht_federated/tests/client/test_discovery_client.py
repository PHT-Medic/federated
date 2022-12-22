# flake8: noqa

from uuid import uuid4

import numpy as np
import pandas as pd
import pytest
import sklearn
import sklearn.datasets
from fastapi.encoders import jsonable_encoder
from fastapi.testclient import TestClient

from pht_federated.aggregator.api.dependencies import get_db
from pht_federated.aggregator.app import app
from pht_federated.aggregator.schemas.dataset_statistics import (
    DiscoveryStatistics, StatisticsCreate)
from pht_federated.aggregator.schemas.discovery import (DataDiscoveryCreate,
                                                        DataDiscoveryUpdate,
                                                        DiscoverySummary)
from pht_federated.aggregator.schemas.proposal import Proposal, ProposalCreate
from pht_federated.aggregator.services.discovery import statistics
from pht_federated.client.resources import ProposalClient
# from pht_federated.client.discovery_client import DiscoveryClient
from pht_federated.client.resources.discovery import DiscoveryClient
from pht_federated.tests.aggregator.test_db import override_get_db

app.dependency_overrides[get_db] = override_get_db

api_client = TestClient(app)


@pytest.fixture
def discovery_client():
    client = DiscoveryClient(api_client, prefix="/api/proposal")
    assert client is not None
    return client


@pytest.fixture
def proposal_id():
    proposal_client = ProposalClient(
        api_client, schema=Proposal, prefix="/api/proposal"
    )
    proposal = proposal_client.create(ProposalCreate(name="Test Proposal", id=uuid4()))
    return proposal.id


def test_create_discovery(proposal_id, discovery_client):
    discover = DataDiscoveryCreate(query={"hello": "world"})
    response = discovery_client.create(proposal_id, discover)
    assert response.proposal_id == proposal_id
    assert response.query == discover.query


def test_get_discovery(proposal_id, discovery_client):
    discover = DataDiscoveryCreate(query={"hello": "world"})
    response = discovery_client.create(proposal_id, discover)
    response = discovery_client.get(proposal_id, response.id)
    assert response.proposal_id == proposal_id
    assert response.query == discover.query


def test_get_multi_discovery(proposal_id, discovery_client):
    discover = DataDiscoveryCreate(query={"hello": "world"})
    response = discovery_client.create(proposal_id, discover)
    response = discovery_client.get_multi(proposal_id)
    assert len(response) >= 1


def test_update_discovery(proposal_id, discovery_client):
    discover = DataDiscoveryCreate(query={"hello": "world"})
    response = discovery_client.create(proposal_id, discover)
    response = discovery_client.update(
        proposal_id, response.id, DataDiscoveryUpdate(query={"hello": "update"})
    )
    assert response.proposal_id == proposal_id
    assert response.query == {"hello": "update"}


def test_delete_discovery(proposal_id, discovery_client):
    discover = DataDiscoveryCreate(query={"hello": "world"})
    response = discovery_client.create(proposal_id, discover)
    response = discovery_client.delete(proposal_id, response.id)
    assert response.proposal_id == proposal_id
    assert response.query == discover.query

    with pytest.raises(Exception):
        response = discovery_client.get(proposal_id, response.id)


# PROPOSAL_ID_NUMERIC = uuid4()
# PROPOSAL_ID_MIXED = uuid4()
# SELECTED_FEATURES = "age,sex,bmi"
#
# load_dotenv(find_dotenv())
#
#
#
#
# discovery_client = DiscoveryClient(api_url=os.getenv("AGGREGATOR_URL", "http://127.0.0.1:8000"))
#
#
# def test_post_proposal():
#
#     response_mix = discovery_client.create_proposal(proposal_id=PROPOSAL_ID_MIXED)
#     response_num = discovery_client.create_proposal(proposal_id=PROPOSAL_ID_NUMERIC)
#
#     assert type(response_mix) == Proposal
#     assert response_mix.created_at == datetime.now().replace(second=0, microsecond=0)
#     assert type(response_num) == Proposal
#     assert response_num.created_at == datetime.now().replace(second=0, microsecond=0)
#
#
def test_post_discovery_statistics_numeric(discovery_client):

    # setup proposal and discovery
    proposal_client = ProposalClient(
        api_client, schema=Proposal, prefix="/api/proposal"
    )
    proposal = proposal_client.create(ProposalCreate(name="Test Stats", id=uuid4()))
    proposal_id = proposal.id

    discovery = discovery_client.create(
        proposal_id, DataDiscoveryCreate(query={"hello": "world"})
    )

    # get stats from diabetes dataset
    diabetes_dataset = sklearn.datasets.load_diabetes(return_X_y=False, as_frame=False)

    df = pd.DataFrame(
        diabetes_dataset["data"], columns=diabetes_dataset["feature_names"]
    )
    df["target"] = diabetes_dataset["target"]
    df_split = np.array_split(df, 3)

    stats1_json = jsonable_encoder(statistics.get_discovery_statistics(df_split[0]))
    stats2_json = jsonable_encoder(statistics.get_discovery_statistics(df_split[1]))
    stats3_json = jsonable_encoder(statistics.get_discovery_statistics(df_split[2]))

    stats_create_1 = StatisticsCreate(
        **{
            "item_count": stats1_json["item_count"],
            "feature_count": stats1_json["feature_count"],
            "column_information": stats1_json["column_information"],
        }
    )

    stats_create_2 = StatisticsCreate(
        **{
            "item_count": stats2_json["item_count"],
            "feature_count": stats2_json["feature_count"],
            "column_information": stats2_json["column_information"],
        }
    )

    stats_create_3 = StatisticsCreate(
        **{
            "item_count": stats3_json["item_count"],
            "feature_count": stats3_json["feature_count"],
            "column_information": stats3_json["column_information"],
        }
    )

    # post stats to discovery
    response1 = discovery_client.submit_discovery_statistics(
        proposal_id, discovery.id, stats_create_1
    )
    response2 = discovery_client.submit_discovery_statistics(
        proposal_id, discovery.id, stats_create_2
    )
    response3 = discovery_client.submit_discovery_statistics(
        proposal_id, discovery.id, stats_create_3
    )

    assert response1.discovery_id == discovery.id
    assert response2.discovery_id == discovery.id
    assert response3.discovery_id == discovery.id

    stats = statistics.get_discovery_statistics(df)

    aggregate_response = discovery_client.get_aggregated_results(
        proposal_id, discovery.id
    )
    print(aggregate_response)
    assert aggregate_response.discovery_id == discovery.id


#
# def test_post_discovery_statistics_mixed():
#
#     df_titanic = pd.read_csv('../aggregator/data/train_data_titanic.csv')
#     df_split = np.array_split(df_titanic, 3)
#
#     stats1_json = jsonable_encoder(statistics.get_discovery_statistics(df_split[0]))
#     stats2_json = jsonable_encoder(statistics.get_discovery_statistics(df_split[1]))
#     stats3_json = jsonable_encoder(statistics.get_discovery_statistics(df_split[2]))
#
#     response_mix1 = discovery_client.post_discovery_statistics(statistics_create={
#         "item_count": stats1_json['item_count'],
#         "feature_count": stats1_json['feature_count'],
#         "column_information": stats1_json['column_information']
#     }, proposal_id=PROPOSAL_ID_MIXED)
#
#     assert type(response_mix1) == DiscoveryStatistics
#     assert response_mix1.proposal_id == PROPOSAL_ID_MIXED
#
#     response_mix2 = discovery_client.post_discovery_statistics(statistics_create={
#         "item_count": stats2_json['item_count'],
#         "feature_count": stats2_json['feature_count'],
#         "column_information": stats2_json['column_information']
#     },proposal_id=PROPOSAL_ID_MIXED)
#
#     assert type(response_mix2) == DiscoveryStatistics
#     assert response_mix2.proposal_id == PROPOSAL_ID_MIXED
#
#     response_mix3 = discovery_client.post_discovery_statistics(statistics_create={
#         "item_count": stats3_json['item_count'],
#         "feature_count": stats3_json['feature_count'],
#         "column_information": stats3_json['column_information']
#     },proposal_id=PROPOSAL_ID_MIXED)
#
#     assert type(response_mix3) == DiscoveryStatistics
#     assert response_mix3.proposal_id == PROPOSAL_ID_MIXED
#
# def test_get_aggregated_discovery_results():
#
#     response = discovery_client.get_aggregated_discovery_results(proposal_id=PROPOSAL_ID_MIXED)
#     assert type(response) == DiscoverySummary
#     assert response.proposal_id == PROPOSAL_ID_MIXED
#
#     response = json.loads(response.json())
#
#     df_titanic = pd.read_csv('../aggregator/data/train_data_titanic.csv')
#     stats_df = statistics.get_discovery_statistics(df_titanic)
#
#     assert stats_df.column_information[0].mean == response['column_information'][0]['mean']
#     assert stats_df.column_information[0].min == response['column_information'][0]['min']
#     assert stats_df.column_information[0].max == response['column_information'][0]['max']
#     assert stats_df.column_information[0].not_na_elements == response['column_information'][0]['not_na_elements']
#
#     assert stats_df.column_information[4].number_categories == response['column_information'][4]['number_categories']
#     assert stats_df.column_information[4].value_counts == response['column_information'][4]['value_counts']
#     assert stats_df.column_information[4].most_frequent_element == response['column_information'][4]['most_frequent_element']
#     assert stats_df.column_information[4].frequency == response['column_information'][4]['frequency']
#
# def test_get_aggregated_discovery_results_query():
#
#     response = discovery_client.get_aggregated_discovery_results(proposal_id=PROPOSAL_ID_NUMERIC, features=SELECTED_FEATURES)
#     assert type(response) == DiscoverySummary
#     assert response.proposal_id == PROPOSAL_ID_NUMERIC
#
#     response = json.loads(response.json())
#
#     diabetes_dataset = sklearn.datasets.load_diabetes(return_X_y=False, as_frame=False)
#     df = pd.DataFrame(diabetes_dataset['data'], columns=diabetes_dataset['feature_names'])
#     df['target'] = diabetes_dataset['target']
#     stats_df = statistics.get_discovery_statistics(df)
#
#
#     assert stats_df.item_count == response['item_count']
#     assert stats_df.feature_count == response['feature_count']
#
#     assert stats_df.column_information[0].mean == response['column_information'][0]['mean']
#     assert stats_df.column_information[0].min == response['column_information'][0]['min']
#     assert stats_df.column_information[0].max == response['column_information'][0]['max']
#     assert stats_df.column_information[0].not_na_elements == response['column_information'][0]['not_na_elements']
#
# def test_delete_discovery_statistics():
#
#     response = discovery_client.delete_discovery_statistics(proposal_id=PROPOSAL_ID_MIXED)
#     assert type(response) == int
#     assert response == 3
