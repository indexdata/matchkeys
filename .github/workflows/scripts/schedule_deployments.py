#!/usr/bin/env python3

"""
Append the schedule JSONL to schedule-deployments.jsonl file.

NOTE: Please use 'black' to re-format code.
"""

# /// script
# requires-python = ">=3.13"
# dependencies = [
#   "jinja2",
# ]
# [tool.uv]
# exclude-newer = "7 days"
# ///

import argparse
from datetime import datetime, timezone
import json
import logging
import os
from pathlib import Path
import pprint  # pylint: disable=unused-import
import sys

from jinja2 import Environment, FileSystemLoader

SCRIPT_VERSION = "1.5.0"

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
        action = os.environ["ACTION"]
    except KeyError:
        LOGGER.error("Missing env: ACTION")
        options_okay = False
    try:
        schedule = os.environ["SCHEDULE"]
    except KeyError:
        LOGGER.error("Missing env: SCHEDULE")
        options_okay = False
    try:
        dir_output = os.environ["DIR_OUTPUT"]
    except KeyError:
        LOGGER.error("Missing env: DIR_OUTPUT")
        options_okay = False
    try:
        job_id = os.environ["JOB_ID"]
    except KeyError:
        LOGGER.error("Missing env: JOB_ID")
        options_okay = False
    templates_pn = PROG_PATH.joinpath("templates")
    if not templates_pn.exists():
        LOGGER.error("The jinja templates '%s' not found.", templates_pn)
        options_okay = False
    schedule_pn = PROG_PATH.parent.parent.parent.joinpath(
        dir_output, "schedule-deployments.jsonl"
    )
    if not options_okay:
        sys.exit(2)
    return int(job_id), action, schedule, templates_pn, schedule_pn


def append_schedule(job_id, action, id_pool, schedule_pn):
    """
    Composes the JSONL and appends to file.
    """
    json_packet = {}
    json_packet["id"] = job_id
    json_packet["scheduleDate"] = (
        datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    )
    json_packet["action"] = action
    json_packet["initialized"] = False
    json_packet["poolId"] = id_pool
    with open(schedule_pn, mode="a", encoding="utf-8") as output_fh:
        output_fh.write(json.dumps(json_packet, sort_keys=False, indent=None))
        output_fh.write("\n")


def main():
    """
    Append the schedule JSONL to schedule-deployments.jsonl file.
    """
    job_id, action, schedule, templates_pn, schedule_pn = get_options()
    # LOGGER.debug("schedule=%s schedule_pn=%s", schedule, schedule_pn)
    deployments = schedule.split(",")
    matchers = []
    id_pool = ""
    for deployment in deployments:
        matcher, sha = deployment.split(":")
        id_matcher = f"{matcher}~{sha[0:7]}"
        matchers.append(id_matcher)
    id_pool = "_".join(matchers)
    append_schedule(job_id, action, id_pool, schedule_pn)
    env_jinja = Environment(loader=FileSystemLoader(templates_pn))
    template_cr = env_jinja.get_template("cr.yaml.jinja")
    content_cr = template_cr.render(
        mytext="FooBar",
    )
    pprint.pprint(content_cr)


if __name__ == "__main__":
    sys.exit(main())
