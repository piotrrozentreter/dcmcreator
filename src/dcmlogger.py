import logging
import sys

LOGGER_NAME = "dcmcreator"

def setup_logging():
    """Configure application-wide logger to print WARNING+ to stderr and a log file.

    Returns the configured logger instance. If already configured, returns existing one.
    """
    logger = logging.getLogger(LOGGER_NAME)
    if logger.handlers:
        return logger
    logger.setLevel(logging.WARNING)
    fmt = logging.Formatter('%(asctime)s [%(levelname)s] %(name)s: %(message)s')

    # Console handler (stderr)
    sh = logging.StreamHandler(sys.stderr)
    sh.setLevel(logging.WARNING)
    sh.setFormatter(fmt)
    logger.addHandler(sh)

    # File handler (best-effort)
    try:
        fh = logging.FileHandler('dcmcreator.log', encoding='utf-8')
        fh.setLevel(logging.WARNING)
        fh.setFormatter(fmt)
        logger.addHandler(fh)
    except Exception:
        # If file handler cannot be created, continue with console logging only
        pass

    # Route Python warnings to logging
    logging.captureWarnings(True)
    return logger
