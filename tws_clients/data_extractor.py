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
from os.path import isfile
from os.path import join
from os import name as os_name
import signal


OS_IS_UNIX = os_name == 'posix'


class HistoricalDataExtractor(TWSWrapper, TWSClient):

    def __init__(self, end_date='20210101', end_time='15:01:00', duration='1 D', bar_size='1 min',
                 what_to_show='TRADES', use_rth=1, date_format=1, keep_upto_date=False, chart_options=(),
                 create_data_dump=False, output_location=None, verbose=False, debug=False, logger=None,
                 timeout=3, max_attempts=3):
        TWSWrapper.__init__(self)
        TWSClient.__init__(self, wrapper=self)
        self.ticker = None
        self.is_connected = False
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
        self.output_location = output_location or 'data_files/historical_data'
        log_level = 'DEBUG' if debug else ('INFO' if verbose else 'CRITICAL')
        self.logger = logger or get_logger(__name__, log_level)
        self.max_attempts = max_attempts
        self.data = None

    def _init_data_tracker(self):
        """
            Initializes the data tracker.
            Should be invoked for every new ticker.
        """
        _meta_data = {'start': None, 'end': None, 'status': False, 'attempt': 0, '_error_stack': [], 'output_file': ''}
        _initial_data = {'meta_data': _meta_data, 'bar_data': []}
        self.logger.debug('Data tracker was initialized.')
        return _initial_data

    def _reset_attr(self, **kwargs):
        """
            Resets the value of the given attributes
            @param kwargs: keyword argument to reset the attribute
        """
        for attr, value in kwargs.items():
            if value is None:
                raise ValueError(f'Attribute {attr} can not be None.')
            setattr(self, attr, value)

    def _request_historical_data(self):
        """
            Sends request to TWS API
        """
        # noinspection PyUnusedLocal
        def _handle_timeout(signum, frame):
            self.error(self.ticker, -1, f'Historical data request timed out after: {self.timeout} seconds')
        # TODO: final alarm
        if OS_IS_UNIX:
            signal.signal(signal.SIGALRM, _handle_timeout)
            signal.alarm(self.timeout)
        self.logger.info(f'Requesting historical data for ticker: {self.ticker}')
        contract = create_stock(self.ticker)
        end_date_time = f'{self.end_date} {self.end_time}'
        self.data['meta_data']['attempt'] += 1
        self.reqHistoricalData(self.ticker, contract, end_date_time, self.duration, self.bar_size, self.what_to_show,
                               self.use_rth, self.date_format, self.keep_upto_date, self.chart_options)

    def _create_data_dump(self):
        """
            Evaluates extraction status and saves ticker data to relevant file.
        """
        if self.create_data_dump:
            status_directory = 'success' if self.data['meta_data']['status'] else 'failure'
            target_directory = join(dirname(dirname(__file__)), self.output_location,
                                    self.end_date, status_directory)
            target_file = join(target_directory, f'{self.ticker}.json')
            # create relevant directories
            make_dirs(target_directory)
            if not(isfile(target_file)):
                self.save_ticker_file(self.data, target_file)
            self.data['meta_data']['output_file'] = target_file

    def _extraction_check(self):
        """
            Returns True if:
                - Bar data has been extracted and saved to success location
                                    OR
                - Error data has been extracted and saved to failure location
        """
        return isfile(self.data['meta_data']['output_file'])

    def save_ticker_file(self, data, file_path):
        """
            Saves ticker data to a JSON file.
            @param data: dictonary containing ticker's historical data or error info
            @param file_path: target file where data is to be saved
        """
        indent = None  # 4 if self.debug else None
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
            self.logger.info(f'Client successfully connected to TWS API')

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

    def extract_historical_data(self, ticker=None):
        """
            Performs historical data extraction on tickers provided at the time of initialization
            User must first connect to TWS by invoking "connect" method
        """
        if ticker is not None:
            self._reset_attr(ticker=ticker, data=self._init_data_tracker(), extraction_completed=False)
        if not self.is_connected:
            self.connect()
        if not self.extraction_completed and self.data['meta_data']['attempt'] < self.max_attempts:
            self.logger.info(f'Extracting data for: {ticker}')
            self._request_historical_data()
        else:
            self._create_data_dump()
            self.extraction_completed = True
            self.disconnect()

    def historicalData(self, id, bar):
        """
            This method is receives data from TWS API, invoked automatically after "reqHistoricalData".
            @param id: respresents ticker ID
            @param bar: a bar object that contains OHLCV data for a given timestamp
        """
        bar = {'time_stamp': bar.date, 'open': bar.open, 'high': bar.high,
               'low': bar.low, 'close': bar.close, 'volume': bar.volume,
               'average': bar.average, 'count': bar.barCount,
               'session': 1 if int(bar.date.split(' ')[-1].split(':')[0]) < 12 else 2}
        self.data['bar_data'].append(bar)

    def historicalDataEnd(self, id, start, end):
        """
            This method is called automatically after all the bars have been generated by "historicalData".
            Marks the completion of historical data generation for a given ticker.
            @param id: ticker ID
            @param start: starting timestamp
            @param end: ending timestamp
        """
        self.logger.info(f'Data extraction completed for ticker: {id}')
        self.data['meta_data']['start'] = start
        self.data['meta_data']['end'] = end
        self.data['meta_data']['status'] = True
        self._create_data_dump()
        self.extraction_completed = True
        self.disconnect()

    def error(self, id, code, message):
        """
            Error handler for all API calls, invoked directly by EClient methods
            @param id: error ID (-1 means no informational message, not true error)
            @param code: error code, defines error type
            @param message: error message, information about error
        """
        # -1 is not a true error, but only an informational message
        # initial call to run invokes this method with error ID = -1
        # print(f'Error: ID: {id} | Code: {code} | String: {message}')
        if id == -1:
            self.logger.info(f'{message}')
            # error code 502 indicates connection failure
            if code == 502:
                # TODO: to be implemented!
                pass
            # error codes 2103, 2105, 2157 indicate broken connection
            if code in [2103, 2105, 2157]:
                # TODO: to be implemented!
                self.logger.warning(f'Insecure Connection: {message}, Error code: {code}')
                pass
            # error codes 2104, 2106, 2158 indicate connection is OK
            if code in [2104, 2106, 2158]:
                # TODO: to be implemented!
                pass
            # last error code received, marks the completion of initial hand-shake
            # call back the extractor to start pulling historical data
            if code == 2158:
                self.handshake_completed = True
        else:
            self.logger.error(f'{message}: Ticker ID: {id}, Error Code: {code}')
            meta_data = self.data['meta_data']
            attempts = meta_data['attempt']

            if attempts <= self.max_attempts:
                error = {'code': code, 'message': message}
                meta_data['_error_stack'].append(error)
            else:
                if not self.extraction_completed:
                    self._create_data_dump()
                    self.extraction_completed = True

            # -1 indicates a timeout
            # 162 indicates that HMDS return no data
            # 322 indicates that API request limit(50) has been breached
            # 504 indicates no connection
            if code in [-1, 162, 322, 504]:
                self.cancelHistoricalData(id)
                self.logger.warning(f'Canceling: {id} | {code} | {message}')

        if self.handshake_completed:
            if not self.extraction_completed:
                self.extract_historical_data()
            else:
                self.disconnect()

    def get_data(self):
        return self.data


if __name__ == '__main__':
    from time import time
    from data_files.input_data import load_csv

    test_tickers = [1301, 1302, 1303, 3434, 3450]
    total_tickers = len(test_tickers)
    start = time()
    data = {}
    for i in range(total_tickers):
        ticker = test_tickers[i]
        extractor = HistoricalDataExtractor(end_date='20200601',
                                            end_time='15:01:00',
                                            create_data_dump=True,
                                            timeout=3,
                                            debug=True)
        extractor.extract_historical_data(ticker)
        # data[ticker] = extractor.data
        print(f'=== Processed: {i+1} / {total_tickers} ===', end='\n')
    end = time()
    lapsed = round(end - start, 3)
    print(dumps(data, indent=2, sort_keys=True))
    print(f'Time Lapsed: {lapsed} seconds')
