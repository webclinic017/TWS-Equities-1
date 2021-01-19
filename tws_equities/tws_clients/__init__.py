from alive_progress import alive_bar
from os.path import dirname
from os.path import join
from os import listdir
from sys import stdout

# from time import sleep

from tws_equities.helpers import BAR_CONFIG as _BAR_CONFIG
from tws_equities.tws_clients.base import TWSWrapper
from tws_equities.tws_clients.base import TWSClient
from tws_equities.tws_clients.data_extractor import HistoricalDataExtractor
from tws_equities.helpers import create_batches
from tws_equities.helpers import get_date_range
from tws_equities.helpers import delete_file
from tws_equities.helpers import make_dirs
from tws_equities.helpers import save_data_as_json


# TODO: add info messages to console
# TODO: find a better way to do this
# TODO: duplicate file creation
_BATCH_SIZE = 30
_PROJECT_ROOT = dirname(dirname(dirname(__file__)))
_PATH_TO_HISTORICAL_DATA = join(_PROJECT_ROOT, 'historical_data')
CACHE_DIRECTORY = None


def _cache_data(data, cache_success, cache_failure):
    for ticker in data:
        data_to_save = data[ticker]
        status = data_to_save['meta_data']['status']

        file_path = join(cache_success if status else cache_failure, f'{ticker}.json')
        save_data_as_json(data_to_save, file_path)


def _filter_file(file_name, file_type='json'):
    return file_name.split('.')[-1] == file_type


def _get_ticker_id(file_name):
    return int(file_name.split('.')[0])


def _get_unprocessed_tickers(tickers, success_directory, failure_directory):
    """
        # TODO: to be added...
    """
    success_tickers = list(map(_get_ticker_id, filter(_filter_file, listdir(success_directory))))
    # exclude tickers that have already processed successfully
    unprocessed_tickers = list(set(tickers).difference(success_tickers))

    # clean failure directory, all these tickers will have to be processed again
    failure_files = list(filter(_filter_file, listdir(failure_directory)))
    failure_tickers = list(map(_get_ticker_id, failure_files))
    common_tickers = list(set(tickers).intersection(failure_tickers))
    for ticker in common_tickers:
        file_name = f'{ticker}.json'
        delete_file(failure_directory, file_name)

    return unprocessed_tickers


def _prep_for_extraction(tickers, target_date):
    # stdout.write(f'=> Setting things up for extraction for: {target_date}\n')

    # form data caching directory
    cache_directory = join(_PATH_TO_HISTORICAL_DATA, target_date)

    # create cache directory for success
    cache_success = join(cache_directory, '.success')
    make_dirs(cache_success)

    # create cache directory for failure
    cache_failure = join(cache_directory, '.failure')
    make_dirs(cache_failure)
    # stdout.write(f'\t-> Cache directies created...\n')

    # save tickers for later use
    path_input_tickers = join(cache_directory, 'input_tickers.json')
    save_data_as_json(tickers, path_input_tickers, indent=0)
    # stdout.write(f'\t-> Cached target tickers...\n')

    # extract tickers that are yet to be processed
    tickers = _get_unprocessed_tickers(tickers, cache_success, cache_failure)
    # stdout.write(f'\t-> Excluded already processed tickers...\n')
    # stdout.write(f'\t-> Total target tickers: {len(tickers)}\n')

    return tickers, cache_success, cache_failure


def _extractor(tickers, end_date, end_time, duration, bar_size, what_to_show, use_rth,
               date_format, keep_upto_date, chart_options):
    client = HistoricalDataExtractor(end_date=end_date, end_time=end_time, duration=duration,
                                     bar_size=bar_size, what_to_show=what_to_show, use_rth=use_rth,
                                     date_format=date_format, keep_upto_date=keep_upto_date,
                                     chart_options=chart_options)
    client.extract_historical_data(tickers)
    return client.data


def _run_extractor(batches, end_date, end_time, duration, bar_size, what_to_show, use_rth, date_format,
                   keep_upto_date, chart_options, cache_success, cache_failure):
    total = len(batches)
    data = {}
    stdout.write('=> Extraction in progress, this can take some time time. Please wait...\n')
    with alive_bar(total=total, **_BAR_CONFIG) as bar:
        for i in range(total):
            if i % 10 == 0 or i+1 == total:
                _cache_data(data, cache_success, cache_failure)
                data = {}
            batch = batches[i]
            temp = _extractor(batch, end_date, end_time, duration, bar_size, what_to_show,
                              use_rth, date_format, keep_upto_date, chart_options)
            data.update(temp)
            bar()  # update progress bar
    # return success & failure files
    return listdir(cache_success), listdir(cache_failure)


# noinspection PyUnusedLocal
def _cleanup(success_files, success_directory, failure_files, failure_directory):
    stdout.write(f'=> Post-extraction cleanup initiated...\n')
    common_files = list(set(success_files).intersection(failure_files))
    stdout.write(f'\t-> Detected {len(common_files)} duplicate files...\n')
    for file in common_files:
        delete_file(failure_directory, file)
    # stdout.write(f'\t-> Clean completed successfully...\n')


# noinspection PyUnusedLocal
def _sanity_check(tickers, success_files, success_directory, failure_files, failure_directory):
    """
        To be implemented...
    """
    status = False
    return status


def extract_historical_data(tickers=None, start_date=None, end_date=None, end_time=None, duration='1 D',
                            bar_size='1 min', what_to_show='TRADES', use_rth=1, date_format=1,
                            keep_upto_date=False, chart_options=(), batch_size=_BATCH_SIZE):
    """
        A wrapper function around HistoricalDataExtractor, that pulls data from TWS for the given tickers.
        :param tickers: ticker ID (ex: 1301)
        :param start_date: date from which the extraction is to be started (ex: '20201231')
        :param end_date: end date (ex: '20210101')
        :param end_time: end time (ex: '15:00:01')
        :param duration: the amount of time to go back from end_date_time (ex: '1 D')
        :param bar_size: valid bar size or granularity of data (ex: '1 min')
        :param what_to_show: the type of data to retrieve (ex: 'TRADES')
        :param use_rth: 1 means retrieve data withing regular trading hours, else 0
        :param date_format: format for bar data, 1 means yyyyMMdd, 0 means epoch time
        :param keep_upto_date: setting to True will continue to return unfinished bar data
        :param chart_options: to be documented
        :param batch_size: size of each batch as integer, default=30
    """
    stdout.write(f'\n{"-"*40} Init Extraction {"-"*40}\n')
    date_range = get_date_range(start_date, end_date)
    for target_date in date_range:
        tickers, cache_success, cache_failure = _prep_for_extraction(tickers, target_date)
        batches = create_batches(tickers, batch_size)
        success_files, failure_files = _run_extractor(batches, target_date, end_time, duration, bar_size,
                                                      what_to_show, use_rth, date_format, keep_upto_date,
                                                      chart_options, cache_success, cache_failure)
        _cleanup(success_files, cache_success, failure_files, cache_failure)
        # stdout.write(f'=> Extraction completed for: {target_date}\n')
        stdout.write(f'\n{"-"*100}\n\n')
    # its_a_bad_news = not _sanity_check(tickers, success_files, cache_success, failure_files, cache_failure)
    # if its_a_bad_news:
    #     print('Its a bad news! You gotta do it again... :(')


if __name__ == '__main__':
    tickers = list(range(1300, 1320))
    extract_historical_data(tickers,
                            end_date='20210115',
                            end_time='15:01:00',
                            duration='1 D',
                            batch_size=5)
