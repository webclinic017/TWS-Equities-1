#! TWS-Project/venv/bin/python3.9

"""
    © 2020 K2Q Capital Limited
    All rights reserved.

                        TWS: Equities Data Extractor
                        ----------------------------
    This module is the main controller built around "HistoricalDataExtractor"
    client. It intends to provides a Command Line Interface (CLI) using
    Python's "argparse" module(https://docs.python.org/3/library/argparse.html).

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

from sys import stderr
from sys import stdout

from data_files import create_csv_dump
from data_files import generate_extraction_metrics
from helpers import get_logger
from parsers import parse_user_args
from tws_clients import extract_historical_data


def setup_logger(args):
    """
        Setup & return a logger for the current run.
    """
    level = 'INFO' if args['debug'] else (
            'WARNING' if args['verbose'] else 'ERROR')
    logger = get_logger(__name__, level)
    return logger


def main():
    user_args = vars(parse_user_args())
    logger = setup_logger(user_args)
    try:
        extract_historical_data(**user_args)
        create_csv_dump(user_args['end_date'])
        generate_extraction_metrics(user_args['end_date'], input_tickers=user_args['tickers'])
    except KeyboardInterrupt:
        _message = 'Detected keyboard interruption from the user, terminating program...'
        logger.warning(_message)
        stderr.write(f'{_message}\n')
    except Exception as e:
        _message = f'Program crashed, Error: {e}'
        logger.critical(_message, exc_info=True)
        stderr.write(f'{_message}\n')
        # if user_args['debug']:
        #     raise e
    stderr.flush()
    stdout.flush()


if __name__ == '__main__':
    main()
