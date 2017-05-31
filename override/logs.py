import logging


def get_logger(name):
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(module)s.%(name)s: %(message)s')
    logging_instance = logging.getLogger(name)
    logging_instance.setLevel(logging.INFO)
    console_log = logging.StreamHandler()
    console_log.setLevel(logging.INFO)
    console_log.setFormatter(formatter)
    logging_instance.addHandler(console_log)
    return logging_instance

logger = get_logger('override')
