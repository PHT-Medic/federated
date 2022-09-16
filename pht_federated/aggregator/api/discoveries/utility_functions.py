from pht_federated.aggregator.api.discoveries.statistics import *
from collections import Counter


def aggregate_numeric_column(feature_lst: list, feature: dict):
    value = feature

    discovery_title = ""
    discovery_item_count_not_na = []
    discovery_mean = []
    discovery_std = []
    discovery_min = []
    discovery_max = []

    for feature2 in feature_lst:
        if feature2['title'] == value['title']:
            data = feature2
            discovery_title = data['title']
            discovery_item_count_not_na.append(data['not_na_elements'])
            discovery_mean.append((data['mean'], data['mean'] * data['not_na_elements']))
            discovery_std.append(data['std'])
            discovery_min.append(data['min'])
            discovery_max.append(data['max'])

    discovery_mean_combined = (sum([pair[1] for pair in discovery_mean]) / sum(discovery_item_count_not_na))
    discovery_std = calc_combined_std(discovery_item_count_not_na, discovery_std, discovery_mean, discovery_mean_combined)
    discovery_min = min(discovery_min)
    discovery_max = max(discovery_max)

    discovery_summary_json = {
        "type": 'numeric',
        "title": discovery_title,
        "not_na_elements": sum(discovery_item_count_not_na),
        "mean": discovery_mean_combined,
        "std": discovery_std,
        "min": discovery_min,
        "max": discovery_max
    }

    figure = create_dot_plot(discovery_summary_json)
    fig_json = plotly.io.to_json(figure)
    obj = json.loads(fig_json)

    figure_schema = {
        'title': discovery_title,
        'type': "numeric",
        'figure': obj
    }

    discovery_figure = DiscoveryFigure(**figure_schema)
    discovery_summary_json['figure_data'] = discovery_figure

    return discovery_summary_json

def aggregate_categorical_column(feature_lst: list, feature: dict, num_discoveries: int):
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

    c = Counter()
    for d in discovery_value_counts:
        c.update(d)

    discovery_value_counts = dict(c)
    for entry in discovery_value_counts.items():
        discovery_value_counts[entry[0]] = round(entry[1] / num_discoveries)

    discovery_most_frequent_element = max(discovery_value_counts, key=discovery_value_counts.get)
    discovery_frequency = discovery_value_counts[discovery_most_frequent_element]
    discovery_number_categories /= num_discoveries

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

    return discovery_summary_json

def aggregate_unstructured_data(feature_lst: list, feature: dict):

    discovery_summary_json = {
        "type": 'unstructured'
    }

    return discovery_summary_json

def aggregate_unique_column(feature_lst: list, feature: dict, num_discoveries: int):

    value = feature
    discovery_title = ""
    discovery_no_duplicates = 0

    for feature2 in feature_lst:
        if feature2['title'] == value['title']:
            data = feature2
            discovery_title = data['title']
            discovery_no_duplicates += data['number_of_duplicates']

    discovery_no_duplicates /= num_discoveries

    discovery_summary_json = {
        "type": 'unique',
        "title": discovery_title,
        "number_of_duplicates": discovery_no_duplicates
    }

    return discovery_summary_json

def aggregate_equal_column(feature_lst: list, feature: dict):

    value = feature
    discovery_title = ""
    discovery_equal_value = []

    for feature2 in feature_lst:
        if feature2['title'] == value['title']:
            data = feature2
            discovery_title = data['title']
            discovery_equal_value.append(data['value'])

    if discovery_equal_value.count(discovery_equal_value[0]) == len(discovery_equal_value):
        pass
    else:
        raise Exception(f"Not all discoveries share an equal column considering the feature {discovery_title} ")

    discovery_summary_json = {
        "type": 'equal',
        "title": discovery_title,
        "value": discovery_equal_value
    }

    return discovery_summary_json