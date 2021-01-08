#! TWS-Project/venv/bin/python3.9

"""
    Historical data extractor, written around TWS API(reqHistoricalData)
    =ArrayFormula(IF(ROW(A:A)=1, "ID", IF(B:B="", "", (ROW(B:B)-1))))
"""

from tws_clients import TWSWrapper
from tws_clients import TWSClient
from helpers import create_stock
from helpers import get_logger
from helpers import make_dirs
from json import dumps
from os.path import dirname
from os.path import join
from os import walk
from os import name as os_name
from itertools import chain
import signal
from time import sleep

OS_IS_UNIX = os_name == 'posix'
PROJECT_DIRECTORY = dirname(dirname(__file__))
flatten = chain.from_iterable


class HistoricalDataExtractor(TWSWrapper, TWSClient):

    def __init__(self, end_date='20210101', end_time='15:01:00', duration='1 D', bar_size='1 min',
                 what_to_show='TRADES', use_rth=1, date_format=1, keep_upto_date=False, chart_options=(),
                 create_data_dump=False, output_location=None, verbose=False, debug=False, logger=None,
                 timeout=3, max_attempts=3):
        TWSWrapper.__init__(self)
        TWSClient.__init__(self, wrapper=self)
        self.ticker = None
        self._target_tickers = []
        self._proccesed_tickers = []
        self.is_connected = False
        self.directory_maker = make_dirs
        # TODO: implement broken connection handler
        self.connection_is_broken = False
        self.handshake_completed = False
        self.extraction_completed = False
        self.end_date = end_date
        self.end_time = end_time
        self.duration = duration
        self.bar_size = bar_size
        self.what_to_show = what_to_show
        self.use_rth = use_rth
        self.date_format = date_format
        self.keep_upto_date = keep_upto_date
        self.chart_options = chart_options
        self.timeout = timeout
        self.create_data_dump = create_data_dump
        self.debug = debug
        self.output_location = output_location or join(PROJECT_DIRECTORY,
                                                       'data_files',
                                                       'historical_data',
                                                       self.end_date)
        log_level = 'DEBUG' if debug else ('INFO' if verbose else 'CRITICAL')
        self.logger = logger or get_logger(__name__, log_level)
        self.max_attempts = max_attempts
        self.data = None

    def _init_data_tracker(self, ticker):
        """
            Initializes the data tracker.
            Should be invoked for every new ticker.
        """
        _meta_data = {'start': None, 'end': None, 'status': False, 'attempt': 0, '_error_stack': [], 'output_file': ''}
        _initial_data = {'meta_data': _meta_data, 'bar_data': []}
        self.data[ticker] = _initial_data

    def _reset_attr(self, **kwargs):
        """
            Resets the value of the given attributes
            @param kwargs: keyword argument to reset the attribute
        """
        for attr, value in kwargs.items():
            if value is None:
                raise ValueError(f'Attribute {attr} can not be None.')
            setattr(self, attr, value)

    def _set_timeout(self):
        """
            Break the call running longer than timeout threshold.
            Call error method with code=-1 on timeout.
            NOTE: Not supported on Windows OS yet.
        """
        # noinspection PyUnusedLocal
        def _handle_timeout(signum, frame):
            self.error(self.ticker, -1, f'Historical data request timed out after: {self.timeout} seconds')
        # TODO: final alarm
        if OS_IS_UNIX:
            signal.signal(signal.SIGALRM, _handle_timeout)
            signal.alarm(self.timeout)

    def _request_historical_data(self, ticker):
        """
            Sends request to TWS API
        """
        self._set_timeout()
        contract = create_stock(ticker)
        end_date_time = f'{self.end_date} {self.end_time}'
        self.data[ticker]['meta_data']['attempt'] += 1
        self.logger.info(f'Requesting historical data for ticker: {ticker}')
        print(f'Requesting historical data for ticker: {ticker}')
        self.reqHistoricalData(ticker, contract, end_date_time, self.duration, self.bar_size, self.what_to_show,
                               self.use_rth, self.date_format, self.keep_upto_date, self.chart_options)

    def _create_data_dump(self, ticker, data):
        """
            Evaluates extraction status and saves ticker data to relevant file.
            :param ticker: ticker ID
            :param data: historical data in a dictionary
        """
        print(f'Creating data dump for: {ticker}')
        print(f'Data:\n{dumps(data, indent=2, sort_keys=True)}')
        if self.create_data_dump:
            status_directory = 'success' if data['meta_data']['status'] else 'failure'
            target_directory = join(self.output_location, status_directory)
            target_file = join(target_directory, f'{ticker}.json')
            self.directory_maker(target_directory)
            # if not (isfile(target_file)):
            self.data[ticker]['meta_data']['output_file'] = target_file
            self.save_ticker_file(data, target_file)

    def _extraction_check(self, ticker):
        """
            Returns True if:
                - Bar data has been extracted and saved to success location
                                    OR
                - Error data has been extracted and saved to failure location
        """
        meta_data = self.data[ticker]['meta_data']
        return meta_data['status'] or meta_data['attempt'] >= self.max_attempts

    def _get_processed_tickers(self):
        """
            Read output location and findout tickers for which data dump has been created.
            :return: list of processed tickers
        """
        # get all tickers for which a data dump has been created
        # success & failure directories, both are included
        # get all files from self.output_location
        # filter out files ending with .json
        # split filename and convert to int, to get ticker ID
        return list(
                        map(lambda z: int(z.split('.')[0]),
                            filter(lambda y: y.endswith('.json'),
                                   flatten(map(lambda x: x[2],
                                               walk(self.output_location)
                                               )
                                           )
                                   )
                            )
                    )

    def _get_target_ticker(self):
        """
            :return: First ticker from unprocessed tickers
        """
        unprocessed_tickers = list(set(self._target_tickers).difference(self._get_processed_tickers()))
        if bool(unprocessed_tickers):
            return unprocessed_tickers[0]

    def save_ticker_file(self, data, file_path):
        """
            Saves ticker data to a JSON file.
            @param data: dictonary containing ticker's historical data or error info
            @param file_path: target file where data is to be saved
        """
        indent = 4 if self.debug else 2
        with open(file_path, 'w') as f:
            f.writelines(dumps(data, sort_keys=True, indent=indent))
            self.logger.info(f'Written ticker data at location: {file_path}')

    def connect(self, host='127.0.0.1', port=7497, client_id=10):
        """
            Establishes a connection to TWS API
            Sets 'is_connected' to True after a successful connection
            @param host: IP Adrress of the machine hosting the TWS app
            @param port: Port number on which TWS is listenign to new connections
            @param client_id: Client ID using which connection will be made
        """
        if not self.is_connected:
            super().connect(host, port, client_id)
            self.is_connected = self.isConnected()
            self.run()

    def disconnect(self):
        """
            Disconnects the client from TWS API
        """
        self.is_connected = False
        super().disconnect()

    def run(self):
        """
            Triggers the infinite message loop defined within parent class(EClient):
                - Completes the initial handshake
                - Triggers data extraction from error method
            Note: User must connect to TWS API prior to calling this method.
        """
        if not self.is_connected:
            raise ConnectionError(f'Not yet connected to TWS API, invoke "connect" method with valid arguments.')
        super().run()

    def extract_historical_data(self, tickers=None):
        """
            Performs historical data extraction on tickers provided as input.
        """
        if tickers is not None:
            self._reset_attr(_target_tickers=tickers, data={}, extraction_completed=False)
        if not self.is_connected:
            self.connect()
        # _target_ticker = self._get_target_ticker()
        unprocessed_tickers = list(set(self._target_tickers).difference(self._proccesed_tickers))
        print(f'UU: {unprocessed_tickers}')
        if bool(unprocessed_tickers):
            _target_ticker = unprocessed_tickers[0]
            if _target_ticker not in self.data:
                self._init_data_tracker(_target_ticker)
            ticker_is_not_processed = not self._extraction_check(_target_ticker)
            self.logger.info(f'Extracting data for: {_target_ticker}')
            print(f'Extracting data for: {_target_ticker} | Type: {type(_target_ticker)}')
            if ticker_is_not_processed:
                self._request_historical_data(_target_ticker)
            else:
                self._create_data_dump(_target_ticker, self.data[_target_ticker])
                self._proccesed_tickers.append(_target_ticker)
                self.extract_historical_data()
        else:
            print(f'Ran out of tickers to process...')
            self.disconnect()

    def historicalData(self, id, bar):
        """
            This method is receives data from TWS API, invoked automatically after "reqHistoricalData".
            :param id: respresents ticker ID
            :param bar: a bar object that contains OHLCV data
        """
        session = 1 if int(bar.date.split(' ')[-1].split(':')[0]) < 12 else 2
        bar = {'time_stamp': bar.date, 'open': bar.open, 'high': bar.high, 'low': bar.low,
               'close': bar.close, 'volume': bar.volume, 'average': bar.average,
               'count': bar.barCount, 'session': session}
        self.data[id]['bar_data'].append(bar)

    def historicalDataEnd(self, id, start, end):
        """
            This method is called automatically after all the bars have been generated by "historicalData".
            Marks the completion of historical data generation for a given ticker.
            :param id: ticker ID
            :param start: starting timestamp
            :param end: ending timestamp
        """
        self.logger.info(f'Data extraction completed for ticker: {id}')
        self.data[id]['meta_data']['start'] = start
        self.data[id]['meta_data']['end'] = end
        self.data[id]['meta_data']['status'] = True
        self._create_data_dump(id, self.data[id])
        self._proccesed_tickers.append(id)
        sleep(0.1)
        self.extract_historical_data()
        # self.extraction_completed = True
        # self.disconnect()

    def error(self, id, code, message):
        """
            Error handler for all API calls, invoked directly by EClient methods
            :param id: error ID (-1 means no informational message, not true error)
            :param code: error code, defines error type
            :param message: error message, information about error
        """
        # -1 is not a true error, but only an informational message
        # initial call to run invokes this method with error ID = -1
        print(f'Error: ID: {id} | Code: {code} | String: {message}')
        if id == -1:
            self.logger.info(f'{message}')
            # error code 502 indicates connection failure
            if code == 502:
                self.logger.critical(f'Connection Failure: {message}, Error Code: {code}')
                raise ConnectionError('Could not connect to TWS, please ensure TWS is running.')
            # error codes 2103, 2105, 2157 indicate broken connection
            if code in [2103, 2105, 2157]:
                self.logger.critical(f'Insecure Connection: {message}, Error code: {code}')
                raise ConnectionError(f'Detected broken connection, please try re-connecting the webfarms in TWS.')
            # error codes 2104, 2106, 2158 indicate connection is OK
            if code in [2104, 2106, 2158]:
                self.logger.info(message)
            # last error code received, marks the completion of initial hand-shake
            # call back the extractor to start pulling historical data
            if code == 2158:
                self.logger.info(f'Secure connection established to TWS API, initial handshake completed.')
                self.handshake_completed = True
        else:
            print(f'\n\n------------------\n\n')
            self.logger.error(f'{message}: Ticker ID: {id}, Error Code: {code}')
            meta_data = self.data[id]['meta_data']
            attempts = meta_data['attempt']

            if attempts <= self.max_attempts:
                error = {'code': code, 'message': message}
                meta_data['_error_stack'].append(error)
            else:
                self._create_data_dump(id, self.data[id])
                self._proccesed_tickers.append(id)
                sleep(0.1)
                # self.cancelHistoricalData(id)
                # if not self.extraction_completed:
                # self._create_data_dump()
                # self.extraction_completed = True

            # -1 indicates a timeout
            # 162 indicates that HMDS return no data
            # 322 indicates that API request limit(50) has been breached
            # 504 indicates no connection
            if code in [-1, 162, 322, 504]:
                self.cancelHistoricalData(id)
                self.logger.warning(f'Canceling: {id} | {code} | {message}')

        self.extraction_completed = self._target_tickers == self._proccesed_tickers
        if self.handshake_completed:
            if not self.extraction_completed:
                self.extract_historical_data()
            else:
                self.disconnect()


if __name__ == '__main__':
    from time import time
    from data_files.input_data import test_tickers

    test_tickers = test_tickers[:15]
    print(f'Target: {test_tickers}')
    total_tickers = len(test_tickers)
    start = time()
    data = {}
    extractor = HistoricalDataExtractor(end_date='20210106',
                                        end_time='09:01:00',
                                        create_data_dump=True,
                                        timeout=3000,
                                        debug=True)
    extractor.extract_historical_data(test_tickers)
    # print(dumps(extractor.data, indent=2, sort_keys=True))

    # for i in range(total_tickers):
    #     ticker = test_tickers[i]
    #     extractor = HistoricalDataExtractor(end_date='20210106',
    #                                         end_time='09:01:00',
    #                                         create_data_dump=True,
    #                                         timeout=3,
    #                                         debug=True)
    # extractor.extract_historical_data(ticker)
    # data[ticker] = extractor.data
    # print(f'=== Processed: {i+1} / {total_tickers} ===')
    end = time()
    lapsed = round(end - start, 3)
    print(dumps(data, indent=2, sort_keys=True))
    print(f'Time Lapsed: {lapsed} seconds')
