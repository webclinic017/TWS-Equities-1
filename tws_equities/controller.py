#! TWS-Project/venv/bin/python3.9

"""
    © 2020 K2Q Capital Limited
    All rights reserved.

                        TWS: Equities Data Extractor
                        ----------------------------
    This module is the main controller built around "HistoricalDataExtractor"
    client. It intends to provides a Command Line Interface (CLI), using
    Python's "argparse" module(https://docs.python.org/3/library/argparse.html),
    to extract historical bar data for Japanese Equities.

    Sample Commands:
    ---------------
        - Pass a list of tickers:
            python controller.py -ed 20201210 -et 09:10:00 tickers -l 1301 1332 1333
        - Pass a file path for tickers:
            - Load default input (Input File: TWS Project/data_files/input_data/tickers.csv)
                python controller.py -ed 20201210 -et 09:10:00 tickers -f default
            - Load custom input from a different file:
                python controller.py -ed 20201210 -et 09:10:00 tickers -f <user_defined_file_path>
            _ Load data from a Google Sheet:
                *** Not supported yet!
        - Export extracted data to JSON files:
            python controller.py -ed 20201210 -et -dd 09:10:00 tickers -l 1301 1332 1333

        - NOTE:
            - Data is exported to: 'TWS Project/data_files/historical_data/'.
            - Data is segregated based on end date and extraction status.
            - Tickers must be passed as the last input to the CLI (to be handled).
"""


from tws_equities.data_files import create_csv_dump
from tws_equities.data_files import generate_extraction_metrics
from tws_equities.helpers import get_logger
from tws_equities.helpers import get_date_range
from tws_equities.tws_clients import extract_historical_data


def setup_logger(name, verbose=False, debug=False):
    """
        Setup & return a logger object.
    """
    level = 'DEBUG' if debug else ('INFO' if verbose else 'WARNING')
    logger = get_logger(name, level)
    return logger


def download(**kwargs):
    extract_historical_data(**kwargs)


def convert(start_date=None, end_date=None):
    if start_date is None:
        start_date = end_date
    if end_date is None:
        raise ValueError(f'User must pass at least the end date for data conversion.')
    date_range = get_date_range(start_date, end_date)
    for date in date_range:
        create_csv_dump(date)


def metrics(start_date=None, end_date=None, tickers=None):
    if start_date is None:
        start_date = end_date
    if end_date is None:
        raise ValueError(f'User must pass at least the end date for metrics generation.')
    if tickers is None:
        # fixme: to be implemented...
        pass
    date_range = get_date_range(start_date, end_date)
    for date in date_range:
        generate_extraction_metrics(date)


def run(**kwargs):
    download(**kwargs)
    tickers, start_date, end_date = kwargs.get('tickers'), kwargs.get('start_date'), kwargs.get('end_date')
    convert(start_date=start_date, end_date=end_date)
    metrics(start_date=start_date, end_date=end_date)


if __name__ == '__main__':
    convert(end_date='20210120')
