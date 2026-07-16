import logging
import os

from logging.handlers import RotatingFileHandler


def setup_logger(log_file, level="INFO"):

    directory = os.path.dirname(log_file)

    if directory:
        os.makedirs(directory, exist_ok=True)


    logger = logging.getLogger("OHMeshBridge")


    if logger.hasHandlers():
        return logger


    logger.setLevel(
        getattr(logging, level.upper(), logging.INFO)
    )


    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(message)s",
        "%Y-%m-%d %H:%M:%S"
    )


    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=5 * 1024 * 1024,
        backupCount=10,
        encoding="utf-8"
    )

    file_handler.setFormatter(formatter)


    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)


    logger.addHandler(file_handler)
    logger.addHandler(console_handler)


    return logger

def setup_audit_logger(log_file):

    import logging

    audit_logger = logging.getLogger("OHMeshBridgeAudit")

    if audit_logger.hasHandlers():
        return audit_logger


    handler = RotatingFileHandler(
        log_file,
        maxBytes=5 * 1024 * 1024,
        backupCount=10,
        encoding="utf-8"
    )


    formatter = logging.Formatter(
        "%(asctime)s | %(message)s",
        "%Y-%m-%d %H:%M:%S"
    )


    handler.setFormatter(formatter)

    audit_logger.addHandler(handler)
    audit_logger.setLevel(logging.INFO)

    return audit_logger