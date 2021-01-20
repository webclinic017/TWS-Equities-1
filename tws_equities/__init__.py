"""
    ©2021 K2Q Capital Limited.
    All rights reserved.
"""


from tws_equities.parsers import parse_user_args
from tws_equities.controller import setup_logger
from tws_equities.controller import run
from tws_equities.controller import download
from tws_equities.controller import convert
from tws_equities.controller import metrics


__author__ = {'Mandeep Singh'}
__copyright__ = '© 2021 K2Q Capital Limited'
__license__ = 'MIT'

# version
__major__ = 1
__minor__ = 0
__micro__ = 0
__version__ = f'{__major__}.{__minor__}.{__micro__}'


COMMAND_MAP = {
                    'run': run,
                    'download': download,
                    'convert': convert,
                    'metrics': metrics
              }

__all__ = [
                'parse_user_args',
                'setup_logger',
                'run',
                'download',
                'convert',
                'metrics',
                'COMMAND_MAP'
          ]
