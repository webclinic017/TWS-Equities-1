import pandas as pd
from os.path import dirname
from os.path import isdir
from os.path import join
from os import listdir
import json
import sys


ROOT_DIRECTORY = dirname(__file__)


def generate_failure_dataframe(location, verbose):
    """
        # TODO: to be added...
        @param verbose:
        @param location:
    """
    expected_columns = ['ecode', 'status', 'attempt', 'code', 'message']
    data_frame = pd.DataFrame(columns=expected_columns)

    json_files = list(filter(lambda x: x.endswith('.json'), listdir(location)))
    total_files = len(json_files)
    if verbose:
        sys.stdout.write(f'Generating dataframe for {total_files} failure tickers...\n')
    for i in range(total_files):
        file_name = json_files[i]
        ticker = int(file_name.split('.')[0])
        file_path = join(location, file_name)
        with open(file_path, 'r') as f:
            data = json.loads(f.read())['meta_data']
        temp = pd.DataFrame(data['_error_stack'])
        temp['ecode'] = ticker
        temp['attempts'] = int(data['attempt'])
        temp['status'] = data['status']
        data_frame = data_frame.append(temp)
        if verbose:
            sys.stdout.write(f'\r--- Processed: {i+1} / {total_files} ---')
    sys.stdout.flush()
    data_frame.reset_index(inplace=True)
    return data_frame


def generate_success_dataframe(location, verbose):
    """
        # TODO: to be added...
        @param verbose:
        @param location:
    """
    expected_columns = ['time_stamp', 'ecode', 'session', 'open', 'high',
                        'low', 'close', 'volume', 'count', 'average']
    data_frame = pd.DataFrame(columns=expected_columns)
    json_files = list(filter(lambda x: x.endswith('.json'), listdir(location)))
    total_files = len(json_files)
    if verbose:
        sys.stdout.write(f'Generating dataframe for {total_files} success tickers...\n')
    for i in range(total_files):
        file_name = json_files[i]
        ticker = int(file_name.split('.')[0])
        file_path = join(location, file_name)
        with open(file_path, 'r') as f:
            data = json.loads(f.read())['bar_data']
        temp = pd.DataFrame(data)
        temp['ecode'] = ticker
        data_frame = data_frame.append(temp)
        if verbose:
            sys.stdout.write(f'\r--- Processed: {i+1} / {total_files} ---')
    sys.stdout.flush()
    data_frame.reset_index(inplace=True)
    return data_frame


def create_csv_dump(target_date, verbose=False):
    """
        TODO: To be added...
    """
    if target_date not in listdir(ROOT_DIRECTORY):
        raise NotADirectoryError(f'Data storage directory for {target_date} not found at {ROOT_DIRECTORY}')
    target_location = join(dirname(__file__), target_date)
    success_location = join(target_location, 'success')
    failure_location = join(target_location, 'failure')

    if isdir(success_location):
        data_frame = generate_success_dataframe(success_location, verbose)
        data_frame.to_csv(f'{target_location}/success.csv')
        if verbose:
            sys.stdout.write(f'\nSuccess CSV: {join(target_location, "success.csv")}\n')
    if isdir(failure_location):
        data_frame = generate_failure_dataframe(failure_location, verbose)
        data_frame.to_csv(f'{target_location}/failure.csv')
        if verbose:
            sys.stdout.write(f'\nFailure CSV: {join(target_location, "failure.csv")}\n')
    sys.stdout.flush()


if __name__ == '__main__':
    create_csv_dump('20201231')
