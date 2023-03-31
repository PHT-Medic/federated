import re
import pandas as pd

from pht_federated.aggregator.schemas.dataset_statistics import DatasetStatistics



def adjust_name_differences(local_dataset_stat: DatasetStatistics, difference_report: dict) -> DatasetStatistics:
    """
    Changes the column names of the local dataset according to the suggested changes provided by the difference report.
    :param local_dataset_stat: summary statistics of the given local dataset
    :param difference_report: Lists differences between local and aggregated datasets and provides hints to resolve them
    :return adjusted_dataset -> Dataset with applied column name changes
    """

    local_dataset_stat = local_dataset_stat.dict()
    #print("Local dataset: {}".format(local_dataset))
    #print("Difference Report: {}".format(difference_report))

    name_errors = [column["hint"] for column in difference_report["errors"] if column["error"]["type"] == "added"]
    #print("Name Errors : {}".format(name_errors))

    name_diffs = [re.findall('"([^"]*)"', errors) for errors in name_errors]
    name_diffs = [error for error in name_diffs if len(error) > 1]
    #print("Name diffs : {}".format(name_diffs))

    for column in local_dataset_stat["column_information"]:
        for diff in name_diffs:
            if column["title"] == diff[0]:
                column["title"] = diff[1]

    #print("Updated local dataset : {}".format(local_dataset))

    return DatasetStatistics(**local_dataset_stat)

def delete_name_differences(local_dataset_stat: DatasetStatistics, difference_report: dict) -> DatasetStatistics:
    """
    Deletes the column names of the local dataset when the respective column is only available locally
    :param local_dataset_stat: summary statistics of the given local dataset
    :param difference_report: Lists differences between local and aggregated datasets and provides hints to resolve them
    :return adjusted_dataset -> Dataset with applied column name changes
    """

    local_dataset_stat = local_dataset_stat.dict()

    name_errors = [column["hint"] for column in difference_report["errors"] if column["error"]["type"] == "added"]
    name_diffs = [re.findall('"([^"]*)"', errors) for errors in name_errors]
    name_diffs = [error for error in name_diffs if len(error) == 1]

    for c in range(len(local_dataset_stat["column_information"])):
        for diff in name_diffs:
            if local_dataset_stat["column_information"][c]["title"] == diff[0]:
                del local_dataset_stat["column_information"][c]

    return DatasetStatistics(**local_dataset_stat)


def adjust_type_differences(local_dataset: pd.DataFrame, local_dataset_stat: DatasetStatistics,
                            difference_report: dict) -> DatasetStatistics:
    """
    Changes the column types of the local dataset according to the suggested changes provided by the difference report
    while taking multiple different mismatching cases into account
    :param local_dataset: Pandas dataframe of the tabular local dataset
    :param local_dataset_stat: summary statistics of the given local dataset
    :param difference_report: Lists differences between local and aggregated datasets and provides hints to resolve them
    :return adjusted_dataset -> Dataset with applied column name changes
    """

    local_dataset_stat = local_dataset_stat.dict()

    print("Local Dataset : {}".format(local_dataset))
    print("Local Dataset Statistics : {}".format(local_dataset_stat))
    print("Difference Report : {}".format(difference_report))

    type_errors = [column["hint"] for column in difference_report["errors"] if column["error"]["type"] == "type"]
    print("Type Errors : {}".format(type_errors))

    type_diffs = [re.findall('"([^"]*)"', errors) for errors in type_errors]
    print("Type diffs : {}".format(type_diffs))

    #numeric = local_dataset.applymap(lambda x: isinstance(x, (int, float)))['Age']
    #print(numeric)

    for differences in type_diffs:
        find_mismatch(local_dataset, differences[0], differences[1])




def find_mismatch(local_dataset: pd.DataFrame, column_name: str, column_type: type):

    for entry in local_dataset[column_name]:
        print(entry)
        type_bool = isinstance(entry, (column_type))
        print(type_bool)
        if type_bool == False:
            try:
                pass
            except:
                pass