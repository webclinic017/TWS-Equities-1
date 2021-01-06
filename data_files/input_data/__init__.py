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
