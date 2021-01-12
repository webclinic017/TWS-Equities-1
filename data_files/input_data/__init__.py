import pandas as pd
from os.path import isfile
from os.path import dirname
from os.path import join


_ROOT_DIRECTORY = dirname(__file__)

_PATH_TO_INPUT_TICKERS = join(_ROOT_DIRECTORY, 'tickers.csv')
_PATH_TO_JAPAN_INDICES = join(_ROOT_DIRECTORY, 'japan_indices.csv')

TEST_TICKERS = [
                    1301,
                    1332,
                    1376,
                    1377,
                    1382,
                    1383,
                    1401,
                    1407,
                    1419,
                    1429,
                    1435,
                    1436,
                    1450,
                    1712,
                    1716,
                    1717,
                    1730,
                    1736,
                    1758,
                    1762,
                    1782,
                    1783,
                    1799,
                    1801,
                    1814,
                    1815,
                    1820,
                    1833,
                    1835,
                    1840,
                    1860,
                    1861,
                    1866,
                    1867,
                    1878,
                    1879,
                    1881,
                    1882,
                    1887,
                    1888,
                    1899,
                    1904,
                    1905,
                    1909,
                    1928,
                    1929,
                    1930,
                    1941,
                    1942,
                    1944,
                    1945,
                    1954,
                    1959,
                    1960,
                    1961,
                    1963,
                    1964,
                    1965,
                    7203
                ]


def _is_dataframe(_object):
    """
        Raises a type error if a given object is not a pandas dataframe.
        :param object: will accept anything as an input
    """
    if not(isinstance(_object, pd.DataFrame)):
        raise TypeError(f'Expected a pandas data frame, received: {type(_object)}')
    return True


def _drop_unnamed_columns(data_frame):
    """
        Drop all columns that start with 'Unnamed:'
        :param data_frame: pandas data frame
        :return: data frame after removing unnamed columns
    """
    if _is_dataframe(data_frame):
        for column in data_frame.columns:
            if column.lower().startswith('unnamed:'):
                data_frame.drop(column, axis=1, inplace=True)
    return data_frame


def _format_column_names(data_frame):
    """
        Converts all column names to lower case and replaces white space with underscore.
        :param data_frame: pandas data frame
        :return: same data frame with updated column names
    """
    if _is_dataframe(data_frame):
        data_frame.columns = list(map(lambda x: x.lower().replace(' ', '_'), data_frame.columns))
    return data_frame


def validate_target_file(file_path):
    """
        Validates that file is CSV and present on the given location.
        :param file_path: location of the data file
        :return: None
    """
    supported_file_types = ['csv']
    file_type = file_path.split('.')[-1]
    if file_type not in supported_file_types:
        raise TypeError(f'Data file must be CSV, received: {file_type}')
    if not(isfile(file_path)):
        raise FileNotFoundError(f'File: {file_path} does not exist.')


def load_csv(file_path=None):
    """
        Loads ticker data from a CSV file.
        :param file_path: path to CSV file, defaults='tickers.csv'
        :return: list of tickers
    """
    # TODO: add a logger
    if file_path is None:
        file_path = _PATH_TO_INPUT_TICKERS
    validate_target_file(file_path)
    csv = pd.read_csv(file_path)
    # TODO: user specified file may not have an ecode column
    return csv.ecode.tolist()


def get_input_tickers():
    return load_csv()


def get_japan_indices():
    """
        Loads, cleans & returns japan_indices.csv
    """
    if not isfile(_PATH_TO_JAPAN_INDICES):
        raise FileNotFoundError(f'Can not find Japan Indices file at: {_PATH_TO_JAPAN_INDICES}')
    csv = pd.read_csv(_PATH_TO_JAPAN_INDICES)
    csv = _drop_unnamed_columns(csv)
    csv.fillna('', inplace=True)
    return csv


drop_unnamed_columns = _drop_unnamed_columns
format_column_names = _format_column_names
