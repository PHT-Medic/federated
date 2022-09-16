from pht_federated.aggregator.api.discoveries.statistics import *



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

    feature_lst = [x for x in feature_lst if x['title'] != discovery_title]

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


def aggregate_categorical_column(feature_lst: list, feature: dict):
    None

