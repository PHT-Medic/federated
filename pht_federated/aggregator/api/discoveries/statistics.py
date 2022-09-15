import pandas as pd
from typing import Optional
from pandas.api.types import is_numeric_dtype, is_bool_dtype
import plotly.express as px
import plotly.io
from plotly.graph_objects import Figure
import json
from pht_federated.aggregator.api.schemas.discovery import DiscoverySummary, DiscoveryFigure
from pht_federated.aggregator.api.schemas.dataset_statistics import DatasetStatistics
import plotly.graph_objects as go


def get_discovery_statistics(dataframe: pd.DataFrame) -> Optional[DatasetStatistics]:
    """
    Computes statistical information of a dataset
    :param dataframe: Dataset as dataframe object
    :return: Dataset statistics
    """
    if not (isinstance(dataframe, pd.DataFrame)):
        raise TypeError("The given dataset needs to be in pandas DataFrame format in order to get DiscoveryStatistcs.")
    shape = dataframe.shape
    description = dataframe.describe(include='all')
    n_items = shape[0]
    n_features = shape[1]
    columns_inf = get_column_information(dataframe, description)


    schema_data = {
        'item_count': n_items,
        'feature_count': n_features,
        'column_information': columns_inf
    }

    statistics = DatasetStatistics(**schema_data)
    return statistics


def get_column_information(dataframe: pd.DataFrame, description: pd.DataFrame) -> dict:
    """
    Extract information out of dataframe and summarize it in a dictionary
    :param dataframe: Dataframe to summarize
    :param description: Dataframe description as dataframe object
    :return: Dictionary with column information
    """
    columns_inf = []
    columns = dataframe.columns.values.tolist()
    for i in range(len(columns)):
        title = columns[i]
        count = description[title]["count"]
        columns_inf.append({
            'title': title
        })
        nan_count = dataframe[title].isna().sum()
        if not(is_numeric_dtype(dataframe[title])) or is_bool_dtype(dataframe[title]):
            # extract information from categorical column
            columns_inf[i]['not_na_elements'] = count - nan_count
            columns_inf = process_categorical_column(dataframe, columns_inf, i, description, title)
        else:
            # extract information from numerical column
            zero_count = dataframe[title][dataframe[title]==0].count()
            undefined_count = nan_count + zero_count
            columns_inf[i]['not_na_elements'] = count - undefined_count
            columns_inf = process_numerical_column(columns_inf, i, description, title)


    return columns_inf


def process_numerical_column(columns_inf: dict, i: int, description: pd.DataFrame, title: str) -> dict:
    """
    Extract information from numerical column and create plot of column data
    :param dataframe: discovery as dataframe object
    :param columns_inf: array containing all information of different columns
    :param i: current column index
    :param description: description of all dataset columns
    :param title: title of column with index i
    :return: array with column information, key and json to save chart in cache
    """
    columns_inf[i]['type'] = "numeric"
    columns_inf[i]['mean'] = description[title]["mean"]
    columns_inf[i]['std'] = description[title]["std"]
    columns_inf[i]['min'] = description[title]["min"]
    columns_inf[i]['max'] = description[title]["max"]
    return columns_inf


def process_categorical_column(dataframe: pd.DataFrame, columns_inf: dict, i: int, description: pd.DataFrame, title: str) -> dict:
    """
    Extract information from categorical column and create plot of column data
    :param dataframe: discovery as dataframe object
    :param columns_inf: array containing all information of different columns
    :param i: current column index
    :param description: description of all dataset columns
    :param title: title of column with index i
    :return: array with column information, key and json to save chart in cache
    """
    count = columns_inf[i]['not_na_elements']
    unique = description[title]["unique"]
    top = description[title]["top"]
    freq = description[title]["freq"]


    # if every entry has a unique value (or at most 50 values are given multiple times)
    if count - 50 < unique <= count:
        column_type = "unique"
        columns_inf[i]['type'] = column_type
        columns_inf[i]['title'] = title
        columns_inf[i]['number_of_duplicates'] = count - unique
    else:
        # all elements of column have the same value
        if unique == 1:
            column_type = "equal"
            columns_inf[i]['title'] = title
            columns_inf[i]['value'] = top
            # if column has just one equal value, no plot is created

        else:
            value_counts = dataframe[title].value_counts().to_dict()
            column_type = "categorical"
            columns_inf[i]['number_categories'] = unique
            columns_inf[i]['most_frequent_element'] = top
            columns_inf[i]['frequency'] = freq
            columns_inf[i]['value_counts'] = value_counts

        columns_inf[i]['type'] = column_type

    return columns_inf

def create_figure(fig: Figure) -> DiscoveryFigure:
    """
    Create DataSetFigure-Object of a plotly figure
    :param fig: Plotly figure
    :return: DataSetFigure-Object with JSON-representation of plotly figure
    """
    fig_json = plotly.io.to_json(fig)
    obj = json.loads(fig_json)
    figure = DiscoveryFigure(fig_data=obj)
    #print("Figure  data : {}".format(figure.fig_data))
    return figure

def plot_figure_json(json_data: dict):
    fig_plotly = plotly.io.from_json(json.dumps(json_data))
    fig_plotly.show()


def create_dot_plot(json_data: dict) -> Figure:

    feature_name = [json_data['title']]
    mean = [json_data['mean']]
    std_plus = [json_data['mean'] + json_data['std']]
    std_minus = [json_data['mean'] - json_data['std']]
    min_value = [json_data['min']]
    max_value = [json_data['max']]

    trace_mean = go.Scatter(
        x=feature_name,
        y=mean,
        marker=dict(color="blue", size=12),
        mode='markers',
        name="Mean"
    )
    trace_std_plus = go.Scatter(
        x=feature_name,
        y=std_plus,
        marker=dict(color="red", size=12),
        mode='markers',
        name="Standard Deivation"
    )
    trace_std_minus = go.Scatter(
        x=feature_name,
        y=std_minus,
        marker=dict(color="red", size=12),
        mode='markers',
        name="Standard Deviation -",
        showlegend=False
    )
    trace_min = go.Scatter(
        x=feature_name,
        y=min_value,
        marker=dict(color="green", size=12),
        mode='markers',
        name="Min-Value"
    )
    trace_max = go.Scatter(
        x=feature_name,
        y=max_value,
        marker=dict(color="green", size=12),
        mode='markers',
        name="Max-Value"
    )

    data = [trace_mean, trace_std_plus, trace_std_minus, trace_min, trace_max]
    layout = go.Layout(
        title=f'Dot-Plot over Discovery Results of Numerical Feature : "{feature_name[0]}"',
        xaxis_title="Feature Name",
        yaxis_title="Value"
    )
    fig = go.Figure(data=data, layout=layout)

    return fig

def create_barplot(json_data: dict) -> Figure:

    value_counts = json_data['value_counts']
    feature_title = json_data['title']
    names_col = ["Value", "Count"]
    dat = value_counts.items()
    plot_df = pd.DataFrame(data=dat, columns=names_col)

    bar = px.bar(plot_df, x='Count', y='Value', title=f'Value Counts of Categorical Feature : "{feature_title}"', color=dat)

    return bar


def calc_combined_std(sample_size: list, std_lst: list, means: list, combined_mean: float) -> float:

    nominator = []

    for i in range(len(std_lst)):
        nominator.append(sample_size[i] * pow(std_lst[i], 2) + sample_size[i] * pow((means[i][0] - combined_mean), 2))

    combined_std = sum(nominator) / sum(sample_size)

    return combined_std


