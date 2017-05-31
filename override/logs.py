import logging


def get_logger(name):
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(module)s.%(name)s: %(message)s')
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    console_log = logging.StreamHandler()
    console_log.setLevel(logging.INFO)
    console_log.setFormatter(formatter)
    logger.addHandler(console_log)
    return logger

logger = get_logger('override')
