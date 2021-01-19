from argparse import ArgumentParser
from tws_equities.data_files import get_default_tickers
# from tws_equities.data_files import get_tickers_from_user_file
from tws_equities.parsers.input_parser._cli_config import CLI_CONFIG
from sys import stdout
# TODO: build uploader
# TODO: allow the user to provide an output location
# TODO: good to have: new data formats apart from CSV and JSON


def _add_positional_arguments(parser, config):
    if not(isinstance(parser, ArgumentParser)):
        raise TypeError(f'Expected "ArgumentParser" object, received {type(parser)}')
    for name, options in config.items():
        sub_parser = parser.add_subparsers(dest=name)
        _build_command(sub_parser, name=name, **options)


def _add_optional_arguments(parser, config):
    if not(isinstance(parser, ArgumentParser)):
        raise TypeError(f'Expected "ArgumentParser" object, received {type(parser)}')
    for _, options in config.items():
        name, flag = options['name'], options['flag']
        options = {k: v for (k, v) in options.items() if k not in ['name', 'flag']}
        parser.add_argument(name, flag, **options)


# noinspection PyShadowingBuiltins
def _build_command(sub_parser, name=None, help=None, description=None, positional_arguments=None,
                   optional_arguments=None):
    if sub_parser is None:
        raise TypeError(f'Expected "argparse._SubParserAction" object, received "None".')
    command = sub_parser.add_parser(name, help=help, description=description)
    if optional_arguments is not None:
        _add_optional_arguments(command, optional_arguments)
    if positional_arguments is not None:
        _add_positional_arguments(command, positional_arguments)


def parse_user_args(command_line=None):
    # root parser
    parser = ArgumentParser(prog='tws_equities',
                            description='A Python CLI built to download bar-data for Japanese Equities from '
                                        'TWS API.',
                            epilog='All optional arguments work like a toggle switch, user need not pass an '
                                   'explicit value to them.',
                            )

    parser.add_argument('--verbose', '-v', default=False, action='store_true',
                        help='Use this option to enable console logging, default behavior is to display '
                             'error messages only. Pair this option with "--debug / -d" option to view more '
                             'detailed messages.'
                        )
    parser.add_argument('--debug', '-d', default=False, action='store_true',
                        help='This option will not only enable console logging but would also start raising '
                             'hidden errors, specifically built for developers trying to debug a problem.')

    # add & build sub-parser for supported commands
    # refer to _COMMAND_CONFIG for available commands
    sub_praser = parser.add_subparsers(dest='command')
    for name, config in CLI_CONFIG.items():
        _build_command(sub_praser, name=name, **config)

    args = parser.parse_args(command_line)

    # user did not choose a command to run
    if args.command is None:
        stdout.write('User should specify which command to run, '
                     'please choose from the options given below.\n\n')
        parser.print_help()
        exit(0)

    # user did not specify tickers
    if hasattr(args, 'tickers') and args.tickers is None:
        stdout.write(f'User did not specify target tickers, loading from default input file.\n')
        args.tickers = get_default_tickers()[:500]  # TODO: remove it

    return vars(args)


if __name__ == '__main__':
    command_line = None
    parse_user_args(command_line=command_line)
