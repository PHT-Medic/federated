import json
import pandas as pd
import sklearn
from sklearn.datasets import load_diabetes
from fastapi.testclient import TestClient
from pht_federated.aggregator.app import app
from pht_federated.aggregator.api.dependencies import get_db
from pht_federated.aggregator.api.endpoints.discovery import *
from pht_federated.aggregator.api.discoveries import statistics
import plotly.graph_objects as go

from pht_federated.tests.aggregator.test_db import override_get_db

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

PROPOSAL_ID = 42
FEATURE_NAME = "bmi"


def test_data_set_create():

    diabetes_dataset = sklearn.datasets.load_diabetes(return_X_y=False, as_frame=False)

    df = pd.DataFrame(diabetes_dataset['data'], columns=diabetes_dataset['feature_names'])
    df['target'] = diabetes_dataset['target']
    #print("Diabetes dataset pandas : {}".format(tabulate(df, headers='keys', tablefmt='psql')))

    stats_df = statistics.get_discovery_statistics(df, PROPOSAL_ID)
    #print("Resulting DataSetStatistics from diabetes_dataset : {} + type {}".format(stats_df, type(stats_df)))

    stats_dict = jsonable_encoder(stats_df)
    stats_json = json.dumps(stats_dict)
    stats_json_load = json.loads(stats_json)

    response = client.post(f"/api/proposal/{stats_json_load['proposal_id']}/discovery", json={
                            "proposal_id" : stats_json_load['proposal_id'],
                            "item_count" : stats_json_load['item_count'],
                            "feature_count" : stats_json_load['feature_count'],
                            "data_information" : stats_json_load['data_information']
    })

    assert response.status_code == 200, response.text

    response = client.post(f"/api/proposal/{stats_json_load['proposal_id']}/discovery", json={
                            "proposal_id" : stats_json_load['proposal_id'],
                            "item_count" : int(stats_json_load['item_count']) + 1,
                            "feature_count" : int(stats_json_load['feature_count']) + 1,
                            "data_information" : stats_json_load['data_information']
    })


    assert response.status_code == 200, response.text

    data = response.json()
    discovery_id = data["proposal_id"]
    assert discovery_id


def test_discovery_get():
    response = client.get(f"/api/proposal/{PROPOSAL_ID}/discovery?query_all=True")
    #print("Resulting Response : {}".format(response.json()))
    assert response.status_code == 200, response.text


'''
def test_delete_discovery():
    response = client.delete(f"/api/proposal/{PROPOSAL_ID}/discovery")
    assert response.status_code == 200, response.text
'''

'''
def test_plot_discovery():
    response = client.get(f"/api/proposal/{PROPOSAL_ID}/discovery?query_all=True")
    assert response.status_code == 200, response.text

    #print("RESPONSE : {} and type : {}".format(response.json(), type(response.json())))

    for discovery in response.json():
        for feature in discovery['data_information']:
            if feature['title'] == FEATURE_NAME:
                data = feature

    discovery_summary_json = {
        "feature_name": FEATURE_NAME,
        "discovery_mean" : data['mean'],
        "discovery_std" : data['std'],
        "discovery_min" : data['min'],
        "discovery_max" : data['max']
    }

    plot_errorbar(discovery_summary_json)

'''

def test_plot_discovery_aggregated():

    response = client.get(f"/api/proposal/{PROPOSAL_ID}/discovery/plot_single?feature_name={FEATURE_NAME}")
    assert response.status_code == 200, response.text

'''
def test_plot_discovery_aggregated_all_features():

    response = client.get(f"/api/proposal/{PROPOSAL_ID}/discovery/plot")
    assert response.status_code == 200, response.text
'''






