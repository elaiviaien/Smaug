"""Module for setting up a logger with a file handler."""

import logging


def setup_logger(name: str) -> logging.Logger:
    """Set up a logger with a file handler."""
    logger = logging.getLogger(f"{name}_logger")
    # set all levels
    logger.setLevel(logging.DEBUG)
    if not logger.hasHandlers():
        handler = logging.FileHandler(f"{name}.log")
        handler.setLevel(logging.DEBUG)

        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        handler.setFormatter(formatter)

        logger.addHandler(handler)

    return logger


class LoggerWriter:
    """Class for redirecting stdout and stderr to the logger."""

    def __init__(self, logger):
        self.logger = logger

    def write(self, message):
        """Write a message to the logger."""
        if message.rstrip() != "":
            self.logger.log(self.logger.level, message.rstrip())

    def flush(self):
        """Flush the logger."""
        pass
