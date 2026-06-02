import logging
import functools

logging.basicConfig(level=logging.INFO,
                    filename="FindMeMovie.log",
                    format="%(asctime)s - %(levelname)s - %(filename)s - %(lineno)d - %(message)s",
                    encoding="utf-8")

logger = logging.getLogger(__name__)

def logger_decorator(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            res = func(*args, **kwargs)
            logger.info(f'{func.__name__} executed.')
            return res
        except Exception as e:
            logger.error(e)
            raise e
    return wrapper

