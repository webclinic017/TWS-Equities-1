#! TWS-Project/venv/bin/python3.9


from tws_equities import parse_user_args
from tws_equities import setup_logger
from tws_equities import COMMAND_MAP
# from json import dumps
import sys

# load user input
user_args = parse_user_args()

# extract command and remove the key
# command is only to be used at the top-level
# we won't need it for subsequent calls
command = user_args['command']
del user_args['command']

# setup root logger
verbose, debug = user_args['verbose'], user_args['debug']
logger = setup_logger(__name__, verbose=verbose, debug=debug)


def main():
    try:
        target_function = COMMAND_MAP[command]
        target_function(**user_args)
    except KeyboardInterrupt as e:
        _message = 'Detected keyboard interruption from the user, terminating program....'
        sys.stderr.write(f'{_message}\n')
        logger.error(_message)
    except Exception as e:
        _message = f'Program Crashed: {e}'
        sys.stderr.write(f'{_message}\n')
        logger.critical(_message, exc_info=True)
        if debug:
            raise e
    sys.stderr.flush()
    sys.stdout.flush()


if __name__ == '__main__':
    main()
