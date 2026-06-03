# pylint: disable=broad-exception-caught

"""
Logging and Telemetry Configuration Module.

Sets up global file-based rotation logging parameters and provides
auditing decorators to track standard method executions and failures.
"""

import logging
import functools

logging.basicConfig(level=logging.INFO,
                    filename="FindMeMovie.log",
                    format="%(asctime)s - %(levelname)s - %(filename)s - %(lineno)d - %(message)s",
                    encoding="utf-8")

logger = logging.getLogger(__name__)

def logger_decorator(func):
    """
    A decorator that logs the execution and potential errors of a function.

    Captures successful method executions and writes operational error states
    alongside call-stack traces directly into the master log file.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        """Internal wrapper around the decorated target executable."""
        try:
            res = func(*args, **kwargs)
            logger.info("%s executed.", func.__name__)
            return res
        except Exception as e:
            logger.error("Error in %s: %s", func.__name__, e, exc_info=True)
            raise e
    return wrapper
