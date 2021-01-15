from os.path import dirname
from os.path import join
from os.path import isdir
from json import dumps
from sys import stdout
import pandas as pd

from tws_equities.data_files.input_data import get_default_tickers
from tws_equities.data_files.input_data import get_tickers_from_user_file
from tws_equities.data_files.input_data import get_japan_indices
from tws_equities.data_files.input_data import drop_unnamed_columns
from tws_equities.data_files.input_data import TEST_TICKERS
from tws_equities.data_files.historical_data import create_csv_dump


_ROOT_DIRECTORY = dirname(__file__)
_PATH_TO_HISTORICAL_DATA = join(_ROOT_DIRECTORY, 'historical_data')

# INPUT_TICKERS = get_default_tickers()
_JAPAN_INDICES = get_japan_indices()
_N_225_TICKERS = _JAPAN_INDICES[_JAPAN_INDICES.n_225 != ''].n_225
N_225_TICKERS = _N_225_TICKERS.apply(lambda x: int(x.split('.')[0])).tolist()

_TOPIX_TICKERS = _JAPAN_INDICES[_JAPAN_INDICES.topix != ''].topix
TOPIX_TICKERS = _TOPIX_TICKERS.apply(lambda x: int(x.split('.')[0])).tolist()

_JASDAQ_20_TICKERS = _JAPAN_INDICES[_JAPAN_INDICES.jasdaq_20 != ''].jasdaq_20
JASDAQ_20_TICKERS = _JASDAQ_20_TICKERS.apply(lambda x: int(x.split('.')[0])).tolist()

_EXPECTED_METRICS = [
    'total_tickers', 'total_extracted',
    'extraction_successful', 'extraction_failure',
    'success_ratio', 'failure_ratio',
    'n_225_success_ratio', 'n_225_failure_ratio',
    'topix_success_ratio', 'topix_failure_ratio',
    'jasdaq_20_success_ratio', 'jasdaq_20_failure_ratio',
    'missing_tickers_ratio', 'missing_tickers'
]
_METRICS = dict(zip(_EXPECTED_METRICS, [None]*len(_EXPECTED_METRICS)))


def save_file_as_json(json, file_path, sort_keys=True, indent=4):
    with open(file_path, 'w') as f:
        f.writelines(dumps(json, sort_keys=sort_keys, indent=indent))


# noinspection PyUnusedLocal
def generate_extraction_metrics(target_date, input_tickers):
    """
        Generates metrics about success & failure tickers.
        Metrics are saved into a new file called 'metrics.csv'
        :param input_tickers: tickers against which extraction has been performed
        :param target_date: date for which metrics are needed
    """
    stdout.write('Extraction & data conversion has been completed.\n')
    stdout.write('Generating final metrics, please wait...\n')
    target_directory = join(_PATH_TO_HISTORICAL_DATA, target_date)
    if not isdir(target_directory):
        raise NotADirectoryError(f'Data storage directory for {target_date} not found at'
                                 f'{_PATH_TO_HISTORICAL_DATA}')
    success = drop_unnamed_columns(pd.read_csv(join(target_directory, 'success.csv')))
    failure = drop_unnamed_columns(pd.read_csv(join(target_directory, 'failure.csv')))

    success_tickers = success.ecode.unique().tolist()
    failure_tickers = failure.ecode.unique().tolist()

    total_tickers = len(input_tickers)

    extraction_successful = len(success_tickers)
    extraction_failure = len(failure_tickers)

    total_extracted = extraction_successful + extraction_failure

    success_ratio = round(extraction_successful / total_tickers, 3)
    failure_ratio = round(extraction_failure / total_tickers, 3)

    n_225_input = list(set(input_tickers).intersection(N_225_TICKERS))
    n_225_success = list(set(success_tickers).intersection(n_225_input))
    n_225_failure = list(set(failure_tickers).intersection(n_225_input))

    n_225_success_ratio = round(len(n_225_success) / len(n_225_input), 3)
    n_225_failure_ratio = round(len(n_225_failure) / len(n_225_input), 3)

    topix_input = list(set(input_tickers).intersection(TOPIX_TICKERS))
    topix_success = list(set(success_tickers).intersection(topix_input))
    topix_failure = list(set(failure_tickers).intersection(topix_input))

    topix_success_ratio = round(len(topix_success) / len(topix_input), 3)
    topix_failure_ratio = round(len(topix_failure) / len(topix_input), 3)

    jasdaq_20_input = list(set(input_tickers).intersection(JASDAQ_20_TICKERS))
    jasdaq_20_success = list(set(success_tickers).intersection(jasdaq_20_input))
    jasdaq_20_failure = list(set(failure_tickers).intersection(jasdaq_20_input))

    jasdaq_20_success_ratio = round(len(jasdaq_20_success) / len(jasdaq_20_input), 3)
    jasdaq_20_failure_ratio = round(len(jasdaq_20_failure) / len(jasdaq_20_input), 3)

    missing_tickers = list(set(input_tickers).difference(success_tickers + failure_tickers))
    missing_tickers_ratio = round(len(missing_tickers) / total_tickers, 3)

    all_vars = vars()
    for key in _METRICS:
        _METRICS[key] = all_vars[key]

    save_file_as_json(_METRICS, join(target_directory, 'metrics.json'))
    stdout.write('\n')
    stdout.flush()
    return _METRICS


if __name__ == '__main__':
    generate_extraction_metrics('20210112', [1301, 1302, 1303, 1304])
