import logging
import sys

from extract_zipped_email_attachments.settings import config


def build_logger(log_level, log_file_location=None):
    log_format = '[%(asctime)s] [%(levelname)s] (%(process)d) %(module)s: %(message)s'
    log_level_translations = {'DEBUG': 10,
                              'INFO': 20,
                              'WARNING': 30,
                              'ERROR': 40,
                              'CRITICAL': 50}

    if not isinstance(log_level, int):
        log_level = log_level_translations[log_level.upper()]

    if not isinstance(log_level, int) and log_level in log_level_translations.values():
        raise TypeError('log_level defined incorrectly')

    logging.basicConfig(stream=sys.stdout, level=log_level, format=log_format)

    logger = logging.getLogger(__name__)

    if log_file_location:
        fh = logging.FileHandler(log_file_location)
        fh.setLevel(log_level)
        fh.setFormatter(logging.Formatter(log_format))
        logger.addHandler(fh)

    return logger

log = build_logger(log_level=config['log_level'])
