from alive_progress import alive_bar
from tws_clients.base import TWSWrapper
from tws_clients.base import TWSClient
from tws_clients.data_extractor import HistoricalDataExtractor


def extractor(ticker, end_date, end_time, duration, bar_size, what_to_show, use_rth,
              date_format, keep_upto_date, chart_options, create_data_dump, verbose, debug):
    client = HistoricalDataExtractor(end_date=end_date, end_time=end_time, duration=duration,
                                     bar_size=bar_size, what_to_show=what_to_show, use_rth=use_rth,
                                     date_format=date_format, keep_upto_date=keep_upto_date,
                                     chart_options=chart_options, create_data_dump=create_data_dump,
                                     verbose=verbose, debug=debug)
    client.extract_historical_data(ticker)
    return client.data


# TODO: correct default values
def extract_historical_data(tickers=(), end_date='20200101', end_time='15:01:00', duration='1 D',
                            bar_size='1 min', what_to_show='TRADES', use_rth=1, date_format=1,
                            keep_upto_date=False, chart_options=(), create_data_dump=False,
                            verbose=False, debug=False):
    """
        A wrapper function around HistoricalDataExtractor, that pulls data from TWS for the given tickers.
        Designed to provide a multi-threaded extraction mechanism.
        @param tickers: ticker ID (ex: 1301)
        @param end_date: end date (ex: '20201126')
        @param end_time: end time (ex: '20201126 15:00:01')
        @param duration: the amount of time to go back from end_date_time (ex: '1 D')
        @param bar_size: valid bar size or granularity of data (ex: '1 min')
        @param what_to_show: the type of data to retrieve (ex: 'TRADES')
        @param use_rth: 1 means retrieve data withing regular trading hours, else 0
        @param date_format: format for bar data, 1 means yyyyMMdd, 0 means epoch time
        @param keep_upto_date: setting to True will continue to return unfinished bar data
        @param chart_options: to be documented
        @param create_data_dump: toggle to create extract ticker data into a JSON file
        @param verbose: increase verbosity of the program
        @param debug: allow to debug messages to be shown on console
        @return: an array of dictionaries, containing relevant data for each ticker
    """
    data = {}
    total = len(tickers)
    with alive_bar(total=total, title='Data Extraction', calibrate=50) as bar:
        for i in range(total):
            ticker = tickers[i]
            data[ticker] = extractor(ticker, end_date, end_time, duration, bar_size, what_to_show,
                                     use_rth, date_format, keep_upto_date, chart_options,
                                     create_data_dump, verbose, debug)
            bar()  # update progress bar
    return data


if __name__ == '__main__':
    import json
    tickers = [1301, 1302, 1303]
    data = extract_historical_data(tickers,
                                   end_date='20201230',
                                   end_time='09:01:00',
                                   duration='1 D')
    print(json.dumps(data, indent=2, sort_keys=True))
