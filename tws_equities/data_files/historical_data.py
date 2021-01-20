from alive_progress import alive_bar
from glob import glob
from os.path import isdir
from os.path import join
from os.path import sep
import pandas as pd
from sys import stdout

from tws_equities.data_files import get_japan_indices
from tws_equities.helpers import BAR_CONFIG as _BAR_CONFIG
from tws_equities.helpers import read_json_file
from tws_equities.helpers import save_data_as_json
from tws_equities.helpers import make_dirs
from tws_equities.helpers import delete_directory
from tws_equities.helpers import read_csv
from tws_equities.helpers import isfile
from tws_equities.helpers import HISTORICAL_DATA_STORAGE as _HISTORICAL_DATA_STORAGE


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

    if bool(total):
        json_generator = (read_json_file(file) for file in success_files)
        counter = 0  # to count temp files
        with alive_bar(total=total, **_BAR_CONFIG) as bar:
            for i in range(total):
                ticker_data = next(json_generator)
                bar_data, meta_data = ticker_data['bar_data'], ticker_data['meta_data']
                temp_data = pd.DataFrame(bar_data)
                temp_data['ecode'] = meta_data.get('ecode', _get_ticker_id(success_files[i]))
                data = data.append(temp_data)
                _time_to_cache = (i+1 == total) or ((i > 0) and (i % 100 == 0))
                if _time_to_cache:
                    if data.shape[0] > 0:
                        temp_file = join(temp_directory, f'success_{counter}.csv')
                        data.to_csv(temp_file)
                        data = pd.DataFrame(columns=expected_columns)
                        counter += 1
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

    if bool(total):
        json_generator = map(read_json_file, failure_files)
        counter = 0  # to count temp CSV files
        with alive_bar(total=total, **_BAR_CONFIG) as bar:
            for i in range(total):
                ticker_data = next(json_generator)
                meta_data = ticker_data['meta_data']
                error_stack = meta_data['_error_stack']
                temp_data = pd.DataFrame(error_stack)
                status, attempts = meta_data['status'], meta_data['attempts']
                temp_data['ecode'] = meta_data.get('ecode', _get_ticker_id(failure_files[i]))
                temp_data['status'], temp_data['attempts'] = status, attempts
                data = data.append(temp_data)
                _time_to_cache = (i+1 == total) or ((i > 0) and (i % 100 == 0))
                if _time_to_cache:
                    if data.shape[0] > 0:
                        temp_file = join(temp_directory, f'failure_{counter}.csv')
                        data.to_csv(temp_file)
                        data = pd.DataFrame(columns=expected_columns)
                        counter += 1
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
    stdout.write(f'{"-"*40} Init Conversion {"-"*40}\n')
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


def _get_ratio(input_items, output_items, decimal_palces=3):
    return_value = 0.0
    try:
        return_value = round(len(output_items) / len(input_items), decimal_palces)
    except ZeroDivisionError:
        pass
    return return_value


# noinspection PyUnusedLocal
# TODO: refactor
def generate_extraction_metrics(target_date):
    """
        Generates metrics about success & failure tickers.
        Metrics are saved into a new file called 'metrics.csv'
        :param target_date: date for which metrics are needed
    """
    stdout.write('Generating final metrics, please wait...\n')
    expected_metrics = [
                            'total_tickers', 'total_extracted', 'total_extraction_ratio',
                            'extraction_successful', 'extraction_failure',
                            'success_ratio', 'failure_ratio',
                            'n_225_input_ratio', 'n_225_success_ratio', 'n_225_failure_ratio',
                            'topix_input_ratio', 'topix_success_ratio', 'topix_failure_ratio',
                            'jasdaq_20_input_ratio', 'jasdaq_20_success_ratio', 'jasdaq_20_failure_ratio',
                            'missing_tickers_ratio', 'missing_tickers'
                       ]
    metrics = dict(zip(expected_metrics, [0.0]*len(expected_metrics)))
    target_directory = join(_HISTORICAL_DATA_STORAGE, target_date)
    if not isdir(target_directory):
        raise NotADirectoryError(f'Data storage directory for {target_date} not found at'
                                 f'{_HISTORICAL_DATA_STORAGE}')

    success_file = join(target_directory, 'success.csv')
    failure_file = join(target_directory, 'failure.csv')
    input_tickers_file = join(target_directory, 'input_tickers.json')

    if not isfile(success_file):
        raise FileNotFoundError(f'Can not find success file: {success_file}')

    if not isfile(failure_file):
        raise FileNotFoundError(f'Can not find failure file: {failure_file}')

    if not isfile(input_tickers_file):
        raise FileNotFoundError(f'Can not find input tickers file: {input_tickers_file}')

    input_tickers = read_json_file(input_tickers_file)
    japan_indices = get_japan_indices()

    _n_225_tickers = japan_indices[japan_indices.n_225.str.contains('T')].n_225.unique().tolist()
    n_225_tickers = list(map(lambda x: int(x.split('.')[0]), _n_225_tickers))

    _topix_tickers = japan_indices[japan_indices.topix.str.contains('T')].topix.unique().tolist()
    topix_tickers = list(map(lambda x: int(x.split('.')[0]), _topix_tickers))

    _jasdaq_20_tickers = japan_indices[japan_indices.jasdaq_20.str.contains('T')].jasdaq_20.unique().tolist()
    jasdaq_20_tickers = list(map(lambda x: int(x.split('.')[0]), _jasdaq_20_tickers))

    success = read_csv(success_file)
    failure = read_csv(failure_file)

    success_tickers = success.ecode.unique().tolist()
    failure_tickers = failure.ecode.unique().tolist()

    total_tickers = len(input_tickers)
    if total_tickers == 0:
        raise ValueError(f'Can not find any input tickers in file {input_tickers_file}')

    extraction_successful = len(success_tickers)
    extraction_failure = len(failure_tickers)
    total_extracted = extraction_successful + extraction_failure
    total_extraction_ratio = round(total_extracted / total_tickers, 3)

    success_ratio = round(extraction_successful / total_tickers, 3)
    failure_ratio = round(extraction_failure / total_tickers, 3)

    n_225_input = list(set(input_tickers).intersection(n_225_tickers))
    if bool(n_225_input):
        n_225_input_ratio = round(len(n_225_input) / len(n_225_tickers), 3)
        n_225_success = list(set(success_tickers).intersection(n_225_input))
        n_225_failure = list(set(failure_tickers).intersection(n_225_input))
        n_225_success_ratio = round(len(n_225_success) / len(n_225_input), 3)
        n_225_failure_ratio = round(len(n_225_failure) / len(n_225_input), 3)

    topix_input = list(set(input_tickers).intersection(topix_tickers))
    if bool(topix_input):
        topix_input_ratio = round(len(topix_input) / len(topix_tickers), 3)
        topix_success = list(set(success_tickers).intersection(topix_input))
        topix_failure = list(set(failure_tickers).intersection(topix_input))
        topix_success_ratio = round(len(topix_success) / len(topix_input), 3)
        topix_failure_ratio = round(len(topix_failure) / len(topix_input), 3)

    jasdaq_20_input = list(set(input_tickers).intersection(jasdaq_20_tickers))
    if bool(jasdaq_20_input):
        jasdaq_20_input_ratio = round(len(jasdaq_20_input) / len(jasdaq_20_tickers), 3)
        jasdaq_20_success = list(set(success_tickers).intersection(jasdaq_20_input))
        jasdaq_20_failure = list(set(failure_tickers).intersection(jasdaq_20_input))
        jasdaq_20_success_ratio = round(len(jasdaq_20_success) / len(jasdaq_20_input), 3)
        jasdaq_20_failure_ratio = round(len(jasdaq_20_failure) / len(jasdaq_20_input), 3)

    missing_tickers = list(set(input_tickers).difference(success_tickers + failure_tickers))
    missing_tickers_ratio = round(len(missing_tickers) / total_tickers, 3)

    all_vars = vars()
    for key in all_vars:
        if key in expected_metrics:
            metrics[key] = all_vars[key]

    save_data_as_json(metrics, join(target_directory, 'metrics.json'))
    stdout.write('\n')


if __name__ == '__main__':
    # create_csv_dump('20210120')
    generate_extraction_metrics('20210120')
