#!/usr/bin/env python3

"""
Append the schedule JSONL to schedule-matchkeys.jsonl file.

NOTE: Please use 'black' to re-format code.
"""

import argparse
from datetime import datetime, timezone
import json
import logging
import os
from pathlib import Path
import sys

SCRIPT_VERSION = "1.0.2"

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
        schedule = os.environ["SCHEDULE"]
    except KeyError:
        LOGGER.error("Missing env: SCHEDULE")
        options_okay = False
    try:
        job_id = os.environ["JOB_ID"]
    except KeyError:
        LOGGER.error("Missing env: JOB_ID")
        options_okay = False
    schedule_pn = PROG_PATH.parent.parent.parent.joinpath("js/schedule-matchkeys.jsonl")
    if not options_okay:
        sys.exit(2)
    return int(job_id), schedule, schedule_pn


def append_schedule(job_id, schedule, schedule_pn):
    """
    Composes the JSONL and appends to file.
    """
    json_packet = {}
    json_packet["id"] = job_id
    json_packet["scheduleDate"] = (
        datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    )
    json_packet["deployment"] = schedule
    with open(schedule_pn, mode="a", encoding="utf-8") as output_fh:
        output_fh.write(json.dumps(json_packet, sort_keys=False, indent=None))
        output_fh.write("\n")


def main():
    """
    Append the schedule JSONL to schedule-matchkeys.jsonl file.
    """
    job_id, schedule, schedule_pn = get_options()
    LOGGER.debug("schedule=%s schedule_pn=%s", schedule, schedule_pn)
    append_schedule(job_id, schedule, schedule_pn)


if __name__ == "__main__":
    sys.exit(main())
