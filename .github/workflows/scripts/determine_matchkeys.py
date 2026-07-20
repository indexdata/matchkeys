#!/usr/bin/env python3

"""
Determine relevant matchkeys from the list of touched files.

NOTE: Please use 'black' to re-format code.
"""

import argparse
import logging
import os
import re
from pathlib import Path
import sys

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
    Gets the input options.
    Verifies configuration.
    """
    options_okay = True
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
    try:
        files_list = os.environ["FILES_LIST"]
    except KeyError:
        LOGGER.error("Missing env: FILES_LIST")
        options_okay = False
    if not options_okay:
        sys.exit(2)
    return files_list


def main():
    """
    Determine relevant matchkeys from the list of touched files.

    Returns:
        Space-delimited string of matchkey names.
    """
    files_list = get_options()
    LOGGER.debug("files_list=%s", files_list)
    matchkey_src_re = r"^js/matchkeys/([^/]+)/.+\.mjs$"
    test_src_re = r"^js/test/([^.]+)\.mjs$"
    test_assertion_re = r"js/test/assertions-([^\.]+)\.json$"
    # FIXME: also read their assertions JSON and detect if files changed
    matchkeys = set()
    for input_fn in files_list.split():
        match = re.search(matchkey_src_re, input_fn)
        if match:
            matchkeys.add(match.group(1))
        match = re.search(test_src_re, input_fn)
        if match:
            matchkeys.add(match.group(1))
        match = re.search(test_assertion_re, input_fn)
        if match:
            matchkeys.add(match.group(1))
    LOGGER.info("Determined %s matchkeys.", len(matchkeys))
    print(" ".join(matchkeys))


if __name__ == "__main__":
    sys.exit(main())
