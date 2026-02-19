import logging
import sys
import time
from contextlib import contextmanager


def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(logging.Formatter(
            "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        ))
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger


@contextmanager
def timer(logger: logging.Logger, label: str):
    start = time.perf_counter()
    yield
    elapsed = time.perf_counter() - start
    logger.info(f"{label}: {elapsed:.3f}s")
