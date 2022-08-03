import sklearn
from sklearn.datasets import load_diabetes
import pandas as pd

from fastapi.testclient import TestClient
from pht_federated.aggregator.main import app
from pht_federated.aggregator.api.endpoints.dependencies import get_db
from pht_federated.aggregator.api.discoveries import statistics

from .test_db__ import override_get_db

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)




def test_data_set_create():

    diabetes_dataset = sklearn.datasets.load_diabetes(return_X_y=False, as_frame=False)

    diabetes_dataset_pandas = pd.DataFrame(diabetes_dataset.data, columns=diabetes_dataset.feature_names)

    print("Diabetes dataset sklearn : {}".format(diabetes_dataset_pandas))

    #stats_df = pd.DataFrame(diabetes_dataset)

    #print("Diabetes dataset pandas : {}".format(stats_df))

    stats = statistics.get_dataset_statistics(diabetes_dataset_pandas)

    #print("Resulting DataSetStatistics from diabetes_dataset : {} + type {}".format(stats, type(stats)))

    '''response = client.post("/api/datasets", json={
        "name": "test data set",
        "data_type": "tabular",
        "storage_type": "fhir"

    })'''



    response = client.post("/api/discoveries", json={
                            "proposal_id" : "1",
                            "count" : "10",
                            "data_information" : { "Color":"Red", "Size":"Big", "Shape":"Round" }
    })


    assert response.status_code == 200, response.text

    data = response.json()
    discovery_id = data["id"]
    assert discovery_id


def test_discovery_get():
    response = client.get(f"/api/discovery/{1}")
    assert response.status_code == 200, response.text

    data = response.json()
    assert data["name"] == "test data set"


def test_get_all_discoveries():
    response = client.get("/api/discovery")
    assert response.status_code == 200, response.text
    data = response.json()

    assert len(data) >= 1