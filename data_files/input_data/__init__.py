import pandas as pd
from os.path import isfile
from os.path import dirname
from os.path import join


def get_default_file_path():
    """
        Generate full path for tickers.csv
        :return: file path for tickers.csv
    """
    return join(dirname(__file__), 'tickers.csv')


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
        file_path = get_default_file_path()
    validate_target_file(file_path)
    csv = pd.read_csv(file_path)
    return csv.code.tolist()


test_tickers = [
                    123,
                    467,
                    58787,
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
                    1965
                ]
