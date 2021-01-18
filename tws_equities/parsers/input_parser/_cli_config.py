from datetime import datetime as dt
from tws_equities.parsers.input_parser._input_types import INPUT_TYPES
from tws_equities.parsers.input_parser._ticker_actions import TICKER_ACTIONS


_DATE_FORMAT = '%Y%m%d'
_CURRENT_DATE = dt.today().date().strftime(_DATE_FORMAT)

_LIST_ACTION = TICKER_ACTIONS['list']
_FILE_ACTION = TICKER_ACTIONS['file']
_URL_ACTION = TICKER_ACTIONS['url']


# to provide users with new options, add a dictionary objec:with in the section below
# these objects will serve as optional arguments
# options built for downloader
_START_DATE = dict(name='--start-date', flag='-sd', type=INPUT_TYPES['date'], default=_CURRENT_DATE,
                   dest='start_date', help='Start date for data extraction, default is None.'
                                         '(Expected format: "YYYYMMDD")')

_END_DATE = dict(name='--end-date', flag='-ed', type=INPUT_TYPES['date'], default=_CURRENT_DATE,
                 dest='end_date', help='End date for data extraction, default is current date.'
                                       '(Expected format: "YYYYMMDD")')

_END_TIME = dict(name='--end-time', flag='-et', type=INPUT_TYPES['time'], default='15:01:00',
                 dest='end_time', help='End time for data extraction, default is "15:01:00".'
                                       '(Expected format: "HH:MM:SS")')

_DURATION = dict(name='--duration', flag='-d', type=INPUT_TYPES['duration'], default='1 D', dest='duration',
                 help='The amount of time to go back from the given end date and time.(default: "1 D")')

_BAR_SIZE = dict(name='--bar-size', flag='-b', type=INPUT_TYPES['bar_size'], default='1 min', dest='bar_size',
                 help='The granularity of the data to be extracted.(default: "1 min")')

_WHAT_TO_SHOW = dict(name='--what-to-show', flag='-w', type=str, default='TRADES', dest='what_to_show',
                     choices=['TRADES'],  # 'MIDPOINT', 'BID', 'ASK'],
                     help='The type of data to retrieve, only TRADE data is supported currently.')

_USE_RTH = dict(name='--use-rth', flag='-u', type=int, default=1, dest='use_rth', choices=[1],
                help='Whether(1) or not(0) to retrieve data generated only within Regular Trading Hours(RTH)'
                     ', currently only 1 is supported.')


# options built for CSV maker
# TODO: provide default values for data & output locations
_DATA_LOCATION = dict(name='--data-location', flag='-d', default=None, dest='data_location',
                      help='Allows the user to choose a location from where raw data is to be read.')
_OUTPUT_LOCATION = dict(name='--output-location', flag='-o', default=None, dest='output_location',
                        help='Allows the user to choose a location where the output file will be saved.')
_FORMAT = dict(name='--format', flag='-f', type=str, default='csv', choices=['csv'], dest='format',
               help='Allows the user to choose the final data format, currently only CSV is supported.')


# optional arguments built specifically for tickers command, do not alter these
_LIST = dict(name='--list', flag='-l', type=int, nargs='+', dest='tickers', default=None,
             action=_LIST_ACTION, help='Accepts multiple ticker IDs separated by white space.')

_FILE = dict(name='--file', flag='-f', type=INPUT_TYPES['file'], dest='tickers', action=_FILE_ACTION,
             help='Accepts a file path that contains ticker IDs, '
                  'only CSV file are supported that must have a column called "ecode". '
                  '(Supports relative paths.)')

_URL = dict(name='--url', flag='-u', type=INPUT_TYPES['url'], dest='tickers', action=_URL_ACTION,
            help='Accepts a URL to Google Sheets containing ticker IDs, '
                 'this feature is still under development and not avialable for usage yet.')


# use above mentioned options, to build a config for user-facing commands
# build config for tickers command
_OPTIONAL_ARGUMENTS = dict(list=_LIST, file=_FILE, url=_URL)
_POSITIONAL_ARGUMENTS = None
_TICKERS = dict(help='Use this command to pass custom ticker ID(s) as an input to the program.',
                description='Allows the user to pass tickers as an input to the program, provides 3 '
                            'different options to do so but the user must ensure that they use only one at a '
                            'time. Otherwise, last selected option will be chosen to read input.',
                optional_arguments=_OPTIONAL_ARGUMENTS, positional_arguments=_POSITIONAL_ARGUMENTS)


# building config for run command
_OPTIONAL_ARGUMENTS = dict(start_date=_START_DATE, end_date=_END_DATE, end_time=_END_TIME, duration=_DURATION,
                           bar_size=_BAR_SIZE, what_to_show=_WHAT_TO_SHOW, use_rth=_USE_RTH)
_POSITIONAL_ARGUMENTS = dict(tickers=_TICKERS)
_RUN = dict(help='Use this command to trigger a complete run that would download bar-data, convert & save it '
                 'to a CSV file and finally present the user with extraction metrics.',
            description='Allows the user to trigger an end to end run, which would include data download, '
                        'conversion to CSV & metrics generation.',
            optional_arguments=_OPTIONAL_ARGUMENTS, positional_arguments=_POSITIONAL_ARGUMENTS)

# building config for download command
# TODO: output location
_OPTIONAL_ARGUMENTS = dict(end_date=_END_DATE, end_time=_END_TIME, duration=_DURATION,
                           bar_size=_BAR_SIZE, what_to_show=_WHAT_TO_SHOW,
                           use_rth=_USE_RTH)
_POSITIONAL_ARGUMENTS = dict(tickers=_TICKERS)
_DOWNLOAD = dict(help='Use this command to only download and save bar-data in JSON format.',
                 description='Allows the user to trigger data download from TWS API, which will be saved in '
                             'JSON format.',
                 optional_arguments=_OPTIONAL_ARGUMENTS, positional_arguments=_POSITIONAL_ARGUMENTS)

# building config for download command
# TODO: input location
_OPTIONAL_ARGUMENTS = dict(end_date=_END_DATE, url=_URL, file=_FILE)
_POSITIONAL_ARGUMENTS = None  # dict(tickers=_TICKERS)
_UPLOAD = dict(help='Use this command to upload CSV files to a google drive location. This feature is yet to '
                    'be built and not available for usage yet.',
               description='Allows the user to upload CSV file to google drive. Not implemented yet.',
               optional_arguments=_OPTIONAL_ARGUMENTS, positional_arguments=_POSITIONAL_ARGUMENTS)

# building config for download command
_OPTIONAL_ARGUMENTS = dict(end_date=_END_DATE, data_location=_DATA_LOCATION, output_location=_OUTPUT_LOCATION,
                           format=_FORMAT)
_POSITIONAL_ARGUMENTS = None  # dict(tickers=_TICKERS)
_CONVERT = dict(help='Use this command to convert & save already downloaded data to a CSV file.',
                description='Allows the user to convert & save downloaded JSON data to a CSV file.',
                optional_arguments=_OPTIONAL_ARGUMENTS, positional_arguments=_POSITIONAL_ARGUMENTS)


# building config for download command
_OPTIONAL_ARGUMENTS = dict(end_date=_END_DATE, data_location=_DATA_LOCATION)
_POSITIONAL_ARGUMENTS = None  # dict(tickers=_TICKERS)
_METRICS = dict(help='Use this command to generate, display & save extraction metrics for a given date. ',
                description='Allows the user to generate, display & save extraction metrics for a given '
                            'date. This command expectes that data is already downloaded and available in '
                            'CSV format.',
                optional_arguments=_OPTIONAL_ARGUMENTS, positional_arguments=_POSITIONAL_ARGUMENTS)


# build an over-all config for all the available commands
# each keyword argument represents a distinct command
CLI_CONFIG = dict(run=_RUN, download=_DOWNLOAD, upload=_UPLOAD, convert=_CONVERT, metrics=_METRICS)
