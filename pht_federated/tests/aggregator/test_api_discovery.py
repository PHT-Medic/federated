import sklearn
from sklearn.datasets import load_diabetes
import pandas as pd
from tabulate import tabulate
from fastapi.encoders import jsonable_encoder
import json

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

    stats_df = statistics.get_dataset_statistics(df)
    print("Resulting DataSetStatistics from diabetes_dataset : {} + type {}".format(stats_df, type(stats_df)))

    stats_dict = jsonable_encoder(stats_df)
    stats_json = json.dumps(stats_dict)

    print(stats_json, type(stats_json))
    stats_json_load = json.loads(stats_json)
    print(stats_json_load['data_information'])

    #test = [{{'title': 'age', 'not_na_elements': 442, 'figure': None, 'type': 'numeric', 'mean': -2.511816797794472e-19, 'std': 0.047619047619047644, 'min': -0.1072256316073538, 'max': 0.11072667545381144}, {'title': 'sex', 'not_na_elements': 442, 'figure': None, 'type': 'numeric', 'mean': 1.2307902309192911e-17, 'std': 0.047619047619047665, 'min': -0.044641636506989144, 'max': 0.05068011873981862}, {'title': 'bmi', 'not_na_elements': 442, 'figure': None, 'type': 'numeric', 'mean': -2.2455642172282577e-16, 'std': 0.047619047619047616, 'min': -0.09027529589850945, 'max': 0.17055522598064407}, {'title': 'bp', 'not_na_elements': 442, 'figure': None, 'type': 'numeric', 'mean': -4.7975700837874414e-17, 'std': 0.047619047619047596, 'min': -0.11239880254408448, 'max': 0.13204361674121307}, {'title': 's1', 'not_na_elements': 442, 'figure': None, 'type': 'numeric', 'mean': -1.3814992387869595e-17, 'std': 0.04761904761904759, 'min': -0.12678066991651324, 'max': 0.15391371315651542}, {'title': 's2', 'not_na_elements': 442, 'figure': None, 'type': 'numeric', 'mean': 3.918434204559376e-17, 'std': 0.047619047619047644, 'min': -0.11561306597939897, 'max': 0.19878798965729408}, {'title': 's3', 'not_na_elements': 442, 'figure': None, 'type': 'numeric', 'mean': -5.7771786349272854e-18, 'std': 0.047619047619047596, 'min': -0.10230705051741597, 'max': 0.18117906039727852}, {'title': 's4', 'not_na_elements': 442, 'figure': None, 'type': 'numeric', 'mean': -9.042540472060099e-18, 'std': 0.047619047619047616, 'min': -0.0763945037500033, 'max': 0.18523444326019867}, {'title': 's5', 'not_na_elements': 442, 'figure': None, 'type': 'numeric', 'mean': 9.293722151839546e-17, 'std': 0.047619047619047616, 'min': -0.12609712083330468, 'max': 0.13359728192191356}, {'title': 's6', 'not_na_elements': 442, 'figure': None, 'type': 'numeric', 'mean': 1.1303175590075123e-17, 'std': 0.047619047619047644, 'min': -0.13776722569000302, 'max': 0.13561183068907107}, {'title': 'target', 'not_na_elements': 442, 'figure': None, 'type': 'numeric', 'mean': 152.13348416289594, 'std': 77.09300453299109, 'min': 25.0, 'max': 346.0}}]



    response = client.post(f"/api/proposal/{7}/discovery", json={
                            "proposal_id" : 7,
                            "item_count" : 422,
                            "feature_count" : 10,
                            "data_information" : stats_json_load['data_information']
    })



    assert response.status_code == 200, response.text

    data = response.json()
    discovery_id = data["proposal_id"]
    assert discovery_id


def test_discovery_get():
    response = client.get(f"/api/proposal/{7}/discovery")
    assert response.status_code == 200, response.text

    data = response.json()
    assert data["feature_count"] == 10


def test_delete_discovery():
    response = client.delete(f"/api/proposal/{7}/discovery")
    assert response.status_code == 200, response.text

    data = response.json()

    assert data["feature_count"] == 10