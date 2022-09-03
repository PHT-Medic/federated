import pandas as pd
from typing import Optional
from pandas.api.types import is_numeric_dtype, is_bool_dtype
import plotly.express as px
import plotly.io
from plotly.graph_objects import Figure
import json
from pht_federated.aggregator.api.schemas.discovery import DiscoveryStatistics, DiscoverySummary, DiscoveryFigure
import plotly.graph_objects as go
from plotly.subplots import make_subplots

def get_discovery_statistics(dataframe: pd.DataFrame, proposal_id: int) -> Optional[DiscoveryStatistics]:
    """
    Computes statistical information of a dataset
    :param dataframe: Dataset as dataframe object
    :return: Dataset statistics
    """
    if not (isinstance(dataframe, pd.DataFrame)):
        raise TypeError
    shape = dataframe.shape
    description = dataframe.describe(include='all')

    n_items = shape[0]
    n_features = shape[1]
    columns_inf = get_column_information(dataframe, description)


    schema_data = {
        'proposal_id': proposal_id,
        'item_count': n_items,
        'feature_count': n_features,
        'data_information': columns_inf
    }

    statistics = DiscoverySummary(**schema_data)
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
            columns_inf = process_categorical_column(columns_inf, i, description, title)
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


def process_categorical_column(columns_inf: dict, i: int, description: pd.DataFrame, title: str) -> dict:
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
        if unique != count:
            columns_inf[i]['number_of_duplicates'] = count - unique
    else:
        # all elements of column have the same value
        if unique == 1:
            column_type = "equal"
            columns_inf[i]['value'] = top
            # if column has just one equal value, no plot is created

        else:
            column_type = "categorical"
            columns_inf[i]['number_categories'] = unique
            columns_inf[i]['most_frequent_element'] = top
            columns_inf[i]['frequency'] = freq

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

def plot_figure(fig: Figure):
    fig.show()


def create_errorbar(json_data: dict) -> Figure:

    fig = go.Figure()

    trace1 = go.Scatter(
        x=[json_data['title']],
        y=[json_data['mean']],
        error_y=dict(
            type='data',  # value of error bar given in data coordinates
            array=[json_data['std']],
            visible=True)
    )
    trace2 = go.Scatter(
        x=[json_data['title']],
        y=[json_data['mean']],
        #line=dict(color="#ffe476"),
        error_y=dict(
            type='data',  # value of error bar given in data coordinates
            symmetric=False,
            value=abs(json_data['max']),
            valueminus=abs(json_data['min']),
            visible=True)
    )

    fig.add_trace(trace1)
    fig.add_trace(trace2)

    #fig.show()

    return fig

def create_errorbar2(json_data: dict) -> Figure:

    fig = go.Figure()

    trace1 = go.Scatter(
        x=[json_data['title']],
        y=[json_data['mean']],
        error_y=dict(
            type='data',  # value of error bar given in data coordinates
            array=[json_data['std']],
            visible=True)
    )
    trace2 = go.Scatter(
        x=[json_data['title']],
        y=[json_data['mean']],
        #line=dict(color="#ffe476"),
        error_y=dict(
            type='data',  # value of error bar given in data coordinates
            symmetric=False,
            value=abs(json_data['max']),
            valueminus=abs(json_data['min']),
            visible=True)
    )

    fig.add_trace(trace1)
    fig.add_trace(trace2)

    fig.show()

    return fig