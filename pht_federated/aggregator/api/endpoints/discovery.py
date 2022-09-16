from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.encoders import jsonable_encoder

from pht_federated.aggregator.api.schemas.dataset_statistics import *
from pht_federated.aggregator.api.crud.crud_dataset_statistics import datasets
from pht_federated.aggregator.api.discoveries.utility_functions import *
from pht_federated.aggregator.api import dependencies
from sqlalchemy.orm import Session


router = APIRouter()

@router.get("/{proposal_id}/discovery", response_model=DiscoverySummary)
def get_discovery_all(proposal_id: int, query: Union[str, None] = Query(default=None), db: Session = Depends(dependencies.get_db)):

    response = datasets.get_all_by_proposal_id(proposal_id, db)
    if not response:
        raise HTTPException(status_code=404, detail=f"Discovery of proposal with id '{proposal_id}' not found.")

    feature_lst = []
    aggregated_feature_lst = []

    discovery_item_count = 0
    discovery_feature_count = 0

    if len(response) < 2:
        print("Not able to aggregate a discovery summary over less than 2 DatasetStatistics. Aborted.")
        discovery_summary_schema = {}
        discovery_summary = DiscoverySummary(**discovery_summary_schema)
        return discovery_summary
    else:
        for discovery in response:
            discovery = jsonable_encoder(discovery)
            discovery_item_count += discovery['item_count']
            discovery_feature_count += discovery['feature_count']
            for feature in discovery['column_information']:
                if query:
                    selected_features = query.split(',')
                    if feature['title'] in selected_features:
                        feature_lst.append(feature)
                else:
                    feature_lst.append(feature)

        for feature in feature_lst:
            if feature['type'] == 'numeric':
                discovery_summary_json = aggregate_numeric_column(feature_lst, feature)
                aggregated_feature_lst.append(discovery_summary_json)

            elif feature['type'] == 'categorical':
                discovery_summary_json = aggregate_categorical_column(feature_lst, feature, len(response))
                aggregated_feature_lst.append(discovery_summary_json)

            elif feature['type'] == 'unstructured':
                discovery_summary_json = aggregate_unstructured_data(feature_lst, feature)
                aggregated_feature_lst.append(discovery_summary_json)

            elif feature['type'] == 'unique':
                discovery_summary_json = aggregate_unique_column(feature_lst, feature, len(response))
                aggregated_feature_lst.append(discovery_summary_json)

            elif feature['type'] == 'equal':
                discovery_summary_json = aggregate_equal_column(feature_lst, feature)
                aggregated_feature_lst.append(discovery_summary_json)

            feature_lst = [x for x in feature_lst if x['title'] != feature['title']]

            if len(feature_lst) == 0:
                break

        discovery_feature_count /= len(response)

        discovery_summary_schema = {
            "proposal_id": proposal_id,
            "item_count": discovery_item_count,
            "feature_count": discovery_feature_count,
            "data_information": aggregated_feature_lst
        }
        discovery_summary = DiscoverySummary(**discovery_summary_schema)

        print("DISCOVERY SUMMARY : {}".format(discovery_summary))

        return discovery_summary


@router.delete("/{proposal_id}/discovery", response_model=DiscoveryStatistics)
def delete_discovery_statistics(proposal_id: int, db: Session = Depends(dependencies.get_db)) -> DiscoveryStatistics:
    discovery_del = datasets.delete_by_proposal_id(proposal_id, db)
    if not discovery_del:
        raise HTTPException(status_code=404, detail=f"DatasetStatistics of proposal with id '{proposal_id}' not found.")
    return discovery_del

@router.post("/{proposal_id}/discovery", response_model=DiscoveryStatistics)
def post_discovery_statistics(proposal_id: int, create_msg: StatisticsCreate, db: Session = Depends(dependencies.get_db)) -> DatasetStatistics:
    dataset_statistics = json.loads(create_msg.json())
    discovery_statistics_schema = {
        "proposal_id": proposal_id,
        "item_count": dataset_statistics['item_count'],
        "feature_count": dataset_statistics['feature_count'],
        "column_information": dataset_statistics['column_information']
    }
    discovery_statistics = StatisticsCreate(**discovery_statistics_schema)
    discovery_statistics = datasets.create(db, obj_in=discovery_statistics)
    if not discovery_statistics:
        raise HTTPException(status_code=400, detail=f"DatasetStatistics of proposal with id '{proposal_id}' could not be created.")
    return discovery_statistics

