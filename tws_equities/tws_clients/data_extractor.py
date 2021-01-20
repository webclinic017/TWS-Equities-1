#! TWS-Project/venv/bin/python3.9

"""
    Historical data extractor, written around TWS API(reqHistoricalData)
"""

from tws_equities.tws_clients import TWSWrapper
from tws_equities.tws_clients import TWSClient
from tws_equities.helpers import create_stock
from tws_equities.helpers import get_logger
from tws_equities.helpers import make_dirs
from json import dumps
# from os.path import dirname
# from os.path import isfile
# from os.path import join
# from os import walk
from os import name as os_name
from itertools import chain
import signal


OS_IS_UNIX = os_name == 'posix'
# PROJECT_DIRECTORY = dirname(dirname(__file__))
_LOGGER = get_logger(__name__)
flatten = chain.from_iterable


class HistoricalDataExtractor(TWSWrapper, TWSClient):

    def __init__(self, end_date='20210101', end_time='15:01:00', duration='1 D', bar_size='1 min',
                 what_to_show='TRADES', use_rth=1, date_format=1, keep_upto_date=False, chart_options=(),
                 logger=None, timeout=3, max_attempts=3):
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
        self.logger = logger or _LOGGER
        self.max_attempts = max_attempts
        self.data = None

    def _init_data_tracker(self, ticker):
        """
            Initializes the data tracker.
            Should be invoked for every new ticker.
        """
        _meta_data = {'start': None, 'end': None, 'status': False, 'attempts': 0,
                      '_error_stack': [], 'total_bars': 0, 'ecode': ticker}
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

    def _log_message(self, message, level):
        """
        Logs message if logger has been initialized.
        :param message: message to log
        :param level: level of the message
    """
        if self.logger is not None:
            level_map = {
                            'debug': self.logger.debug,
                            'info': self.logger.info,
                            'warning': self.logger.warning,
                            'error': self.logger.error,
                            'critical': self.logger.critical
                        }
            log = level_map.get(level, 'error')
            log(message)

    def _set_timeout(self, ticker):
        """
            Break the call running longer than timeout threshold.
            Call error method with code=-1 on timeout.
            NOTE: Not supported on Windows OS yet.
        """
        # noinspection PyUnusedLocal
        def _handle_timeout(signum, frame):
            self.error(ticker, -1, f'Historical data request timed out after: {self.timeout} seconds')
        # TODO: final alarm
        if OS_IS_UNIX:
            signal.signal(signal.SIGALRM, _handle_timeout)
            signal.alarm(self.timeout)

    def _request_historical_data(self, ticker):
        """
            Sends request to TWS API
        """
        self._set_timeout(ticker)
        contract = create_stock(ticker)
        end_date_time = f'{self.end_date} {self.end_time}'
        self._log_message(f'Requesting historical data for ticker: {ticker}', level='info')
        self.data[ticker]['meta_data']['attempts'] += 1
        self.reqHistoricalData(ticker, contract, end_date_time, self.duration, self.bar_size,
                               self.what_to_show, self.use_rth, self.date_format, self.keep_upto_date,
                               self.chart_options)

    # def _create_data_dump(self, ticker, data):
    #     """
    #         Evaluates extraction status and saves ticker data to relevant file.
    #         :param ticker: ticker ID
    #         :param data: historical data in a dictionary
    #     """
    #     if self.create_data_dump:
    #         status_directory = 'success' if data['meta_data']['status'] else 'failure'
    #         target_directory = join(self.output_location, status_directory)
    #         target_file = join(target_directory, f'{ticker}.json')
    #         self.directory_maker(target_directory)
    #         self.data[ticker]['meta_data']['output_file'] = target_file
    #         data_has_not_been_saved = not((isfile(target_file)) or (isfile(join(self.output_location,
    #                                                                             'success',
    #                                                                             f'{ticker}.json'))))
    #         if data_has_not_been_saved:
    #             self.save_ticker_file(data, target_file)

    def save_ticker_file(self, data, file_path):
        """
            Saves ticker data to a JSON file.
            @param data: dictonary containing ticker's historical data or error info
            @param file_path: target file where data is to be saved
        """
        with open(file_path, 'w') as f:
            f.writelines(dumps(data, sort_keys=True, indent=1))
            self._log_message(f'Written ticker data at location: {file_path}', level='info')

    def _extraction_check(self, ticker):
        """
            Returns True if:
                - Bar data has been extracted and saved to success location
                                    OR
                - Error data has been extracted and saved to failure location
        """
        meta_data = self.data[ticker]['meta_data']
        # data_dumped = isfile(join(self.output_location, 'success', f'{ticker}.json'))
        status = meta_data['status']
        max_attempts_reached = meta_data['attempts'] >= self.max_attempts
        return status or max_attempts_reached

    # def _get_processed_tickers(self):
    #     """
    #         Read output location and findout tickers for which data dump has been created.
    #         :return: list of processed tickers
    #     """
    #     get all tickers for which a data dump has been created
    #     success & failure directories, both are included
    #     get all files from self.output_location
    #     filter out files ending with .json
    #     split filename and convert to int, to get ticker ID
        # return list(
        #                 map(lambda z: int(z.split('.')[0]),
        #                     filter(lambda y: y.endswith('.json'),
        #                            flatten(map(lambda x: x[2],
        #                                        walk(self.output_location)
        #                                        )
        #                                    )
        #                            )
        #                     )
        #             )

    # def _get_target_ticker(self):
    #     """
    #         :return: First ticker from unprocessed tickers
    #     """
    #     unprocessed_tickers = list(set(self._target_tickers).difference(self._get_processed_tickers()))
    #     if bool(unprocessed_tickers):
    #         return unprocessed_tickers[0]

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
        self._reset_attr(is_connected=False, handshake_completed=False)
        super().disconnect()

    def run(self):
        """
            Triggers the infinite message loop defined within parent class(EClient):
                - Completes the initial handshake
                - Triggers data extraction from error method
            Note: User must connect to TWS API prior to calling this method.
        """
        if not self.is_connected:
            raise ConnectionError(f'Not connected to TWS API, please launch TWS and enable API settings.')
        super().run()

    def extract_historical_data(self, tickers=None):
        """
            Performs historical data extraction on tickers provided as input.
        """
        if tickers is not None:
            self._reset_attr(_target_tickers=tickers, data={})
        if not self.is_connected:
            self.connect()
        unprocessed_tickers = list(set(self._target_tickers).difference(self._proccesed_tickers))
        if bool(unprocessed_tickers):
            _target_ticker = unprocessed_tickers[0]
            if _target_ticker not in self.data:
                self._init_data_tracker(_target_ticker)
            ticker_is_not_processed = not self._extraction_check(_target_ticker)
            if ticker_is_not_processed:
                self._log_message(f'Extracting data for: {_target_ticker}', level='info')
                self._request_historical_data(_target_ticker)
            else:
                # self._create_data_dump(_target_ticker, self.data[_target_ticker])
                self._proccesed_tickers.append(_target_ticker)
                self.extract_historical_data()
        else:
            self.disconnect()

    def historicalData(self, id, bar):
        """
            This method is receives data from TWS API, invoked automatically after "reqHistoricalData".
            :param id: respresents ticker ID
            :param bar: a bar object that contains OHLCV data
        """
        # extracting hour from date, format: '20210101 09:00:00'
        session = 1 if int(bar.date.split(' ')[-1].split(':')[0]) < 12 else 2
        bar = {'time_stamp': bar.date, 'open': bar.open, 'high': bar.high, 'low': bar.low,
               'close': bar.close, 'volume': bar.volume, 'average': bar.average,
               'count': bar.barCount, 'session': session}
        if bar not in self.data[id]['bar_data']:
            self.data[id]['bar_data'].append(bar)

    def historicalDataEnd(self, id, start, end):
        """
            This method is called automatically after all the bars have been generated by "historicalData".
            Marks the completion of historical data generation for a given ticker.
            :param id: ticker ID
            :param start: starting timestamp
            :param end: ending timestamp
        """
        self._log_message(f'Data extraction completed for ticker: {id}', level='info')
        self.data[id]['meta_data']['start'] = start
        self.data[id]['meta_data']['end'] = end
        self.data[id]['meta_data']['status'] = True
        self.data[id]['meta_data']['total_bars'] = len(self.data[id]['bar_data'])
        # self._create_data_dump(id, self.data[id])
        self._proccesed_tickers.append(id)
        self.extract_historical_data()

    def error(self, id, code, message):
        """
            Error handler for all API calls, invoked directly by EClient methods
            :param id: error ID (-1 means no informational message, not true error)
            :param code: error code, defines error type
            :param message: error message, information about error
        """
        # -1 is not a true error, but only an informational message
        # initial call to run invokes this method with error ID = -1
        # print(f'Error: ID: {id} | Code: {code} | String: {message}')
        if id == -1:
            # error code 502 indicates connection failure
            if code == 502:
                self._log_message(f'Connection Failure: {message}, Error Code: {code}', level='critical')
                raise ConnectionError('Could not connect to TWS, please ensure TWS is running.')
            # error codes 2103, 2105, 2157 indicate broken connection
            if code in [2103, 2105, 2157]:
                self._log_message(f'Insecure Connection: {message}, Error code: {code}', level='critical')
                raise ConnectionError(f'Detected broken connection, please try re-connecting the webfarms '
                                      f'in TWS.')
            # error codes 2104, 2106, 2158 indicate connection is OK
            if code in [2104, 2106, 2158]:
                self._log_message(message, level='info')
            # last error code received, marks the completion of initial hand-shake
            # call back the extractor to start pulling historical data
            if code == 2158:
                self._log_message(f'Secure connection established to TWS API.', level='info')
                self.handshake_completed = True
        else:
            self._log_message(f'{message}: Ticker ID: {id}, Error Code: {code}', level='error')
            meta_data = self.data[id]['meta_data']
            attempts = meta_data['attempts']
            error = {'code': code, 'message': message}
            meta_data['_error_stack'].append(error)

            if attempts >= self.max_attempts:
                # self._create_data_dump(id, self.data[id])
                self._proccesed_tickers.append(id)

            # -1 indicates a timeout
            # 162 indicates that HMDS return no data
            # 322 indicates that API request limit(50) has been breached
            # 504 indicates no connection
            if code in [-1, 322, 504]:
                self.cancelHistoricalData(id)
                self._log_message(f'Canceling: {id} | {code} | {message}', level='error')

        if self.handshake_completed:
            extraction_is_not_completed = self._target_tickers != self._proccesed_tickers
            if extraction_is_not_completed:
                self.extract_historical_data()
            else:
                self.disconnect()


if __name__ == '__main__':
    import json
    tickers = [1301]
    extractor = HistoricalDataExtractor(end_date='20210120', end_time='09:01:00')
    extractor.extract_historical_data(tickers)
    print(json.dumps(extractor.data, indent=1, sort_keys=True))
