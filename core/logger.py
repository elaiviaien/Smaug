import logging


def get_file_handler(name: str) -> logging.FileHandler:
    handler = logging.FileHandler(f"logs/{name}.log")
    handler.setLevel(logging.DEBUG)

    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    handler.setFormatter(formatter)

    return handler


def get_stream_handler() -> logging.StreamHandler:
    handler = logging.StreamHandler()
    handler.setLevel(logging.DEBUG)

    formatter = logging.Formatter("%(levelname)s - %(message)s")
    handler.setFormatter(formatter)

    return handler


def setup_logger(
    name: str, file_handler: bool = True, stream_handler: bool = True
) -> logging.Logger:
    logger = logging.getLogger(f"{name}_logger")
    # set all levels
    logger.setLevel(logging.DEBUG)
    if not logger.hasHandlers():
        if file_handler:
            file_handler = get_file_handler(name)
            logger.addHandler(file_handler)
        if stream_handler:
            stream_handler = get_stream_handler()
            logger.addHandler(stream_handler)

    return logger


class LoggerWriter:

    def __init__(self, logger: logging.Logger, level: int = logging.INFO):
        self.logger = logger
        self.level = level

    def write(self, message):
        if message.rstrip() != "":
            self.logger.log(self.level, message.rstrip())

    def flush(self):
        for handler in self.logger.handlers:
            handler.flush()
