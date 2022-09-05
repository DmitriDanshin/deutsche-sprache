import logging
import sys
from pathlib import Path
from settings import LOGGER_FORMAT, LOGGER_PATH


def setup_logger(name: str, log_file: Path, level=logging.DEBUG):
    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(
        logging.Formatter(fmt=LOGGER_FORMAT)
    )

    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(
        logging.Formatter(fmt=LOGGER_FORMAT)
    )

    logger_setup = logging.getLogger(name)
    logger_setup.setLevel(level)
    logger_setup.addHandler(file_handler)
    logger_setup.addHandler(stream_handler)

    return logger_setup


verbformen_logger = setup_logger('VERBFORMEN', Path(LOGGER_PATH) / Path("verbformen.log"))
