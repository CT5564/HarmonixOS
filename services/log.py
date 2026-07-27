# Logging
#
# Central logging setup. Every module gets a child logger
# under the "harmonix" namespace.
#
# Usage:
#   from services.log import get_log
#   log = get_log(__name__)
#   log.info("message")
#   log.error("something broke", exc_info=True)

import logging
import sys
from datetime import datetime


_FORMAT = "%(asctime)s [%(levelname)-8s] %(name)s — %(message)s"
_DATEFMT = "%H:%M:%S"


def setup(
    level: int = logging.DEBUG,
    stream: object | None = None
) -> None:
    """Configure root Harmonix logger. Call once at startup."""

    root = logging.getLogger("harmonix")
    root.setLevel(level)

    if root.handlers:
        return

    handler = logging.StreamHandler(
        stream or sys.stdout
    )
    handler.setLevel(level)

    formatter = logging.Formatter(
        _FORMAT,
        datefmt=_DATEFMT
    )
    handler.setFormatter(formatter)

    root.addHandler(handler)


def get_log(name: str) -> logging.Logger:
    """
    Get a logger for a module.

    Pass __name__ to get a child logger:
        log = get_log(__name__)
    """

    # Strip leading "harmonix." if caller already in package
    # so "harmonix.services.sync" doesn't become
    # "harmonix.harmonix.services.sync"
    if name.startswith("harmonix."):
        key = name
    else:
        key = f"harmonix.{name}"

    return logging.getLogger(key)
