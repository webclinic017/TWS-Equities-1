from ibapi.wrapper import EWrapper
from ibapi.client import EClient


class TWSWrapper(EWrapper):

    def __init__(self):
        EWrapper.__init__(self)


class TWSClient(EClient):

    def __init__(self, wrapper):
        EClient.__init__(self, wrapper)
