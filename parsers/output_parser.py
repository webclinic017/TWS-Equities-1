import pandas as pd
from helpers import make_dirs
from os.path import join


def filter_historical_data(data):
    """
        Filters historical data into two dictionaries: success & failure.
        Removes meta_data from each data object.
        :param data: historical_data extracted from TWS API
        :return: success & failure data
    """
    success = dict(filter(lambda x: data[x[0]]['meta_data']['status'], data.items()))
    failure = dict(filter(lambda x: not (data[x[0]]['meta_data']['status']), data.items()))
    return success, failure


def parse_success_data_into_a_dataframe(data):
    """
        Generates a dataframe with bar dara from for each ticker.
        :param data: dictionary containing ticker wise data
        :return: dataframe containing bar data for all the tickers
    """
    # create a placeholder dataframe
    expected_columns = ['time_stamp', 'ecode', 'session', 'open', 'high',
                        'low', 'close', 'volume', 'count', 'average']
    data_frame = pd.DataFrame(columns=expected_columns)

    print(f'Generating dataframe for success data...')
    tickers = list(data.keys())
    total_tickers = len(tickers)
    # update placeholder by generating ticker-wise dataframe
    for i in range(total_tickers):
        ticker = tickers[i]
        bar_data = data[ticker]['bar_data']
        temp = pd.DataFrame(bar_data)
        temp['ecode'] = ticker
        data_frame = data_frame.append(temp)
        print(f'{"-"*10} Generated dataframe for: {i+1} / {total_tickers} tickers', end='\r')

    return data_frame


def parse_failure_data_into_a_dataframe(data):
    """
            Generates a dataframe with bar dara from for each ticker.
            :param data: dictionary containing ticker wise data
            :return: dataframe containing bar data for all the tickers
    """
    # create a placeholder dataframe
    expected_columns = ['ecode', 'status', 'attempt', 'code', 'message']
    data_frame = pd.DataFrame(columns=expected_columns)

    print(f'Generating dataframe for failure data...')
    tickers = list(data.keys())
    total_tickers = len(tickers)
    # update placeholder by generating ticker-wise dataframe
    for i in range(total_tickers):
        ticker = tickers[i]
        meta_data = data[ticker]['meta_data']
        error_stack, status, attempt = meta_data['_error_stack'], meta_data['status'], meta_data['attempt']
        temp = pd.DataFrame(error_stack)
        temp['ecode'], temp['status'], temp['attempt'] = ticker, status,  attempt
        data_frame = data_frame.append(temp)
        print(f'{"-"*10} Generated dataframe for: {i+1} / {total_tickers} tickers', end='\r')

    return data_frame


def save_to_csv(data, target_location):
    """
        To be added...
        @param data:
        @param target_location:
    """
    make_dirs(target_location)
    success_data, failure_data = filter_historical_data(data)
    print(f'Successfully extracted data for: {len(success_data)} / {len(data)} tickers')
    print(f'Failed to extract data for: {len(failure_data)} / {len(data)} tickers')
    if bool(success_data):
        success = parse_success_data_into_a_dataframe(success_data)
        print('Dataframe generation completed for success data, dumping data to CSV file!')
        success.to_csv(join(target_location, 'success.csv'))
    if bool(failure_data):
        failure = parse_failure_data_into_a_dataframe(failure_data)
        print('Dataframe generation completed for failure data, dumping data to CSV file!')
        failure.to_csv(join(target_location, 'failure.csv'))
