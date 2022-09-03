import sklearn
from sklearn.datasets import load_diabetes
from fastapi.testclient import TestClient
from pht_federated.aggregator.app import app
from pht_federated.aggregator.api.dependencies import get_db
from pht_federated.aggregator.api.endpoints.discovery import *
from pht_federated.aggregator.api.discoveries import statistics


from pht_federated.tests.aggregator.test_db import override_get_db

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

PROPOSAL_ID = 42
FEATURE_NAME = "bmi"


def test_discovery_create():

    diabetes_dataset = sklearn.datasets.load_diabetes(return_X_y=False, as_frame=False)

    df = pd.DataFrame(diabetes_dataset['data'], columns=diabetes_dataset['feature_names'])
    df['target'] = diabetes_dataset['target']
    #print("Diabetes dataset pandas : {}".format(tabulate(df, headers='keys', tablefmt='psql')))

    stats_df = statistics.get_discovery_statistics(df)
    #print("Resulting DataSetStatistics from diabetes_dataset : {} + type {}".format(stats_df, type(stats_df)))

    stats_dict = jsonable_encoder(stats_df)
    stats_json = json.dumps(stats_dict)
    stats_json_load = json.loads(stats_json)

    response = client.post(f"/api/proposal/{PROPOSAL_ID}/discovery", json={
                            "n_items" : stats_json_load['n_items'],
                            "n_features" : stats_json_load['n_features'],
                            "column_information" : stats_json_load['column_information']
    })
    assert response.status_code == 200, response.text

    response = client.post(f"/api/proposal/{PROPOSAL_ID}/discovery", json={
                            "n_items" : int(stats_json_load['n_items']) + 1,
                            "n_features" : int(stats_json_load['n_features']) + 1,
                            "column_information" : stats_json_load['column_information']
    })
    assert response.status_code == 200, response.text



def test_discovery_get_single_aggregated():
    response = client.get(f"/api/proposal/{PROPOSAL_ID}/discovery?feature_name={FEATURE_NAME}")
    assert response.status_code == 200, response.text

def test_discovery_get_all_aggregated():
    response = client.get(f"/api/proposal/{PROPOSAL_ID}/discovery_all")
    assert response.status_code == 200, response.text


def test_plot_discovery_summary_single():
    response = client.get(f"/api/proposal/{PROPOSAL_ID}/discovery?feature_name={FEATURE_NAME}")
    assert response.status_code == 200, response.text

    discovery_summary = response.json()
    #plot_discovery_summary_single(discovery_summary)

def test_plot_discovery_summary_selected_features():
    response = client.get(f"/api/proposal/{PROPOSAL_ID}/discovery_all")
    assert response.status_code == 200, response.text

    discovery_summary = response.json()
    print_available_features(discovery_summary)

    selected_features = ['age', 'bmi', 'sex']

    plot_discovery_summary_selected_features(discovery_summary, selected_features)


'''
def test_delete_discovery():
    response = client.delete(f"/api/proposal/{PROPOSAL_ID}/discovery")
    assert response.status_code == 200, response.text
'''






