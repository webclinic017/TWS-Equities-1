from time import time
from datetime import datetime as dt
from datetime import timedelta
from os.path import isdir
from os.path import join
from os.path import isfile
from os.path import sep
from os import listdir
from os import makedirs
from os import remove
from os import rmdir
import pandas as pd
from concurrent.futures import ThreadPoolExecutor
from functools import partial
import inspect
from json import dumps
from json import loads
from sys import stdout


def timer(function):
    """
        A generic decorator to track execution time of a function
        :param function: decorated function
        :return: decorated function's return value
    """
    def wrapper(*args, **kwargs):
        start = time()
        rv = function(*args, **kwargs)
        end = time()
        lapsed = round(end - start, 3)
        print(f'{"-"*10} Time Lapsed: {lapsed} seconds {"-"*10}')
        return rv
    return wrapper


def get_date_range(start, end):
    # stdout.write(f'=> Generating a valid date-range for data extraction...\n')
    date_format = r'%Y%m%d'
    start_date = dt.strptime(start, date_format)
    end_date = dt.strptime(end, date_format)
    if start_date > end_date:
        raise ValueError(f'Start date [{start_date.date()}] can not be greater than end date '
                         f'[{end_date.date()}]')
    date_range = []
    target_date = start_date
    days_inbetween = (end_date - start_date).days
    for i in range(days_inbetween + 1):  # +1 because we want to include end date as well
        date_range.append(target_date.date().strftime(date_format))
        target_date += timedelta(days=1)

    # stdout.write(f'\t-> Date Range [ Start: {start_date.date()} | End: {end_date.date()} ]\n')
    return date_range


def delete_file(target_directory, target_file):
    file_path = join(target_directory, target_file)
    if isfile(file_path):
        remove(file_path)


def clear_directory(target_location):
    for file_name in listdir(target_location):
        delete_file(target_location, file_name)


def delete_directory(target_directory):
    clear_directory(target_directory)
    if isdir(target_directory):
        rmdir(target_directory)


def make_dirs(target_location):
    """
        Create directory and sub-directories, if not present already.
        :param target_location: path to directory to be created
    """
    if not(isdir(target_location)):
        makedirs(target_location)


def run_with_concurrent_threads(function):
    """
        A generic decorator that provides multi-threaded behavior.
        :param function: decorated function
        :return: output of the decorated function in a list
    """
    def wrapper(*args, **kwargs):
        with ThreadPoolExecutor(max_workers=8) as e:
            rv = list(e.map(partial(function, **kwargs), *args))
        return rv
    return wrapper


def get_caller():
    """
        Return the name of the caller fucntion.
        # TODO: To be tested
    """
    return inspect.stack()[-1].function


def create_batches(items, batch_size=15):
    """
        Converts an interable into a list of smaller batches.
        :param items: iterable
        :param batch_size: size for each batch
        :return: list of bachtes
        # TODO: Turn it into a generator
    """
    # stdout.write(f'=> Batch creation initiated...\n')
    type_of_items = type(items)
    if type_of_items not in [list, set, tuple]:
        raise TypeError(f'Items must be an iterable, received: {type_of_items}')
    if isinstance(items, set):
        items = list(items)
    batches = []
    start, end, total = 0, batch_size, len(items)

    for i in range(start, total, batch_size):
        batches.append(items[start:end])
        start = end
        end += batch_size
    # stdout.write(f'\t-> Total Items: {total}\n')
    # stdout.write(f'\t-> Total Batches: {len(batches)}\n')
    # stdout.write(f'\t-> Batch Size: {batch_size}\n')
    return batches


def save_data_as_json(data, file_path, write_mode='w', sort_keys=True, indent=1):
    """
        Saves ticker data to a JSON file.
        :param data: python object containg data to be saved
        :param file_path: target file where data is to be saved
        :param write_mode: mode in which to write the file, choose from (w, w+)
        :param sort_keys: save data in sorted order
        :param indent: number of spaces by which data is to be indented
    """
    with open(file_path, write_mode) as f:
        f.writelines(dumps(data, sort_keys=sort_keys, indent=indent))


def read_json_file(file_path):
    """
        Reads a JSON file & loads data into a Python object.
        :param file_path: path to target file that contains JSON data
    """
    with open(file_path, 'r') as f:
        return loads(f.read())


def _get_file_extension(file_path):
    return file_path.split(sep)[-1].split('.')[-1]


def _validate_target_file(file_path, expected_file_type='csv'):
    """
        Validates that file is CSV and present on the given location.
        :param file_path: location of the data file
        :return: None
    """
    if not(isinstance(expected_file_type, str)):
        raise TypeError(f'Expected file type can not be: {expected_file_type}')
    file_type = _get_file_extension(file_path)
    if file_type != expected_file_type:
        raise TypeError(f'Data file must be {expected_file_type.upper()}, received: {file_type}')
    if not(isfile(file_path)):
        raise FileNotFoundError(f'File: {file_path} does not exist.')


def read_csv(file_path):
    _validate_target_file(file_path, expected_file_type='csv')
    return pd.read_csv(file_path)


if __name__ == '__main__':
    s = None
    e = '20210118'
    dr = get_date_range(s, e)
    print(dr)
