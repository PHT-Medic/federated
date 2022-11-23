from fastapi.encoders import jsonable_encoder
from pht_federated.aggregator.api.discoveries import statistics
from pht_federated.aggregator.clients.discovery_client import DiscoveryClient
from uuid import uuid4
from pht_federated.aggregator.api.schemas.dataset_statistics import DiscoveryStatistics
from pht_federated.aggregator.api.schemas.proposals import Proposals
from pht_federated.aggregator.api.schemas.discovery import DiscoverySummary
from datetime import datetime
import sklearn
from sklearn.datasets import load_diabetes, load_breast_cancer
import pandas as pd
import numpy as np
import json

PROPOSAL_ID_NUMERIC = uuid4()
PROPOSAL_ID_MIXED = uuid4()
SELECTED_FEATURES = "age,sex,bmi"

discovery_client = DiscoveryClient(api_url="http://127.0.0.1:8000")


def test_post_proposal():

    response_mix = discovery_client.post_proposal(proposal_id=PROPOSAL_ID_MIXED)
    response_num = discovery_client.post_proposal(proposal_id=PROPOSAL_ID_NUMERIC)

    assert type(response_mix) == Proposals
    assert response_mix.created_at == datetime.now().replace(second=0, microsecond=0)
    assert type(response_num) == Proposals
    assert response_num.created_at == datetime.now().replace(second=0, microsecond=0)


def test_post_discovery_statistics_numeric():

    diabetes_dataset = sklearn.datasets.load_diabetes(return_X_y=False, as_frame=False)

    df = pd.DataFrame(diabetes_dataset['data'], columns=diabetes_dataset['feature_names'])
    df['target'] = diabetes_dataset['target']
    df_split = np.array_split(df, 3)

    stats1_json = jsonable_encoder(statistics.get_discovery_statistics(df_split[0]))
    stats2_json = jsonable_encoder(statistics.get_discovery_statistics(df_split[1]))
    stats3_json = jsonable_encoder(statistics.get_discovery_statistics(df_split[2]))

    response_num1 = discovery_client.post_discovery_statistics(statistics_create={
        "item_count": stats1_json['item_count'],
        "feature_count": stats1_json['feature_count'],
        "column_information": stats1_json['column_information']
    }, proposal_id=PROPOSAL_ID_NUMERIC)

    assert type(response_num1) == DiscoveryStatistics
    assert response_num1.proposal_id == PROPOSAL_ID_NUMERIC

    response_num2 = discovery_client.post_discovery_statistics(statistics_create={
        "item_count": stats2_json['item_count'],
        "feature_count": stats2_json['feature_count'],
        "column_information": stats2_json['column_information']
    }, proposal_id=PROPOSAL_ID_NUMERIC)

    assert type(response_num2) == DiscoveryStatistics
    assert response_num2.proposal_id == PROPOSAL_ID_NUMERIC

    response_num3 = discovery_client.post_discovery_statistics(statistics_create={
        "item_count": stats3_json['item_count'],
        "feature_count": stats3_json['feature_count'],
        "column_information": stats3_json['column_information']
    }, proposal_id=PROPOSAL_ID_NUMERIC)

    assert type(response_num3) == DiscoveryStatistics
    assert response_num3.proposal_id == PROPOSAL_ID_NUMERIC

def test_post_discovery_statistics_mixed():

    df_titanic = pd.read_csv('./data/train_data_titanic.csv')
    df_split = np.array_split(df_titanic, 3)

    stats1_json = jsonable_encoder(statistics.get_discovery_statistics(df_split[0]))
    stats2_json = jsonable_encoder(statistics.get_discovery_statistics(df_split[1]))
    stats3_json = jsonable_encoder(statistics.get_discovery_statistics(df_split[2]))

    response_mix1 = discovery_client.post_discovery_statistics(statistics_create={
        "item_count": stats1_json['item_count'],
        "feature_count": stats1_json['feature_count'],
        "column_information": stats1_json['column_information']
    }, proposal_id=PROPOSAL_ID_MIXED)

    assert type(response_mix1) == DiscoveryStatistics
    assert response_mix1.proposal_id == PROPOSAL_ID_MIXED

    response_mix2 = discovery_client.post_discovery_statistics(statistics_create={
        "item_count": stats2_json['item_count'],
        "feature_count": stats2_json['feature_count'],
        "column_information": stats2_json['column_information']
    },proposal_id=PROPOSAL_ID_MIXED)

    assert type(response_mix2) == DiscoveryStatistics
    assert response_mix2.proposal_id == PROPOSAL_ID_MIXED

    response_mix3 = discovery_client.post_discovery_statistics(statistics_create={
        "item_count": stats3_json['item_count'],
        "feature_count": stats3_json['feature_count'],
        "column_information": stats3_json['column_information']
    },proposal_id=PROPOSAL_ID_MIXED)

    assert type(response_mix3) == DiscoveryStatistics
    assert response_mix3.proposal_id == PROPOSAL_ID_MIXED

def test_get_aggregated_discovery_results():

    response = discovery_client.get_aggregated_discovery_results(proposal_id=PROPOSAL_ID_MIXED)
    assert type(response) == DiscoverySummary
    assert response.proposal_id == PROPOSAL_ID_MIXED

    response = json.loads(response.json())

    df_titanic = pd.read_csv('./data/train_data_titanic.csv')
    stats_df = statistics.get_discovery_statistics(df_titanic)

    assert stats_df.column_information[0].mean == response['column_information'][0]['mean']
    assert stats_df.column_information[0].min == response['column_information'][0]['min']
    assert stats_df.column_information[0].max == response['column_information'][0]['max']
    assert stats_df.column_information[0].not_na_elements == response['column_information'][0]['not_na_elements']

    assert stats_df.column_information[4].number_categories == response['column_information'][4]['number_categories']
    assert stats_df.column_information[4].value_counts == response['column_information'][4]['value_counts']
    assert stats_df.column_information[4].most_frequent_element == response['column_information'][4]['most_frequent_element']
    assert stats_df.column_information[4].frequency == response['column_information'][4]['frequency']

def test_get_aggregated_discovery_results_query():

    response = discovery_client.get_aggregated_discovery_results(proposal_id=PROPOSAL_ID_NUMERIC, features=SELECTED_FEATURES)
    assert type(response) == DiscoverySummary
    assert response.proposal_id == PROPOSAL_ID_NUMERIC

    response = json.loads(response.json())

    diabetes_dataset = sklearn.datasets.load_diabetes(return_X_y=False, as_frame=False)
    df = pd.DataFrame(diabetes_dataset['data'], columns=diabetes_dataset['feature_names'])
    df['target'] = diabetes_dataset['target']
    stats_df = statistics.get_discovery_statistics(df)


    assert stats_df.item_count == response['item_count']
    assert stats_df.feature_count == response['feature_count']

    assert stats_df.column_information[0].mean == response['column_information'][0]['mean']
    assert stats_df.column_information[0].min == response['column_information'][0]['min']
    assert stats_df.column_information[0].max == response['column_information'][0]['max']
    assert stats_df.column_information[0].not_na_elements == response['column_information'][0]['not_na_elements']

def test_delete_discovery_statistics():

    response = discovery_client.delete_discovery_statistics(proposal_id=PROPOSAL_ID_MIXED)
    assert type(response) == int
    assert response == 3
