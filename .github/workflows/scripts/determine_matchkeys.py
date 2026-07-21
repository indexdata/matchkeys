#!/usr/bin/env python3

"""
Determine relevant matchkeys from the list of touched files.

NOTE: Please use 'black' to re-format code.
"""

import argparse
import json
import logging
import os
from pathlib import Path
import re
import sys

SCRIPT_VERSION = "1.1.0"

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


def collate_assertions_test_records(input_fn):
    """
    Reads a JSON assertions file and collates the records filenames.
    """
    assertion_records = []
    with open(input_fn, mode="r", encoding="utf-8") as json_fh:
        try:
            content = json.load(json_fh)
        except json.decoder.JSONDecodeError as err:
            msg = f"Trouble loading assertions file: {err.lineno} {err.msg}"
            LOGGER.error(msg)
            raise
    for record_fn in content.keys():
        assertion_records.append(record_fn)
    return assertion_records


def gather_matchkeys_test_records():
    """
    Inspects each assertions file
    and composes list of record files for each matchkey.
    """
    assertion_re = r"assertions-([^\.]+)\.json$"
    matchkeys_records = {}
    dir_test = Path("test")
    files_assertions = list(dir_test.glob("assertions*.json"))
    for input_fn in files_assertions:
        match = re.search(assertion_re, input_fn.name)
        if match:
            assertion = match.group(1)
            # Handle some special files.
            if assertion == "deepdish-goldrush2024":
                assertion = "deepdish"
            try:
                matchkeys_records[assertion]
            except KeyError:
                matchkeys_records[assertion] = set([])
            assertion_records = collate_assertions_test_records(input_fn)
            for record_fn in assertion_records:
                matchkeys_records[assertion].add(f"js/{record_fn}")
    return matchkeys_records


def detect_matchkey_for_record(matchkeys_records, record_fn):
    """
    Detect matchkeys that utilise this record file.
    """
    matchkeys = []
    for matchkey in matchkeys_records.keys():
        if record_fn in matchkeys_records[matchkey]:
            matchkeys.append(matchkey)
    return matchkeys


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
    matchkeys_records = gather_matchkeys_test_records()
    # pprint.pprint(matchkeys_records)
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
        # Handle some special files:
        if input_fn == "js/test/assertions-deepdish-goldrush2024.json":
            matchkeys.add("deepdish")
            matchkeys.discard("deepdish-goldrush2024")
        # Detect changed related assertions records.
        for matchkey in detect_matchkey_for_record(matchkeys_records, input_fn):
            matchkeys.add(matchkey)

    LOGGER.info("Determined %s matchkeys.", len(matchkeys))
    print(" ".join(matchkeys))


if __name__ == "__main__":
    sys.exit(main())
