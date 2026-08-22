#!/usr/bin/env python3

# /// script
# requires-python = ">=3.13"
# dependencies = [
#   "jinja2",
# ]
# [tool.uv]
# exclude-newer = "7 days"
# ///

import argparse
import logging
from pathlib import Path
import pprint  # pylint: disable=unused-import
import sys

from jinja2 import Environment, FileSystemLoader

SCRIPT_VERSION = "1.0.0"

LOGLEVELS = {
    "debug": logging.DEBUG,
    "info": logging.INFO,
    "warning": logging.WARNING,
    "error": logging.ERROR,
    "critical": logging.CRITICAL,
}
PROG_NAME = Path(sys.argv[0]).name
PROG_PATH = Path(__file__).absolute().parent
PROG_DESC = __import__("__main__").__doc__
LOG_FORMAT = "%(levelname)s: %(message)s"
LOGGER = logging.getLogger(PROG_NAME)


def get_options():
    """
    Gets the command-line options.
    Verifies configuration.
    """
    parser = argparse.ArgumentParser(description=PROG_DESC)
    parser.add_argument(
        "-l",
        "--loglevel",
        choices=["debug", "info", "warning", "error", "critical"],
        help="Logging level. (Default: %(default)s)",
    )
    args = parser.parse_args()
    logging.basicConfig(format=LOG_FORMAT)
    if args.loglevel:
        loglevel = LOGLEVELS.get(args.loglevel.lower(), logging.NOTSET)
        LOGGER.setLevel(loglevel)
    LOGGER.info("Using script version: %s", SCRIPT_VERSION)

    
def main():
    """
    Test uv.
    """
    get_options()
    LOGGER.debug("Hello from uv")


if __name__ == "__main__":
    sys.exit(main())
