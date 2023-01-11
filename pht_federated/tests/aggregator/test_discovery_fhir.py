import os
import numpy as np
import pandas as pd
from fhir_kindling import FhirServer
from dotenv import load_dotenv, find_dotenv
from fhir_kindling.serde.flatten import flatten_resources
import pytest
from starlette.testclient import TestClient
from fastapi.encoders import jsonable_encoder
from uuid import uuid4

from pht_federated.aggregator.api.dependencies import get_db
from pht_federated.aggregator.app import app
from pht_federated.aggregator.services.discovery import statistics
from pht_federated.tests.aggregator.test_db import override_get_db

app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)

client = TestClient(app)
PROPOSAL_ID_NUMERIC = uuid4()
PROPOSAL_ID_MIXED = uuid4()


def get_available_resources(fhir_server, ordered_asc):
    if ordered_asc:
        resourceList = sorted(fhir_server.summary().available_resources, key=lambda x: x.count)
    else:
        resourceList = sorted(fhir_server.summary().available_resources, key=lambda x: x.count, reverse=True)
    return resourceList


def remove_unnecessary_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    As not all information of a FHIR-Resource is necessary, this function discards those columns with matching regex
    e.g general data such as meta or ids
    :param df: input dataframe containing fhir resources as a dataframe
    :return: same dataframe but with less columns
    """
    remove_column_regex = 'meta|' \
                          'id|' \
                          'text_status|' \
                          'text_div|' \
                          'resourceType'

    df = df[df.columns.drop(list(df.filter(regex=remove_column_regex)))]
    return df


def get_fhir_df(fhir_server) -> dict:
    resourceList = get_available_resources(fhir_server, ordered_asc=True)
    dataframe_dict = dict()
    for resource in resourceList:
        fhir_df = get_resources_as_df(fhir_server, resource.resource)
        fhir_df = remove_unnecessary_columns(fhir_df)
        dataframe_dict[resource.resource] = fhir_df
    return dataframe_dict


def get_resources_as_df(fhir_server, resourceTyp) -> pd.DataFrame:
    # Connect with basic auth
    # basic_auth_server = FhirServer(api_address=fhir_dict.api_address,username=fhir_dict.username,password=fhir_dict.password ,timeout=36000)
    fhir_server.timeout = None
    query_results = fhir_server.query(resourceTyp, output_format="json").all()
    flatted_resources = flatten_resources(query_results.resources)
    return flatted_resources


def create_proposal_and_discovery():
    response = client.post(
        f"/api/proposal", json={"id": str(uuid4()), "name": "Discovery test proposal"}
    )
    proposal_id = response.json()["id"]
    response = client.post(
        f"/api/proposal/{proposal_id}/discoveries",
        json={
            "query": {"hello": "world"},
        },
    )
    discovery_id = response.json()["id"]
    return proposal_id, discovery_id


@pytest.fixture
def fhir_credentials():
    load_dotenv(find_dotenv())
    url = os.getenv("FHIR_SERVER")
    user = os.getenv("FHIR_USER")
    password = os.getenv("FHIR_PASSWORD")

    return url, user, password


def test_init(fhir_credentials):
    server = FhirServer(
        api_address=fhir_credentials[0],
        username=fhir_credentials[1],
        password=fhir_credentials[2]
    )
    fhir_dic_1 = get_fhir_df(server)
    fhir_dic_2 = get_fhir_df(server)
    fhir_dic_3 = get_fhir_df(server)

    stats1_json = jsonable_encoder(statistics.get_discovery_statistics(fhir_dic_1, "fhir"))
    stats2_json = jsonable_encoder(statistics.get_discovery_statistics(fhir_dic_2, "fhir"))
    stats3_json = jsonable_encoder(statistics.get_discovery_statistics(fhir_dic_3, "fhir"))

    proposal_id, discovery_id = create_proposal_and_discovery()
    proposal_id = client.post(
        f"/api/proposal",
        json={"id": str(PROPOSAL_ID_NUMERIC), "name": "Discovery test proposal"},
    ).json()["id"]

    response = client.post(
        f"/api/proposal/{proposal_id}/discoveries",
        json={
            "query": {"hello": "world"},
        },
    )
    discovery_id = response.json()["id"]
    response = client.post(
        f"/api/proposal/{proposal_id}/discoveries/{discovery_id}/stats",
        json={
            "statistics": stats1_json["statistics"]
        },
    )
    assert response.status_code == 200, response.text

    response = client.post(
        f"/api/proposal/{proposal_id}/discoveries/{discovery_id}/stats",
        json={
            "statistics": stats2_json["statistics"]
        },
    )
    assert response.status_code == 200, response.text

    response = client.post(
        f"/api/proposal/{proposal_id}/discoveries/{discovery_id}/stats",
        json={
            "statistics": stats3_json["statistics"]
        },
    )

    assert response.status_code == 200, response.text


def combine_fhir_dic(dics):
    total_dic = dics.pop(1)
    for dic in dics:
        for key in dic:
            if key in total_dic:
                total_dic[key] = total_dic[key].append(dic[key])
    return total_dic


def test_combine_fhir(fhir_credentials):
    server = FhirServer(
        api_address=fhir_credentials[0],
        username=fhir_credentials[1],
        password=fhir_credentials[2]
    )
    fhir_dic_1 = get_fhir_df(server)
    print("fhir_dic_1:")
    for x in fhir_dic_1:
        print(f"{x}:{len(fhir_dic_1[x])}")

    fhir_dic_2 = get_fhir_df(server)
    print("\nfhir_dic_2:")
    for x in fhir_dic_2:
        print(f"{x}:{len(fhir_dic_2[x])}")

    fhir_dic_3 = get_fhir_df(server)
    print("\nfhir_dic_3:")
    for x in fhir_dic_3:
        print(f"{x}:{len(fhir_dic_3[x])}")

    total_dic = combine_fhir_dic([fhir_dic_1, fhir_dic_2, fhir_dic_3])
    print("\ntotal_dic:")
    for x in total_dic:
        print(f"{x}:{len(total_dic[x])}")


def test_discovery_get_all(fhir_credentials):
    server = FhirServer(
        api_address=fhir_credentials[0],
        username=fhir_credentials[1],
        password=fhir_credentials[2]
    )
    fhir_dic_1 = get_fhir_df(server)
    fhir_dic_2 = get_fhir_df(server)
    fhir_dic_3 = get_fhir_df(server)

    stats1_json = jsonable_encoder(statistics.get_discovery_statistics(fhir_dic_1, "fhir"))
    stats2_json = jsonable_encoder(statistics.get_discovery_statistics(fhir_dic_2, "fhir"))
    stats3_json = jsonable_encoder(statistics.get_discovery_statistics(fhir_dic_3, "fhir"))
    # print("Resulting DataSetStatistics from diabetes_dataset : {} + type {}".format(stats_df, type(stats_df)))

    print("PROPOSAL ID MIXED : {}".format(PROPOSAL_ID_MIXED))

    proposal_id, discovery_id = create_proposal_and_discovery()

    response = client.post(
        f"/api/proposal/{proposal_id}/discoveries/{discovery_id}/stats",
        json={
            "statistics": stats1_json["statistics"]
        },
    )
    assert response.status_code == 200, response.text

    response = client.post(
        f"/api/proposal/{proposal_id}/discoveries/{discovery_id}/stats",
        json={
            "statistics": stats2_json["statistics"]
        },
    )
    assert response.status_code == 200, response.text

    response = client.post(
        f"/api/proposal/{proposal_id}/discoveries/{discovery_id}/stats",
        json={
            "statistics": stats3_json["statistics"]
        },
    )
    assert response.status_code == 200, response.text

    response = client.get(
        f"/api/proposal/{proposal_id}/discoveries/{discovery_id}/summary"
    )
    print("Response:", response)
    assert response.status_code == 200, response.text

    response = response.json()
    total_dic = combine_fhir_dic([fhir_dic_1, fhir_dic_2, fhir_dic_3])
    stats_df = statistics.get_discovery_statistics(total_dic, "fhir")
    # test for same resource names
    agg_resources_names = response["summary"][0]["discovery_resource_types"]
    test_resources_names = stats_df.statistics[0].resource_types
    assert len(agg_resources_names) == len(test_resources_names)
    for x in agg_resources_names:
        assert x in test_resources_names

    for resource_stats in stats_df.statistics[0].server_statistics:
        for resources_agg in response["summary"][0]["discovery_server_statistics"]:
            if resource_stats.resource_name == resources_agg["resource_name"]:
                assert resource_stats.resource_statistics.item_count == \
                       resources_agg["resource_statistics"]["item_count"]
                assert resource_stats.resource_statistics.feature_count == \
                       resources_agg["resource_statistics"]["feature_count"]

                if resource_stats.resource_name == "Immunization":
                    print()
                    assert (
                            resource_stats.resource_statistics.column_information[0].type ==
                            resources_agg["resource_statistics"]["column_information"][0]["type"]
                    )
                    assert (
                            resource_stats.resource_statistics.column_information[0].title ==
                            resources_agg["resource_statistics"]["column_information"][0]["title"]
                    )
                    assert (
                            resource_stats.resource_statistics.column_information[0].value ==
                            resources_agg["resource_statistics"]["column_information"][0]["value"]
                    )
                if resource_stats.resource_name == "Patient":
                    print()
                    assert (
                            resource_stats.resource_statistics.column_information[0].type ==
                            resources_agg["resource_statistics"]["column_information"][0]["type"]
                    )
                    assert (
                            resource_stats.resource_statistics.column_information[0].title ==
                            resources_agg["resource_statistics"]["column_information"][0]["title"]
                    )
                    print()
                    assert (
                            resource_stats.resource_statistics.column_information[0].number_of_duplicates ==
                            resources_agg["resource_statistics"]["column_information"][0]["number_of_duplicates"]
                    )
                if resource_stats.resource_name == "Condition":
                    print()
                    assert (
                            resource_stats.resource_statistics.column_information[0].type ==
                            resources_agg["resource_statistics"]["column_information"][0]["type"]
                    )
                    assert (
                            resource_stats.resource_statistics.column_information[0].title ==
                            resources_agg["resource_statistics"]["column_information"][0]["title"]
                    )
                    assert (
                            resource_stats.resource_statistics.column_information[0].value ==
                            resources_agg["resource_statistics"]["column_information"][0]["value"]
                    )
