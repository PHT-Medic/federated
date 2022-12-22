from typing import Optional

import pandas as pd
import plotly.io
from pandas.api.types import is_bool_dtype, is_numeric_dtype
from plotly.graph_objs import Figure

from pht_federated.aggregator.schemas.dataset_statistics import \
    DatasetStatistics
from pht_federated.aggregator.schemas.discovery import DiscoveryFigure


def get_discovery_statistics(dataframe: pd.DataFrame) -> Optional[DatasetStatistics]:
    """
    Computes statistical information of a dataset
    :param dataframe: Dataset as dataframe object
    :return: Dataset statistics
    """
    if not (isinstance(dataframe, pd.DataFrame)):
        raise TypeError(
            "The given dataset needs to be in pandas DataFrame format in order to get Discovery statistcs."
        )
    shape = dataframe.shape
    description = dataframe.describe(include="all")
    n_items = shape[0]
    n_features = shape[1]
    columns_inf = get_column_information(dataframe, description)

    schema_data = {
        "item_count": n_items,
        "feature_count": n_features,
        "column_information": columns_inf,
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
        columns_inf.append({"title": title})
        nan_count = dataframe[title].isna().sum()
        if not (is_numeric_dtype(dataframe[title])) or is_bool_dtype(dataframe[title]):
            # extract information from categorical column
            columns_inf[i]["not_na_elements"] = count - nan_count
            columns_inf = process_categorical_column(
                dataframe, columns_inf, i, description, title
            )
        else:
            # extract information from numerical column
            zero_count = dataframe[title][dataframe[title] == 0].count()
            undefined_count = nan_count + zero_count
            columns_inf[i]["not_na_elements"] = count - undefined_count
            columns_inf = process_numerical_column(columns_inf, i, description, title)

    return columns_inf


def process_numerical_column(
    columns_inf: dict, i: int, description: pd.DataFrame, title: str
) -> dict:
    """
    Extract information from numerical column and create plot of column data
    :param dataframe: discovery as dataframe object
    :param columns_inf: array containing all information of different columns
    :param i: current column index
    :param description: description of all dataset columns
    :param title: title of column with index i
    :return: array with column information, key and json to save chart in cache
    """
    columns_inf[i]["type"] = "numeric"
    columns_inf[i]["mean"] = description[title]["mean"]
    columns_inf[i]["std"] = description[title]["std"]
    columns_inf[i]["min"] = description[title]["min"]
    columns_inf[i]["max"] = description[title]["max"]
    return columns_inf


def process_categorical_column(
    dataframe: pd.DataFrame,
    columns_inf: dict,
    i: int,
    description: pd.DataFrame,
    title: str,
) -> dict:
    """
    Extract information from categorical column and create plot of column data
    :param dataframe: discovery as dataframe object
    :param columns_inf: array containing all information of different columns
    :param i: current column index
    :param description: description of all dataset columns
    :param title: title of column with index i
    :return: array with column information, key and json to save chart in cache
    """
    count = columns_inf[i]["not_na_elements"]
    unique = description[title]["unique"]
    top = description[title]["top"]
    freq = description[title]["freq"]

    # if every entry has a unique value (or at most 50 values are given multiple times)
    if count - percentage(95, count) < unique <= count:
        column_type = "unique"
        columns_inf[i]["type"] = column_type
        columns_inf[i]["title"] = title
        columns_inf[i]["number_of_duplicates"] = count - unique
    else:
        # all elements of column have the same value
        if unique == 1:
            column_type = "equal"
            columns_inf[i]["title"] = title
            columns_inf[i]["value"] = top
            # if column has just one equal value, no plot is created

        else:
            value_counts = dataframe[title].value_counts().to_dict()
            column_type = "categorical"
            columns_inf[i]["number_categories"] = unique
            columns_inf[i]["most_frequent_element"] = top
            columns_inf[i]["frequency"] = freq
            columns_inf[i]["value_counts"] = value_counts

        columns_inf[i]["type"] = column_type

    return columns_inf


def create_figure(fig: Figure) -> DiscoveryFigure:
    """
    Create DataSetFigure-Object of a plotly figure
    :param fig: Plotly figure
    :return: DataSetFigure-Object with JSON-representation of plotly figure
    """
    fig_json = plotly.io.to_json(fig)
    figure = DiscoveryFigure.parse_raw(fig_json)
    # print("Figure  data : {}".format(figure.fig_data))
    return figure


def calc_combined_std(
    sample_size: list, std_lst: list, means: list, combined_mean: float
) -> float:
    """
    Computes combined standard deviation of multiple different DatasetStatistics
    :param sample_size: list of num of samples for each dataset
    :param std_lst: list of standard deviations for each dataset
    :param means: list of means for each dataset
    :param combined_mean: combined mean value for the number of datasets
    :return: combined standard deviation
    """
    nominator = []

    for i in range(len(std_lst)):
        nominator.append(
            sample_size[i] * pow(std_lst[i], 2)
            + sample_size[i] * pow((means[i][0] - combined_mean), 2)
        )

    combined_std = sum(nominator) / sum(sample_size)

    return combined_std


def percentage(percent, whole):
    return (percent * whole) / 100.0
