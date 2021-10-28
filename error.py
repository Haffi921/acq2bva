import logging
import sys


def true_or_exit(test: bool, msg: str):
    if not test:
        logging.info(msg)
        sys.exit(0)


def true_or_fail(test: bool, msg: str):
    if not test:
        logging.error(msg)
        sys.exit(1)
