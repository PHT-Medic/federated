import sklearn
from sklearn.datasets import load_diabetes
import pandas as pd
from tabulate import tabulate
from fastapi.encoders import jsonable_encoder
import json, plotly

from fastapi.testclient import TestClient
from pht_federated.aggregator.app import app
from pht_federated.aggregator.api.endpoints.dependencies import get_db
from pht_federated.aggregator.api.crud.crud_discovery import *
from pht_federated.aggregator.api.endpoints.discovery import *
from pht_federated.aggregator.api.discoveries import statistics

from pht_federated.tests.aggregator.test_db import override_get_db

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)



def test_data_set_create(proposal_id=42):

    diabetes_dataset = sklearn.datasets.load_diabetes(return_X_y=False, as_frame=False)

    df = pd.DataFrame(diabetes_dataset['data'], columns=diabetes_dataset['feature_names'])
    df['target'] = diabetes_dataset['target']
    #print("Diabetes dataset pandas : {}".format(tabulate(df, headers='keys', tablefmt='psql')))

    stats_df = statistics.get_dataset_statistics(df, proposal_id)
    #print("Resulting DataSetStatistics from diabetes_dataset : {} + type {}".format(stats_df, type(stats_df)))

    stats_dict = jsonable_encoder(stats_df)
    stats_json = json.dumps(stats_dict)
    stats_json_load = json.loads(stats_json)
    #print("STATS DATA : {}".format(stats_json_load))


    response = client.post(f"/api/proposal/{stats_json_load['proposal_id']}/discovery", json={
                            "proposal_id" : stats_json_load['proposal_id'],
                            "item_count" : stats_json_load['item_count'],
                            "feature_count" : stats_json_load['feature_count'],
                            "data_information" : stats_json_load['data_information']
    })


    assert response.status_code == 200, response.text

    data = response.json()
    discovery_id = data["proposal_id"]
    assert discovery_id


def test_discovery_get(proposal_id=42):
    response = client.get(f"/api/proposal/{proposal_id}/discovery")
    assert response.status_code == 200, response.text

    data = response.json()
    assert data["feature_count"] == 11

'''
def test_delete_discovery(proposal_id=42):
    response = client.delete(f"/api/proposal/{proposal_id}/discovery")
    assert response.status_code == 200, response.text
'''


def test_plot_discovery(proposal_id: int = 42, feature_name: str = "bmi"):
    response = client.get(f"/api/proposal/{proposal_id}/discovery")
    assert response.status_code == 200, response.text

    data = response.json()
    for feature in data['data_information']:
        if feature['title'] == feature_name:
            data = feature['figure']['fig_data']


    fig_plotly = plotly.io.from_json(json.dumps(data))
    fig_plotly.show()









