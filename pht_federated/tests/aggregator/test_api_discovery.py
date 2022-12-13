import sklearn
import numpy as np
import pandas as pd
from sklearn.datasets import load_diabetes
from fastapi.testclient import TestClient
from pht_federated.aggregator.app import app
from pht_federated.aggregator.api.dependencies import get_db
from pht_federated.aggregator.api.endpoints.discovery import *
from pht_federated.aggregator.api.discoveries import statistics
from pht_federated.aggregator.api.discoveries.plots import *
from sklearn.datasets import load_breast_cancer
from uuid import uuid4
import pytest

from pht_federated.tests.aggregator.test_db import override_get_db

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

PROPOSAL_ID_NUMERIC = uuid4()
PROPOSAL_ID_NUMERIC2 = uuid4()
PROPOSAL_ID_MIXED = uuid4()
FEATURE_NAME_NUMERIC = "bmi"
FEATURE_NAME_NUMERIC2 = "Age"
FEATURE_NAME_CATEGORICAL = 'Embarked'
SELECTED_FEATURES = "age,sex,bmi"


@pytest.fixture
def proposal_id():
    return str(uuid4())


def create_proposal_and_discovery():
    response = client.post(f"/api/proposal", json={"id": str(uuid4()), "name": "Discovery test proposal"})
    proposal_id = response.json()['id']
    response = client.post(
        f"/api/proposal/{proposal_id}/discoveries",
        json={
            "query": {"hello": "world"},
        }
    )
    discovery_id = response.json()['id']
    return proposal_id, discovery_id


def test_create_discovery(proposal_id):
    response = client.post(f"/api/proposal", json={"id": proposal_id, "name": "Discovery test proposal"})
    print(response.json())
    response = client.post(
        f"/api/proposal/{response.json()['id']}/discoveries",
        json={
            "query": {"hello": "world"},
        }
    )
    assert response.status_code == 200, response.text
    print(response.json())


def test_get_discovery(proposal_id):
    proposal_id, discovery_id = create_proposal_and_discovery()

    response = client.get(f"/api/proposal/{proposal_id}/discoveries/{discovery_id}")

    assert response.status_code == 200, response.text
    assert response.json()["query"] == {"hello": "world"}

    # 404 if proposal does not exist
    response = client.get(f"/api/proposal/{uuid4()}/discoveries/{discovery_id}")
    assert response.status_code == 404, response.text

    # 404 if discovery does not exist
    response = client.get(f"/api/proposal/{proposal_id}/discoveries/{99999}")
    assert response.status_code == 404, response.text


def test_get_all_discoveries():
    response = client.post(f"/api/proposal", json={"id": str(uuid4()), "name": "Discovery test proposal"})
    proposal_id = response.json()['id']
    response = client.post(
        f"/api/proposal/{proposal_id}/discoveries",
        json={
            "query": {"hello": "world"},
        }
    )
    response = client.get(f"/api/proposal/{proposal_id}/discoveries")
    assert response.status_code == 200, response.text
    assert len(response.json()) >= 1

    # 404 if proposal does not exist
    response = client.get(f"/api/proposal/{uuid4()}/discoveries")
    assert response.status_code == 404, response.text


def test_update_discovery():
    proposal_id, discovery_id = create_proposal_and_discovery()
    response = client.put(f"/api/proposal/{proposal_id}/discoveries/{discovery_id}",
                          json={"query": {"hello": "world2"}})
    assert response.status_code == 200, response.text
    assert response.json()["query"] == {"hello": "world2"}

    # 404 if proposal does not exist
    response = client.put(f"/api/proposal/{uuid4()}/discoveries/{discovery_id}", json={"query": {"hello": "world2"}})
    assert response.status_code == 404, response.text

    # 404 if discovery does not exist
    response = client.put(f"/api/proposal/{proposal_id}/discoveries/{99999}", json={"query": {"hello": "world2"}})
    assert response.status_code == 404, response.text


def test_delete_discovery():
    proposal_id, discovery_id = create_proposal_and_discovery()

    response = client.delete(f"/api/proposal/{proposal_id}/discoveries/{discovery_id}")
    assert response.status_code == 200, response.text

    # 404 if proposal does not exist
    response = client.delete(f"/api/proposal/{uuid4()}/discoveries/{discovery_id}")
    assert response.status_code == 404, response.text

    # 404 if discovery does not exist
    response = client.delete(f"/api/proposal/{proposal_id}/discoveries/{99999}")
    assert response.status_code == 404, response.text


def test_discovery_create_numeric():
    diabetes_dataset = sklearn.datasets.load_diabetes(return_X_y=False, as_frame=False)

    df = pd.DataFrame(diabetes_dataset['data'], columns=diabetes_dataset['feature_names'])
    df['target'] = diabetes_dataset['target']
    # print("Diabetes dataset pandas : {}".format(tabulate(df, headers='keys', tablefmt='psql')))
    df_split = np.array_split(df, 3)

    stats1_json = jsonable_encoder(statistics.get_discovery_statistics(df_split[0]))
    stats2_json = jsonable_encoder(statistics.get_discovery_statistics(df_split[1]))
    stats3_json = jsonable_encoder(statistics.get_discovery_statistics(df_split[2]))
    # print("Resulting DataSetStatistics from diabetes_dataset : {} + type {}".format(stats_df, type(stats_df)))

    # proposal_id, discovery_id = create_proposal_and_discovery()
    proposal_id = client.post(
        f"/api/proposal", json={"id": str(PROPOSAL_ID_NUMERIC), "name": "Discovery test proposal"}
    ).json()['id']

    response = client.post(
        f"/api/proposal/{proposal_id}/discoveries",
        json={
            "query": {"hello": "world"},
        }
    )
    discovery_id = response.json()['id']

    response = client.post(f"/api/proposal/{proposal_id}/discoveries/{discovery_id}/stats", json={
        "item_count": stats1_json['item_count'],
        "feature_count": stats1_json['feature_count'],
        "column_information": stats1_json['column_information']
    })
    assert response.status_code == 200, response.text

    response = client.post(f"/api/proposal/{proposal_id}/discoveries/{discovery_id}/stats", json={
        "item_count": stats2_json['item_count'],
        "feature_count": stats2_json['feature_count'],
        "column_information": stats2_json['column_information']
    })
    assert response.status_code == 200, response.text

    response = client.post(f"/api/proposal/{proposal_id}/discoveries/{discovery_id}/stats", json={
        "item_count": stats3_json['item_count'],
        "feature_count": stats3_json['feature_count'],
        "column_information": stats3_json['column_information']
    })

    assert response.status_code == 200, response.text


def test_discovery_create_numeric2():
    breast_cancer_dataset = load_breast_cancer(return_X_y=False, as_frame=False)
    df = pd.DataFrame(breast_cancer_dataset['data'], columns=breast_cancer_dataset['feature_names'])
    df['target'] = breast_cancer_dataset['target']
    # print("Breast Cancer dataset pandas : {}".format(tabulate(df, headers='keys', tablefmt='psql')))
    df_split = np.array_split(df, 3)

    stats1_json = jsonable_encoder(statistics.get_discovery_statistics(df_split[0]))
    stats2_json = jsonable_encoder(statistics.get_discovery_statistics(df_split[1]))
    stats3_json = jsonable_encoder(statistics.get_discovery_statistics(df_split[2]))
    # print("Resulting DataSetStatistics from diabetes_dataset : {} + type {}".format(stats_df, type(stats_df)))

    proposal_id, discovery_id = create_proposal_and_discovery()

    response = client.post(f"/api/proposal/{proposal_id}/discoveries/{discovery_id}/stats", json={
        "item_count": stats1_json['item_count'],
        "feature_count": stats1_json['feature_count'],
        "column_information": stats1_json['column_information']
    })
    assert response.status_code == 200, response.text

    response = client.post(f"/api/proposal/{proposal_id}/discoveries/{discovery_id}/stats", json={
        "item_count": stats2_json['item_count'],
        "feature_count": stats2_json['feature_count'],
        "column_information": stats2_json['column_information']
    })
    assert response.status_code == 200, response.text

    response = client.post(f"/api/proposal/{proposal_id}/discoveries/{discovery_id}/stats", json={
        "item_count": stats3_json['item_count'],
        "feature_count": stats3_json['feature_count'],
        "column_information": stats3_json['column_information']
    })
    assert response.status_code == 200, response.text


def test_discovery_create_mixed():
    df_titanic = pd.read_csv('./data/train_data_titanic.csv')
    df_split = np.array_split(df_titanic, 3)

    stats1_json = jsonable_encoder(statistics.get_discovery_statistics(df_split[0]))
    stats2_json = jsonable_encoder(statistics.get_discovery_statistics(df_split[1]))
    stats3_json = jsonable_encoder(statistics.get_discovery_statistics(df_split[2]))
    # print("Resulting DataSetStatistics from diabetes_dataset : {} + type {}".format(stats_df, type(stats_df)))

    print("PROPOSAL ID MIXED : {}".format(PROPOSAL_ID_MIXED))

    proposal_id, discovery_id = create_proposal_and_discovery()

    response = client.post(f"/api/proposal/{proposal_id}/discoveries/{discovery_id}/stats", json={
        "item_count": stats1_json['item_count'],
        "feature_count": stats1_json['feature_count'],
        "column_information": stats1_json['column_information']
    })
    assert response.status_code == 200, response.text

    response = client.post(f"/api/proposal/{proposal_id}/discoveries/{discovery_id}/stats", json={
        "item_count": stats2_json['item_count'],
        "feature_count": stats2_json['feature_count'],
        "column_information": stats2_json['column_information']
    })
    assert response.status_code == 200, response.text

    response = client.post(f"/api/proposal/{proposal_id}/discoveries/{discovery_id}/stats", json={
        "item_count": stats3_json['item_count'],
        "feature_count": stats3_json['feature_count'],
        "column_information": stats3_json['column_information']
    })
    assert response.status_code == 200, response.text


def test_discovery_get_all():
    df_titanic = pd.read_csv('./data/train_data_titanic.csv')
    df_split = np.array_split(df_titanic, 3)

    stats1_json = jsonable_encoder(statistics.get_discovery_statistics(df_split[0]))
    stats2_json = jsonable_encoder(statistics.get_discovery_statistics(df_split[1]))
    stats3_json = jsonable_encoder(statistics.get_discovery_statistics(df_split[2]))
    # print("Resulting DataSetStatistics from diabetes_dataset : {} + type {}".format(stats_df, type(stats_df)))

    print("PROPOSAL ID MIXED : {}".format(PROPOSAL_ID_MIXED))

    proposal_id, discovery_id = create_proposal_and_discovery()

    response = client.post(f"/api/proposal/{proposal_id}/discoveries/{discovery_id}/stats", json={
        "item_count": stats1_json['item_count'],
        "feature_count": stats1_json['feature_count'],
        "column_information": stats1_json['column_information']
    })
    assert response.status_code == 200, response.text

    response = client.post(f"/api/proposal/{proposal_id}/discoveries/{discovery_id}/stats", json={
        "item_count": stats2_json['item_count'],
        "feature_count": stats2_json['feature_count'],
        "column_information": stats2_json['column_information']
    })
    assert response.status_code == 200, response.text

    response = client.post(f"/api/proposal/{proposal_id}/discoveries/{discovery_id}/stats", json={
        "item_count": stats3_json['item_count'],
        "feature_count": stats3_json['feature_count'],
        "column_information": stats3_json['column_information']
    })
    assert response.status_code == 200, response.text

    response = client.get(f"/api/proposal/{proposal_id}/discoveries/{discovery_id}/summary")
    assert response.status_code == 200, response.text

    response = response.json()

    df_titanic = pd.read_csv('./data/train_data_titanic.csv')
    stats_df = statistics.get_discovery_statistics(df_titanic)

    assert stats_df.item_count == response['item_count']
    assert stats_df.feature_count == response['feature_count']

    assert stats_df.column_information[0].mean == response['column_information'][0]['mean']
    assert stats_df.column_information[0].min == response['column_information'][0]['min']
    assert stats_df.column_information[0].max == response['column_information'][0]['max']
    assert stats_df.column_information[0].not_na_elements == response['column_information'][0]['not_na_elements']

    assert stats_df.column_information[4].number_categories == response['column_information'][4]['number_categories']
    assert stats_df.column_information[4].value_counts == response['column_information'][4]['value_counts']
    assert stats_df.column_information[4].most_frequent_element == response['column_information'][4][
        'most_frequent_element']
    assert stats_df.column_information[4].frequency == response['column_information'][4]['frequency']


def test_discovery_get_selected():
    diabetes_dataset = sklearn.datasets.load_diabetes(return_X_y=False, as_frame=False)

    df = pd.DataFrame(diabetes_dataset['data'], columns=diabetes_dataset['feature_names'])
    df['target'] = diabetes_dataset['target']
    # print("Diabetes dataset pandas : {}".format(tabulate(df, headers='keys', tablefmt='psql')))
    df_split = np.array_split(df, 3)

    stats1_json = jsonable_encoder(statistics.get_discovery_statistics(df_split[0]))
    stats2_json = jsonable_encoder(statistics.get_discovery_statistics(df_split[1]))
    stats3_json = jsonable_encoder(statistics.get_discovery_statistics(df_split[2]))
    # print("Resulting DataSetStatistics from diabetes_dataset : {} + type {}".format(stats_df, type(stats_df)))

    # proposal_id, discovery_id = create_proposal_and_discovery()
    proposal_id = client.post(
        f"/api/proposal", json={"id": str(uuid4()), "name": "Discovery test proposal"}
    ).json()['id']

    response = client.post(
        f"/api/proposal/{proposal_id}/discoveries",
        json={
            "query": {"hello": "world"},
        }
    )
    discovery_id = response.json()['id']

    response = client.post(f"/api/proposal/{proposal_id}/discoveries/{discovery_id}/stats", json={
        "item_count": stats1_json['item_count'],
        "feature_count": stats1_json['feature_count'],
        "column_information": stats1_json['column_information']
    })
    assert response.status_code == 200, response.text

    response = client.post(f"/api/proposal/{proposal_id}/discoveries/{discovery_id}/stats", json={
        "item_count": stats2_json['item_count'],
        "feature_count": stats2_json['feature_count'],
        "column_information": stats2_json['column_information']
    })
    assert response.status_code == 200, response.text

    response = client.post(f"/api/proposal/{proposal_id}/discoveries/{discovery_id}/stats", json={
        "item_count": stats3_json['item_count'],
        "feature_count": stats3_json['feature_count'],
        "column_information": stats3_json['column_information']
    })

    assert response.status_code == 200, response.text
    response = client.get(f"/api/proposal/{proposal_id}/discoveries/{discovery_id}/summary?features={SELECTED_FEATURES}")
    assert response.status_code == 200, response.text

    response = response.json()

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

#
# def test_plot_discovery():
#     response = client.get(f"/api/proposal/{PROPOSAL_ID_NUMERIC}/discovery?features={SELECTED_FEATURES}")
#     assert response.status_code == 200, response.text
#
#     discovery_summary = response.json()
#     figure_data_lst = []
#
#     data_information = discovery_summary['column_information']
#
#     for data in data_information:
#         try:
#             figure_data = {
#                 "data": data['figure_data']['figure']['data'],
#                 "layout": data['figure_data']['figure']['layout']
#             }
#             figure_data_lst.append(figure_data)
#         except:
#             print(f"Feature {data['title']} does not have figure_data available.")
#
#     for figure in figure_data_lst:
#         # plot_figure_json(figure)
#         print("Plotting is commented out in 'test_plot_discovery_summary_selected_features'!")
