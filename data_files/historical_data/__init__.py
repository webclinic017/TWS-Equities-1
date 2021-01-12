from alive_progress import alive_bar
from helpers import BAR_CONFIG as _BAR_CONFIG

from data_files import dirname
from data_files import isdir
from data_files import join
from data_files import listdir
from data_files import pd

import json
import sys


_ROOT_DIRECTORY = dirname(__file__)


# TODO: both dataframe generators should be refactored into a generic fucntion.
# TODO: turn this module into a generator based CSV writer
def generate_failure_dataframe(location):
    """
        Creates a pandas data fame from JSON files present at the given failure location.
        Assumes that all these JSON files have valid error stack.
        :param location: location to read JSON files from
    """
    expected_columns = ['ecode', 'status', 'attempts', 'code', 'message']
    data_frame = pd.DataFrame(columns=expected_columns)

    json_files = list(filter(lambda x: x.endswith('.json'), listdir(location)))
    total = len(json_files)

    sys.stdout.write(f'Failure data extracted successfully for: {total} ticker(s).\n')
    sys.stdout.write(f'DataFrame generation is in progress, plese wait...\n')
    with alive_bar(total=total, **_BAR_CONFIG) as bar:
        for i in range(total):
            file_name = json_files[i]
            ticker = int(file_name.split('.')[0])
            file_path = join(location, file_name)
            with open(file_path, 'r') as f:
                data = json.loads(f.read())['meta_data']
            temp = pd.DataFrame(data['_error_stack'])
            temp['ecode'] = ticker
            temp['attempts'] = data['attempts']
            temp['status'] = data['status']
            data_frame = data_frame.append(temp)
            bar()

    data_frame.sort_values(by=['ecode'], inplace=True)
    data_frame.reset_index(inplace=True)
    if 'index' in data_frame.columns:
        data_frame.drop('index', axis=1, inplace=True)
    return data_frame


def generate_success_dataframe(location):
    """
        Creates a pandas data fame from JSON files present at the given success location.
        Assumes that all these files have valid bar data.
        :param location: location to read JSON files from
    """
    expected_columns = ['time_stamp', 'ecode', 'session', 'open', 'high',
                        'low', 'close', 'volume', 'count', 'average']
    data_frame = pd.DataFrame(columns=expected_columns)
    json_files = list(filter(lambda x: x.endswith('.json'), listdir(location)))
    total = len(json_files)

    sys.stdout.write(f'Bar-data extracted successfully for: {total} ticker(s).\n')
    sys.stdout.write(f'DataFrame generation is in progress, plese wait...\n')
    with alive_bar(total=total, **_BAR_CONFIG) as bar:
        for i in range(total):
            name = json_files[i]
            ticker = int(name.split('.')[0])
            path = join(location, name)
            with open(path, 'r') as f:
                data = json.loads(f.read())['bar_data']
            temp = pd.DataFrame(data)
            temp['ecode'] = ticker
            temp.sort_values(by='time_stamp', inplace=True)
            data_frame = data_frame.append(temp)
            bar()

    data_frame.sort_values(by=['ecode', 'time_stamp'], inplace=True)
    data_frame.reset_index(inplace=True)
    if 'index' in data_frame.columns:
        data_frame.drop('index', axis=1, inplace=True)
    return data_frame


def create_csv_dump(target_date):
    """
        Creates a CSV file from JSON files for a given date.
        Raise an error if directory for the gven is not present.
        Created CSV files will be saved at the same location by the name:
            'success.csv' & 'failure.csv'
    """
    target_directory = join(_ROOT_DIRECTORY, target_date)
    if not isdir(target_directory):
        raise NotADirectoryError(f'Data storage directory for {target_date} not found at {_ROOT_DIRECTORY}')
    target = join(_ROOT_DIRECTORY, target_date)
    success = join(target, 'success')
    failure = join(target, 'failure')

    sys.stdout.write(f'{"-"*40} Init CSV Maker {"-"*41}\n')
    if isdir(success):
        data_frame = generate_success_dataframe(success)
        _path = join(target, 'success.csv')
        data_frame.to_csv(_path)
        sys.stdout.write(f'Written success file at: {_path}\n\n')

    if isdir(failure):
        data_frame = generate_failure_dataframe(failure)
        _path = join(target, 'failure.csv')
        data_frame.to_csv(_path)
        sys.stdout.write(f'Written failure file at: {_path}\n\n')

    sys.stdout.write('\n')
    sys.stdout.flush()


if __name__ == '__main__':
    create_csv_dump('20210112')
