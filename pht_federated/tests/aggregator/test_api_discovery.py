import sklearn
from sklearn.datasets import load_diabetes
import pandas as pd
from tabulate import tabulate

from fastapi.testclient import TestClient
from pht_federated.aggregator.app import app
from pht_federated.aggregator.api.endpoints.dependencies import get_db
from pht_federated.aggregator.api.discoveries import statistics

from .test_db__ import override_get_db

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)




def test_data_set_create():

    diabetes_dataset = sklearn.datasets.load_diabetes(return_X_y=False, as_frame=False)

    #print("Diabetes dataset sklearn : {} ".format(diabetes_dataset))

    df = pd.DataFrame(diabetes_dataset['data'], columns=diabetes_dataset['feature_names'])
    df['target'] = diabetes_dataset['target']
    #print("Diabetes dataset pandas : {}".format(tabulate(df, headers='keys', tablefmt='psql')))

    #stats_df = statistics.get_dataset_statistics(df)

    #print("Resulting DataSetStatistics from diabetes_dataset : {} + type {}".format(stats_df, type(stats_df)))


    response = client.post(f"/api/proposal/{1}/discovery", json={
                            "proposal_id" : 1,
                            "count" : 10,
                            "data_information" : { "Color":"Red", "Size":"Big", "Shape":"Round" }
    })


    assert response.status_code == 200, response.text

    data = response.json()
    discovery_id = data["proposal_id"]
    print(discovery_id)
    assert discovery_id


def test_discovery_get():
    response = client.get(f"/api/proposal/{1}/discovery")
    assert response.status_code == 200, response.text

    data = response.json()
    assert data["count"] == 10


def test_delete_discovery():
    response = client.delete(f"/api/proposal/{1}/discovery")
    assert response.status_code == 200, response.text

    data = response.json()

    assert data["count"] == 10