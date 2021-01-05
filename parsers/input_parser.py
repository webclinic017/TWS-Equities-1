from argparse import ArgumentParser
from argparse import ArgumentTypeError
from datetime import datetime
from os.path import isfile
from data_files import load_csv
from data_files import test_tickers


class EndDate:

    def __call__(self, end_date):
        _err = 'Expected a date-like string, format: "YYYYMMDD" (Ex: "20200101")'
        # all character must be digits
        # there must be 8 digits in total (YYYYMMDD)
        if not(end_date.isdigit()) or len(end_date) != 8:
            raise ArgumentTypeError(_err)
        try:
            datetime.strptime(end_date, '%Y%m%d')
        except:
            raise ArgumentTypeError(_err)
        return end_date


class EndTime:

    def __call__(self, end_time):
        _err = 'Expected a time-like string in 24-hour format: "HH:MM:SS (Ex: "15:01:00")"'
        try:
            datetime.strptime(end_time, '%H:%M:%S')
        except:
            raise ArgumentTypeError(_err)
        return end_time


class Duration:

    def __call__(self, duration):
        _err = 'Expected a string containing a digit and a unit separated by whitespace (Ex: "1 D").'
        valid_units = ['S', 'D', 'W', 'M', 'Y']
        try:
            digit, unit = duration.split()
            assert digit.isdigit()
            assert unit in valid_units
        except:
            raise ArgumentTypeError(_err)
        return duration


class BarSize:

    def __call__(self, bar_size):
        _err = 'Expected a string containing a digit and a valid unit for bar size (Ex: "1 min").'
        valid_bar_sizes = {
            'secs': [1, 5, 10, 15, 30],
            'min': [1, 2, 3, 5, 10, 15, 20, 30],
            'hour': [1, 2, 3, 4, 8],
            'day': [1],
            'week': [1],
            'month': [1]
        }
        try:
            digit, unit = bar_size.split()
            assert digit.isdigit(), f'{_err}'
            assert unit in list(valid_bar_sizes), f'{_err}\nAcceptable units are: {list(valid_bar_sizes.keys())}'
            assert int(digit) in valid_bar_sizes[unit], f'{_err}\nAcceptable values for given unit({unit}) are: ' \
                                                        f'{valid_bar_sizes[unit]}'
        except Exception as e:
            raise ArgumentTypeError(f'{e}')
        return bar_size


class File:

    def __call__(self, file):
        _err = f'Expected a valid file-path, "{file}" is a non-existent file.'
        try:
            # default value will trigger data load from "ticker.csv" file
            # present at: "data_files/input_data/tickers.csv"
            # test is temporary way to load some dummy tickers
            # TODO: find a better ay to load test tickers(unit tests)
            if file not in ['default', 'test']:
                assert isfile(file)
        except:
            raise ArgumentTypeError(_err)
        return file


class URL:

    def __call__(self, url):
        # TODO: to be implemented
        raise NotImplementedError('URL parsing is not supported yet!')


def load_tickers_from_list(args):
    target_tickers = args.list
    return target_tickers


def load_tickers_from_file(args):
    tickers, file = [], args.file
    # TODO: temporary block for testing
    if file == 'test':
        tickers = test_tickers
    elif file == 'default':
        tickers = load_csv()
    elif file.endswitch('.csv'):
        tickers = load_csv(file)
    else:
        raise NotImplementedError(f'This file type is not supported yet: {file}')
    return tickers


def load_tickers_from_url(args):
    # TODO: Implement with requests!
    raise NotImplementedError(f'To be implemented! User Args: {args}')
    # output = []
    # data = urllib2.urlopen(args.tickers_drive) # it's a file like object and works just like a file
    # for line in data:
    #     output.append(line)
    # return output


def parse_tickers(args):
    """
        Validates that user passed correct values for tickers.
        Adds a new attribute to args called "tickers".
        Removes placeholder keys ('list', 'file', 'url').
        :param args: NameSpace object containing user arguments.
        :return: ticker IDs loaded in a list
    """
    tickers = []
    args_in_a_dict = vars(args)
    expected_keys = ['list', 'file', 'url']
    user_keys = list(filter(lambda x: args_in_a_dict.get(x) is not None, expected_keys))

    # user did not pass an argument for tickers
    if not(bool(user_keys)):
        # TODO: display error message without stacktrace
        # TODO: temporary test tickers, for direct run
        tickers.extend([1301, 1302, 1303, 3434, 3435, 6758, 3050, 7203, 8311])
    else:
        # TODO: prevent user from using multiple keys
        user_key = user_keys[0]
        parser_map = {
                       'list': load_tickers_from_list,
                       'file': load_tickers_from_file,
                       'url': load_tickers_from_url
                     }
        tickers = parser_map[user_key](args)

    # remove keys after extracting relevant data
    for key in expected_keys:
        if key in args_in_a_dict:
            delattr(args, key)

    return tickers


def parse_user_args():
    # TODO: fails if tickers are not passed
    # top-level parser
    parser = ArgumentParser()
    parser.add_argument(
                            '--end-date',
                            '-ed',
                            type=EndDate(),
                            default='20201231',
                            help='End date for data extraction, expected format: "YYYYMMDD"'
                        )
    parser.add_argument(
                            '--end-time',
                            '-et',
                            type=EndTime(),
                            default='15:01:00',
                            help='End date for data extraction, expected format: "YYYYMMDD"'
                        )
    parser.add_argument(
                            '--duration',
                            '-d',
                            type=Duration(),
                            default='1 D',
                            help='The amount of time to go back from the given end date and time.'
                        )
    parser.add_argument(
                            '--bar-size',
                            '-b',
                            type=BarSize(),
                            default='1 min',
                            help='The granularity of the data to be extracted.'
                        )
    parser.add_argument(
                            '--what-to-show',
                            '-w',
                            type=str,
                            default='TRADES',
                            choices=['TRADES', 'MIDPOINT', 'BID', 'ASK'],
                            help='The type of data to retrieve'
                        )
    parser.add_argument(
                            '--use-rth',
                            '-u',
                            type=int,
                            default=1,
                            choices=[1],
                            help='The granularity of the data to be extracted.'
                        )
    parser.add_argument(
                            '--data-dump',
                            '-dd',
                            dest='create_data_dump',
                            default=True,
                            action='store_false',
                            help='Toggle this switch to create a data dump.'
                        )
    parser.add_argument(
                            '--verbose',
                            '-vb',
                            default=False,
                            action='store_true',
                            help='Toggle this switch to increase verbosity, displays info message.'
                        )
    parser.add_argument(
                            '--debug',
                            '-db',
                            default=False,
                            action='store_true',
                            help='Toggle this switch to get detailed messages about program execution.'
                        )

    # sub-parser for tickers
    sub_parser = parser.add_subparsers(help='Ticker loader')
    ticker_parser = sub_parser.add_parser('tickers',
                                          help='Use this command to pass ticker input.'
                                          )
    ticker_parser.add_argument(
                                    '--list',
                                    '-l',
                                    type=int,
                                    nargs='+',
                                    help='Accepts multiple ticker IDs separated by whitespace.'
                              )
    ticker_parser.add_argument(
                                    '--file',
                                    '-f',
                                    type=File(),
                                    help='Accepts a file path that contains ticker IDs.'
                              )

    ticker_parser.add_argument(
                                    '--url',
                                    '-u',
                                    type=URL(),
                                    help='Accepts a URL to Google Sheets containing ticker IDs.'
                              )

    args = parser.parse_args()
    args.tickers = parse_tickers(args)
    return args


if __name__ == '__main__':
    user_args = parse_user_args()
    print(f'User Args: {user_args}')
