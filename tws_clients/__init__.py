from alive_progress import alive_bar
from helpers import BAR_CONFIG as _BAR_CONFIG
from tws_clients.base import TWSWrapper
from tws_clients.base import TWSClient
from tws_clients.data_extractor import HistoricalDataExtractor
import sys


_BATCH_SIZE = 30


def batch_maker(tickers, size):
    """
        Generates batches from given list of tickers
        :param tickers: list of ticker
        :param size: size for each batch
        :return: list of bachtes
    """
    batches = []
    start, end = 0, size
    for i in range(start, len(tickers), size):
        batches.append(tickers[start:end])
        start = end
        end += size
    return batches


def extractor(tickers, end_date, end_time, duration, bar_size, what_to_show, use_rth,
              date_format, keep_upto_date, chart_options, create_data_dump, verbose, debug):
    client = HistoricalDataExtractor(end_date=end_date, end_time=end_time, duration=duration,
                                     bar_size=bar_size, what_to_show=what_to_show, use_rth=use_rth,
                                     date_format=date_format, keep_upto_date=keep_upto_date,
                                     chart_options=chart_options, create_data_dump=create_data_dump,
                                     verbose=verbose, debug=debug)
    client.extract_historical_data(tickers)
    return client.data


def extract_historical_data(tickers=(), end_date='20201231', end_time='15:01:00', duration='1 D',
                            bar_size='1 min', what_to_show='TRADES', use_rth=1, date_format=1,
                            keep_upto_date=False, chart_options=(), create_data_dump=True,
                            verbose=False, debug=False, batch_size=_BATCH_SIZE):
    """
        A wrapper function around HistoricalDataExtractor, that pulls data from TWS for the given tickers.
        Designed to provide a multi-threaded extraction mechanism.
        :param tickers: ticker ID (ex: 1301)
        :param end_date: end date (ex: '20201126')
        :param end_time: end time (ex: '20201126 15:00:01')
        :param duration: the amount of time to go back from end_date_time (ex: '1 D')
        :param bar_size: valid bar size or granularity of data (ex: '1 min')
        :param what_to_show: the type of data to retrieve (ex: 'TRADES')
        :param use_rth: 1 means retrieve data withing regular trading hours, else 0
        :param date_format: format for bar data, 1 means yyyyMMdd, 0 means epoch time
        :param keep_upto_date: setting to True will continue to return unfinished bar data
        :param chart_options: to be documented
        :param create_data_dump: toggle to create extract ticker data into a JSON file
        :param verbose: increase verbosity of the program
        :param debug: allow to debug messages to be shown on console
        :param batch_size: size of each batch as integer, default=30
        :return: an array of dictionaries, containing relevant data for each ticker
    """
    batches = batch_maker(tickers, batch_size)
    total = len(batches)

    sys.stdout.write(f'{"-"*40} Init Extraction {"-"*40}\n')
    sys.stdout.write(f'A total of {len(tickers)} tickers have been split into {total} batches of {batch_size} '
                     f'tickers each.\n')
    sys.stdout.write('Batch-wise extraction in progress, this can take some time, please be patient...\n')

    with alive_bar(total=total, **_BAR_CONFIG) as bar:
        for i in range(total):
            batch = batches[i]
            extractor(batch, end_date, end_time, duration, bar_size, what_to_show,
                      use_rth, date_format, keep_upto_date, chart_options,
                      create_data_dump, verbose, debug)
            bar()  # update progress bar

    sys.stdout.write('\n')
    sys.stdout.flush()


if __name__ == '__main__':
    tickers = list(range(1300, 1400))
    extract_historical_data(tickers,
                            end_date='20201230',
                            end_time='09:01:00',
                            duration='1 D')
