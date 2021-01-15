from argparse import Action
from tws_equities.data_files import get_tickers_from_user_file

from tws_equities.data_files.input_data import PATH_TO_DEFAULT_TICKERS
from tws_equities.data_files.input_data import TEST_TICKERS


class _ListLoader(Action):

    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, self.dest, values)


class _FileLoader(Action):

    def __call__(self, parser, namespace, values, option_string=None):
        if values == 'default':
            values = PATH_TO_DEFAULT_TICKERS
        # TODO: find a better way for setting test tickers
        if values == 'test':
            tickers = TEST_TICKERS
        else:
            tickers = get_tickers_from_user_file(values)
        setattr(namespace, self.dest, tickers)


class _URLLoader(Action):

    def __call__(self, parser, namespace, values, option_string=None):
        # setattr(namespace, self.dest, values)
        raise NotImplementedError('Data load from a URL is not implemented yet.')


TICKER_ACTIONS = {
                    'list': _ListLoader,
                    'file': _FileLoader,
                    'url': _URLLoader
                 }
