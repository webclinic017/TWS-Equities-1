from ibapi.client import Contract


def create_stock(symbol, security_type='STK', exchange='SMART', currency='JPY'):
    contract = Contract()
    contract.symbol = symbol
    contract.secType = security_type
    contract.exchange = exchange
    contract.currency = currency
    return contract
