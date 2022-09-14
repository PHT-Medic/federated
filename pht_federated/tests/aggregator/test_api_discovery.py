import sklearn
import numpy as np
from tabulate import tabulate
from sklearn.datasets import load_diabetes
from fastapi.testclient import TestClient
from pht_federated.aggregator.app import app
from pht_federated.aggregator.api.dependencies import get_db
from pht_federated.aggregator.api.endpoints.discovery import *
from pht_federated.aggregator.api.discoveries import statistics
from sklearn.datasets import load_breast_cancer, load_wine


from pht_federated.tests.aggregator.test_db import override_get_db

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

PROPOSAL_ID_NUMERIC = 42
PROPOSAL_ID_NUMERIC2 = 43
PROPOSAL_ID_MIXED = 44
FEATURE_NAME_NUMERIC = "bmi"
FEATURE_NAME_NUMERIC2 = "Age"
FEATURE_NAME_CATEGORICAL = 'Embarked'


def test_discovery_create_numeric():

    diabetes_dataset = sklearn.datasets.load_diabetes(return_X_y=False, as_frame=False)

    df = pd.DataFrame(diabetes_dataset['data'], columns=diabetes_dataset['feature_names'])
    df['target'] = diabetes_dataset['target']
    #print("Diabetes dataset pandas : {}".format(tabulate(df, headers='keys', tablefmt='psql')))
    df_split = np.array_split(df, 3)


    stats_df1 = statistics.get_discovery_statistics(df_split[0])
    stats_df2 = statistics.get_discovery_statistics(df_split[1])
    stats_df3 = statistics.get_discovery_statistics(df_split[2])
    #print("Resulting DataSetStatistics from diabetes_dataset : {} + type {}".format(stats_df, type(stats_df)))

    stats1_json = jsonable_encoder(stats_df1)
    stats2_json = jsonable_encoder(stats_df2)
    stats3_json = jsonable_encoder(stats_df3)



    response = client.post(f"/api/proposal/{PROPOSAL_ID_NUMERIC}/discovery", json={
                            "n_items" : stats1_json['n_items'],
                            "n_features" : stats1_json['n_features'],
                            "column_information" : stats1_json['column_information']
    })
    assert response.status_code == 200, response.text

    response = client.post(f"/api/proposal/{PROPOSAL_ID_NUMERIC}/discovery", json={
                            "n_items" : stats2_json['n_items'],
                            "n_features" : stats2_json['n_features'],
                            "column_information" : stats2_json['column_information']
    })
    assert response.status_code == 200, response.text

    response = client.post(f"/api/proposal/{PROPOSAL_ID_NUMERIC}/discovery", json={
                            "n_items" : stats3_json['n_items'],
                            "n_features" : stats3_json['n_features'],
                            "column_information" : stats3_json['column_information']
    })
    assert response.status_code == 200, response.text


def test_discovery_create_numeric2():
    breast_cancer_dataset = load_breast_cancer(return_X_y=False, as_frame=False)
    df = pd.DataFrame(breast_cancer_dataset['data'], columns=breast_cancer_dataset['feature_names'])
    df['target'] = breast_cancer_dataset['target']
    #print("Breast Cancer dataset pandas : {}".format(tabulate(df, headers='keys', tablefmt='psql')))
    df_split = np.array_split(df, 3)

    stats_df1 = statistics.get_discovery_statistics(df_split[0])
    stats_df2 = statistics.get_discovery_statistics(df_split[1])
    stats_df3 = statistics.get_discovery_statistics(df_split[2])
    # print("Resulting DataSetStatistics from diabetes_dataset : {} + type {}".format(stats_df, type(stats_df)))

    stats1_json = jsonable_encoder(stats_df1)
    stats2_json = jsonable_encoder(stats_df2)
    stats3_json = jsonable_encoder(stats_df3)

    response = client.post(f"/api/proposal/{PROPOSAL_ID_NUMERIC2}/discovery", json={
        "n_items": stats1_json['n_items'],
        "n_features": stats1_json['n_features'],
        "column_information": stats1_json['column_information']
    })
    assert response.status_code == 200, response.text

    response = client.post(f"/api/proposal/{PROPOSAL_ID_NUMERIC2}/discovery", json={
        "n_items": stats2_json['n_items'],
        "n_features": stats2_json['n_features'],
        "column_information": stats2_json['column_information']
    })
    assert response.status_code == 200, response.text

    response = client.post(f"/api/proposal/{PROPOSAL_ID_NUMERIC2}/discovery", json={
        "n_items": stats3_json['n_items'],
        "n_features": stats3_json['n_features'],
        "column_information": stats3_json['column_information']
    })
    assert response.status_code == 200, response.text


def test_discovery_create_mixed():
    df_titanic = pd.read_csv('./data/train_data_titanic.csv')
    df_split = np.array_split(df_titanic, 3)

    stats_df1 = statistics.get_discovery_statistics(df_split[0])
    stats_df2 = statistics.get_discovery_statistics(df_split[1])
    stats_df3 = statistics.get_discovery_statistics(df_split[2])
    # print("Resulting DataSetStatistics from diabetes_dataset : {} + type {}".format(stats_df, type(stats_df)))

    stats1_json = jsonable_encoder(stats_df1)
    stats2_json = jsonable_encoder(stats_df2)
    stats3_json = jsonable_encoder(stats_df3)

    response = client.post(f"/api/proposal/{PROPOSAL_ID_MIXED}/discovery", json={
        "n_items": stats1_json['n_items'],
        "n_features": stats1_json['n_features'],
        "column_information": stats1_json['column_information']
    })
    assert response.status_code == 200, response.text

    response = client.post(f"/api/proposal/{PROPOSAL_ID_MIXED}/discovery", json={
        "n_items": stats2_json['n_items'],
        "n_features": stats2_json['n_features'],
        "column_information": stats2_json['column_information']
    })
    assert response.status_code == 200, response.text

    response = client.post(f"/api/proposal/{PROPOSAL_ID_MIXED}/discovery", json={
        "n_items": stats3_json['n_items'],
        "n_features": stats3_json['n_features'],
        "column_information": stats3_json['column_information']
    })
    assert response.status_code == 200, response.text

def test_discovery_get_all_aggregated():
    response = client.get(f"/api/proposal/{PROPOSAL_ID_MIXED}/discovery")
    assert response.status_code == 200, response.text

def test_discovery_get_single_aggregated():
    response = client.get(f"/api/proposal/{PROPOSAL_ID_MIXED}/discovery_feature?feature_name={FEATURE_NAME_CATEGORICAL}")
    assert response.status_code == 200, response.text


def test_plot_discovery_summary_single():
    response = client.get(f"/api/proposal/{PROPOSAL_ID_MIXED}/discovery_feature?feature_name={FEATURE_NAME_CATEGORICAL}")
    assert response.status_code == 200, response.text

    discovery_summary = response.json()
    data_information = discovery_summary['data_information'][0]
    print("DATA INFORMATION : {}".format(data_information))

    figure_data = {
        "data": data_information['figure_data']['figure']['data'],
        "layout": data_information['figure_data']['figure']['layout']
    }

    plot_figure_json(figure_data)


def test_plot_discovery_summary_selected_features():
    response = client.get(f"/api/proposal/{PROPOSAL_ID_NUMERIC}/discovery")
    assert response.status_code == 200, response.text

    discovery_summary = response.json()

    available_features = []

    for feature in discovery_summary['data_information']:
        available_features.append(feature['title'])

    #print("AVAILABLE FEATURES : {}".format(available_features))

    selected_features = ['age', 'bmi', 'sex']

    figure_data_lst = []

    data_information = discovery_summary['data_information']

    for data in data_information:
        if data['title'] in selected_features:
            figure_data = {
                "data": data['figure_data']['figure']['data'],
                "layout": data['figure_data']['figure']['layout']
            }
            figure_data_lst.append(figure_data)

    for figure in figure_data_lst:
        plot_figure_json(figure)
        #print("Plotting is commented out!")



'''
def test_delete_discovery():
    response = client.delete(f"/api/proposal/{PROPOSAL_ID}/discovery")
    assert response.status_code == 200, response.text
'''






