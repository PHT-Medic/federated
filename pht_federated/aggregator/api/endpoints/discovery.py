from fastapi import APIRouter, Depends, HTTPException
from fastapi.encoders import jsonable_encoder

from pht_federated.aggregator.api.schemas.dataset_statistics import *
from pht_federated.aggregator.api.crud.crud_dataset_statistics import datasets
from pht_federated.aggregator.api.discoveries.statistics import *
from collections import Counter
from pht_federated.aggregator.api.discoveries.utility_functions import *


from pht_federated.aggregator.api import dependencies
from sqlalchemy.orm import Session


router = APIRouter()

@router.get("/{proposal_id}/discovery", response_model=DiscoverySummary)
def get_discovery_all(proposal_id: int, feature_name: str, db: Session = Depends(dependencies.get_db)):

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
                feature_lst.append(feature)

        for feature in feature_lst:
            if feature['type'] == 'numeric':

                discovery_summary_json = aggregate_numeric_column(feature_lst, feature)
                aggregated_feature_lst.append(discovery_summary_json)

                if len(feature_lst) == 0:
                    break

            elif feature['type'] == 'categorical':
                value = feature

                discovery_title = ""
                discovery_item_count_not_na = []
                discovery_number_categories = 0
                discovery_value_counts = []

                for feature2 in feature_lst:
                    if feature2['title'] == value['title']:
                        data = feature2

                        discovery_title = data['title']
                        discovery_item_count_not_na.append(data['not_na_elements'])
                        discovery_number_categories += data['number_categories']
                        discovery_value_counts.append(data['value_counts'])

                feature_lst = [x for x in feature_lst if x['title'] != discovery_title]

                c = Counter()
                for d in discovery_value_counts:
                    c.update(d)

                discovery_value_counts = dict(c)
                for entry in discovery_value_counts.items():
                    discovery_value_counts[entry[0]] = round(entry[1] / len(response))

                discovery_most_frequent_element = max(discovery_value_counts, key=discovery_value_counts.get)
                discovery_frequency = discovery_value_counts[discovery_most_frequent_element]
                discovery_number_categories /= len(response)

                discovery_summary_json = {
                    "type": 'categorical',
                    "title": discovery_title,
                    "not_na_elements": sum(discovery_item_count_not_na),
                    "number_categories": discovery_number_categories,
                    "most_frequent_element": discovery_most_frequent_element,
                    "frequency": discovery_frequency,
                    "value_counts": discovery_value_counts
                }

                figure = create_barplot(discovery_summary_json)
                fig_json = plotly.io.to_json(figure)
                obj = json.loads(fig_json)

                figure_schema = {
                    'title': discovery_title,
                    'type': "numeric",
                    'figure': obj
                }

                discovery_figure = DiscoveryFigure(**figure_schema)
                discovery_summary_json['figure_data'] = discovery_figure
                aggregated_feature_lst.append(discovery_summary_json)

                if len(feature_lst) == 0:
                    break

            elif feature['type'] == 'unstructured':

                discovery_summary_json = {
                    "type": 'unstructured'
                }
                aggregated_feature_lst.append(discovery_summary_json)

            elif feature['type'] == 'unique':

                value = feature
                discovery_title = ""
                discovery_no_duplicates = 0

                for feature2 in feature_lst:
                    if feature2['title'] == value['title']:
                        data = feature2
                        discovery_title = data['title']
                        discovery_no_duplicates += data['number_of_duplicates']

                feature_lst = [x for x in feature_lst if x['title'] != discovery_title]
                if len(feature_lst) == 0:
                    break

                discovery_no_duplicates /= len(response)

                discovery_summary_json = {
                    "type": 'unique',
                    "title": discovery_title,
                    "number_of_duplicates": discovery_no_duplicates
                }
                aggregated_feature_lst.append(discovery_summary_json)

            elif feature['type'] == 'equal':

                value = feature
                discovery_title = ""

                for feature2 in feature_lst:
                    if feature2['title'] == value['title']:
                        data = feature2
                        discovery_title = data['title']
                        discovery_equal_value = data['value']

                feature_lst = [x for x in feature_lst if x['title'] != discovery_title]
                if len(feature_lst) == 0:
                    break

                discovery_summary_json = {
                    "type": 'equal',
                    "title": discovery_title,
                    "value": discovery_equal_value
                }
                aggregated_feature_lst.append(discovery_summary_json)



        discovery_feature_count /= len(response)

        discovery_summary_schema = {
            "proposal_id": proposal_id,
            "item_count": discovery_item_count,
            "feature_count": discovery_feature_count,
            "data_information": aggregated_feature_lst
        }

        discovery_summary = DiscoverySummary(**discovery_summary_schema)

        #print("DISCOVERY SUMMARY : {}".format(discovery_summary))

        return discovery_summary

@router.get("/{proposal_id}/discovery_feature", response_model=DiscoverySummary)
def get_discovery_single(proposal_id: int,  feature_name: str, db: Session = Depends(dependencies.get_db)):

    response = datasets.get_all_by_proposal_id(proposal_id, db)
    if not response:
        raise HTTPException(status_code=404, detail=f"Discovery of proposal with id '{proposal_id}' not found.")

    discovery_item_count = 0
    discovery_feature_count = 0
    discovery_item_count_not_na = []
    discovery_mean = []
    discovery_std = []
    discovery_min = []
    discovery_max = []
    discovery_no_duplicates = 0
    discovery_equal_value = ""

    discovery_number_categories = 0
    discovery_value_counts = []

    feature_type = ""

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
                if feature['title'] == feature_name:
                    data = feature
                    if feature['type'] == 'numeric':
                        feature_type = 'numeric'

                        discovery_item_count_not_na.append(data['not_na_elements'])
                        discovery_mean.append((data['mean'], data['mean'] * data['not_na_elements']))
                        discovery_std.append(data['std'])
                        discovery_min.append(data['min'])
                        discovery_max.append(data['max'])

                    elif feature['type'] == 'categorical':
                        feature_type = 'categorical'

                        discovery_item_count_not_na.append(data['not_na_elements'])
                        discovery_number_categories += data['number_categories']
                        discovery_value_counts.append(data['value_counts'])

                    elif feature['type'] == 'unstructured':
                        None

                    elif feature['type'] == 'unique':
                        feature_type = "unique"
                        discovery_no_duplicates += data['number_of_duplicates']

                    elif feature['type'] == 'equal':
                        feature_type = "equal"
                        discovery_equal_value = data['value']

        if feature_type == "categorical":
            c = Counter()
            for d in discovery_value_counts:
                c.update(d)

            discovery_value_counts = dict(c)
            for entry in discovery_value_counts.items():
                discovery_value_counts[entry[0]] = round(entry[1] / len(response))

            discovery_most_frequent_element = max(discovery_value_counts, key=discovery_value_counts.get)
            discovery_frequency = discovery_value_counts[discovery_most_frequent_element]
            discovery_number_categories /= len(response)

            discovery_summary_json_categorical = {
                "type": "categorical",
                "title": feature_name,
                "not_na_elements": sum(discovery_item_count_not_na),
                "number_categories": discovery_number_categories,
                "most_frequent_element": discovery_most_frequent_element,
                "frequency": discovery_frequency,
                "value_counts": discovery_value_counts
            }
            figure = create_barplot(discovery_summary_json_categorical)
            fig_json = plotly.io.to_json(figure)
            obj = json.loads(fig_json)

            figure_schema = {
                'title': feature_name,
                'type': feature_type,
                'figure': obj
            }

            discovery_figure = DiscoveryFigure(**figure_schema)

            discovery_summary_json_categorical['figure_data'] = discovery_figure
            discovery_summary_schema = {
                "proposal_id": proposal_id,
                "item_count": discovery_item_count,
                "feature_count": discovery_feature_count,
                "data_information": [discovery_summary_json_categorical]
            }
        elif feature_type == "numeric":
            discovery_mean_combined = (sum([pair[1] for pair in discovery_mean]) / sum(discovery_item_count_not_na))
            discovery_std = calc_combined_std(discovery_item_count_not_na, discovery_std, discovery_mean,discovery_mean_combined)
            discovery_min = min(discovery_min, default=0)
            discovery_max = max(discovery_max, default=0)
            discovery_feature_count /= len(response)

            discovery_summary_json_numeric = {
                "type": "numeric",
                "title": feature_name,
                "not_na_elements": discovery_item_count_not_na,
                "mean": discovery_mean_combined,
                "std": discovery_std,
                "min": discovery_min,
                "max": discovery_max
            }
            figure = create_dot_plot(discovery_summary_json_numeric)
            fig_json = plotly.io.to_json(figure)
            obj = json.loads(fig_json)

            figure_schema = {
                'title': feature_name,
                'type': feature_type,
                'figure': obj
            }

            discovery_figure = DiscoveryFigure(**figure_schema)
            discovery_summary_json_numeric['figure_data'] = discovery_figure

            discovery_summary_schema = {
                "proposal_id": proposal_id,
                "item_count": discovery_item_count,
                "feature_count": discovery_feature_count,
                "data_information": [discovery_summary_json_numeric]
            }
        elif feature_type == "unstructured":

            discovery_summary_json_unstructured = {
                "type": 'unstructured'
            }
            discovery_summary_schema = {
                "proposal_id": proposal_id,
                "item_count": discovery_item_count,
                "feature_count": discovery_feature_count,
                "data_information": [discovery_summary_json_unstructured]
            }
        elif feature_type == "unique":

            discovery_summary_json_unique = {
                "type": 'unique',
                "title": feature_name,
                "number_of_duplicates": discovery_no_duplicates
            }
            discovery_summary_schema = {
                "proposal_id": proposal_id,
                "item_count": discovery_item_count,
                "feature_count": discovery_feature_count,
                "data_information": [discovery_summary_json_unique]
            }
        elif feature_type == "equal":

            discovery_summary_json_equal = {
                "type": 'equal',
                "title": feature_name,
                "value": discovery_equal_value
            }
            discovery_summary_schema = {
                "proposal_id": proposal_id,
                "item_count": discovery_item_count,
                "feature_count": discovery_feature_count,
                "data_information": [discovery_summary_json_equal]
            }

        discovery_summary = DiscoverySummary(**discovery_summary_schema)

        #print("DISCOVERY SUMMARY : {}".format(discovery_summary))

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

