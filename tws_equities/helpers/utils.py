from time import time
from os.path import isdir
from os import makedirs
from concurrent.futures import ThreadPoolExecutor
from functools import partial
import inspect


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


def create_batches(items, batch_size=25):
    """
        Converts an interable into a list of smaller batches.
        :param items: iterable
        :param batch_size: size for each batch
        :return: list of bachtes
        # TODO: Turn it into a generator
    """
    batches = []
    start, end = 0, batch_size
    for i in range(start, len(items), batch_size):
        batches.append(items[start:end])
        start = end
        end += batch_size
    return batches
