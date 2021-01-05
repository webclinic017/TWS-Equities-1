from time import time
from os.path import isdir
from os import makedirs
from concurrent.futures import ThreadPoolExecutor
from functools import partial


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
    if not(isdir(target_location)):
        makedirs(target_location)


def run_with_concurrent_threads(function):
    def wrapper(*args, **kwargs):
        with ThreadPoolExecutor(max_workers=8) as e:
            rv = list(e.map(partial(function, **kwargs), *args))
        return rv
    return wrapper


if __name__ == '__main__':
    pass
