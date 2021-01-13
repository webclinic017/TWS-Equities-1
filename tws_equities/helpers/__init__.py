from tws_equities.helpers.logger_setup import get_logger
from tws_equities.helpers.contract_maker import create_stock
from tws_equities.helpers.utils import make_dirs


BAR_CONFIG = {
                'title': 'Status∶',
                'calibrate': 5,
                'force_tty': True,
                'spinner': 'dots_reverse',
                'bar': 'smooth'
             }
