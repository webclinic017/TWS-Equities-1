from os.path import isfile
from os.path import dirname
from os.path import join
from os.path import sep
import pandas as pd


# TODO: load test tickers from a function call
# TODO: better error handling against user input


_ROOT_DIRECTORY = dirname(__file__)
_PATH_TO_JAPAN_INDICES = join(_ROOT_DIRECTORY, 'japan_indices.csv')
PATH_TO_DEFAULT_TICKERS = join(_ROOT_DIRECTORY, 'tickers.csv')
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


def _get_file_extension(file_path):
    return file_path.split(sep)[-1].split('.')[-1]


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


def _validate_target_file(file_path, expected_file_type='csv'):
    """
        Validates that file is CSV and present on the given location.
        :param file_path: location of the data file
        :return: None
    """
    if not(isinstance(expected_file_type, str)):
        raise TypeError(f'Expected file type can not be: {expected_file_type}')
    file_type = _get_file_extension(file_path)
    if file_type != expected_file_type:
        raise TypeError(f'Data file must be {expected_file_type.upper()}, received: {file_type}')
    if not(isfile(file_path)):
        raise FileNotFoundError(f'File: {file_path} does not exist.')


def _read_csv(file_path):
    _validate_target_file(file_path, expected_file_type='csv')
    return pd.read_csv(file_path)


def _load_tickers_from_a_file(file_path):
    data = _read_csv(file_path)
    columns = data.columns
    if 'ecode' not in columns:
        raise ValueError(f'User specified input file does not have a column called "ecode".')
    return data[~data.ecode.isna()].ecode.astype(int).tolist()


def get_default_tickers():
    return _load_tickers_from_a_file(PATH_TO_DEFAULT_TICKERS)


def get_tickers_from_user_file(file_path):
    return _load_tickers_from_a_file(file_path)


def get_japan_indices():
    """
        Loads, cleans & returns japan_indices.csv
    """
    _validate_target_file(_PATH_TO_JAPAN_INDICES, expected_file_type='csv')
    data = _read_csv(_PATH_TO_JAPAN_INDICES)
    data = _drop_unnamed_columns(data)
    data.fillna('', inplace=True)
    return data


drop_unnamed_columns = _drop_unnamed_columns
format_column_names = _format_column_names
