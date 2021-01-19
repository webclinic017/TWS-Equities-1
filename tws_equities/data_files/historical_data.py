from alive_progress import alive_bar
from tws_equities.helpers import BAR_CONFIG as _BAR_CONFIG
from tws_equities.helpers import read_json_file
from tws_equities.helpers import make_dirs
from tws_equities.helpers import read_csv
from tws_equities.helpers import delete_directory

from glob import glob
from os.path import dirname
from os.path import isdir
from os.path import join
from os.path import sep
import pandas as pd
from sys import stdout


_PROJECT_ROOT = dirname(dirname(dirname(__file__)))
_HISTORICAL_DATA_STORAGE = join(_PROJECT_ROOT, 'historical_data')


# TODO: both dataframe generators could be refactored into a generic fucntion.
def generate_success_dataframe(target_directory):
    """
        Creates a pandas data fame from JSON files present at the given failure location.
        Assumes that all these JSON files have valid bar data.
        :param target_directory: location to read JSON files from
    """
    stdout.write(f'=> Generating dataframe for success tickers...\n')

    def _get_ticker_id(file_name):
        return int(file_name.split(sep)[-1].split('.')[0])
    # create a place holder dataframe
    expected_columns = ['time_stamp', 'ecode', 'session', 'high', 'low', 'close',
                        'volume', 'average', 'count']
    data = pd.DataFrame(columns=expected_columns)

    # create temporary directory to store smaller CSV files
    temp_directory = '.temp'
    make_dirs(temp_directory)

    # extract all json files from target directory
    success_file_pattern = join(target_directory, '*.json')
    success_files = glob(success_file_pattern)
    total = len(success_files)
    json_generator = (read_json_file(file) for file in success_files)

    counter = 0  # to count temp files
    with alive_bar(total=total, **_BAR_CONFIG) as bar:
        for i in range(total):
            if i % 100 == 0 or i+1 == total:
                if data.shape[0] > 0:
                    temp_file = join(temp_directory, f'success_{counter}.csv')
                    data.to_csv(temp_file)
                    data = pd.DataFrame(columns=expected_columns)
                    counter += 1
            ticker_data = next(json_generator)
            bar_data, meta_data = ticker_data['bar_data'], ticker_data['meta_data']
            temp_data = pd.DataFrame(bar_data)
            temp_data['ecode'] = meta_data.get('ecode', _get_ticker_id(success_files[i]))
            data = data.append(temp_data)
            bar()

    # merge all CSV files into a single dataframe
    # delete all temp files
    temp_files = glob(join(temp_directory, 'success_*.csv'))
    data = pd.concat(map(read_csv, temp_files))
    data.sort_values(by=['ecode', 'time_stamp'], inplace=True, ignore_index=True)
    data = data[expected_columns]
    delete_directory(temp_directory)

    return data


def generate_failure_dataframe(target_directory):
    """
        Creates a pandas data fame from JSON files present at the given failure location.
        Assumes that all these JSON files have valid error stacks.
        :param target_directory: location to read JSON files from
    """
    stdout.write(f'=> Generting dataframe for failure tickers...\n')

    def _get_ticker_id(file_name):
        return int(file_name.split(sep)[-1].split('.')[0])

    # create a place holder dataframe
    expected_columns = ['ecode', 'status', 'code', 'message', 'attempts']
    data = pd.DataFrame(columns=expected_columns)

    # create temporary directory to store smaller CSV files
    temp_directory = '.temp'
    make_dirs(temp_directory)

    # extract all json files from target directory
    file_pattern = join(target_directory, '*.json')  # TODO: can be modified to match digital values
    failure_files = glob(file_pattern)
    total = len(failure_files)
    json_generator = map(read_json_file, failure_files)

    counter = 0  # to count temp CSV files
    with alive_bar(total=total, **_BAR_CONFIG) as bar:
        for i in range(total):
            if i % 100 == 0 or i+1 == total:
                if data.shape[0] > 0:
                    temp_file = join(temp_directory, f'failure_{counter}.csv')
                    data.to_csv(temp_file)
                    data = pd.DataFrame(columns=expected_columns)
                    counter += 1
            ticker_data = next(json_generator)
            meta_data = ticker_data['meta_data']
            error_stack = meta_data['_error_stack']
            temp_data = pd.DataFrame(error_stack)
            status, attempts = meta_data['status'], meta_data['attempts']
            temp_data['ecode'] = meta_data.get('ecode', _get_ticker_id(failure_files[i]))
            temp_data['status'], temp_data['attempts'] = status, attempts
            data = data.append(temp_data)
            bar()

    # merge all CSV files into a single dataframe
    # delete all temp files
    temp_files = glob(join(temp_directory, 'failure_*.csv'))
    data = pd.concat(map(read_csv, temp_files))
    data.sort_values(by=['ecode'], ignore_index=True, inplace=True)
    data = data[expected_columns]
    delete_directory(temp_directory)

    return data


def create_csv_dump(target_date):
    """
        Creates a CSV file from JSON files for a given date.
        Raise an error if directory for the gven is not present.
        Created CSV files will be saved at the same location by the name:
            'success.csv' & 'failure.csv'
    """
    stdout.write(f'{"-"*40} Init Conversion {"-"*40}')
    target_directory = join(_HISTORICAL_DATA_STORAGE, target_date)
    if not isdir(target_directory):
        raise NotADirectoryError(f'Could not find a data storage directory for date: {target_date}')
    success_directory = join(target_directory, '.success')
    failure_directory = join(target_directory, '.failure')

    if isdir(success_directory):
        success = generate_success_dataframe(success_directory)
        path = join(target_directory, 'success.csv')
        success.to_csv(path, index=False)

    if isdir(failure_directory):
        failure = generate_failure_dataframe(failure_directory)
        path = join(target_directory, 'failure.csv')
        failure.to_csv(path, index=False)

    stdout.write('\n')


if __name__ == '__main__':
    create_csv_dump('20210118')
