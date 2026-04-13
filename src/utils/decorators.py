import functools
import time
import logging

logger = logging.getLogger(__name__)

def timeit(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        end = time.perf_counter()
        logger.debug(f"{func.__name__} took {end - start:.4f}s")
        return result
    return wrapper

def log_execution(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        logger.info(f"Executing: {func.__name__}")
        return func(*args, **kwargs)
    return wrapper
