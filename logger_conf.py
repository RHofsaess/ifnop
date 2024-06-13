import logging
import sys
from datetime import datetime
from typing import Optional


class CustomFormatter(logging.Formatter):
    """Custom formatter to change format based on log level."""
    def __init__(self, fmt: str = "> %(message)s"):
        super().__init__(fmt=fmt)
        self.default_formatter = logging.Formatter(fmt)
        self.debug_formatter = logging.Formatter("%(asctime)s - [%(levelname)s] - %(message)s")
        self.warning_formatter = logging.Formatter("[%(levelname)s] - %(message)s")

    def format(self, record: logging.LogRecord) -> str:
        # Apply the debug formatter if the level is DEBUG
        if record.levelno == logging.DEBUG:
            return self.debug_formatter.format(record)
        elif record.levelno == logging.WARNING:
            return self.warning_formatter.format(record)
        # Use the default formatter for all other levels
        else:
            return self.default_formatter.format(record)


def configure_logger(name: str = 'DefaultLogger', level: int = logging.WARNING,
                     logtofile: str = None) -> logging.Logger:
    """
    Logger configuration function.
    The loglevels are:\n
        DEBUG(10): All stuff is dumped (spammy!)\n
        INFO(20): Default output\n
        WARNING(30): Only warnings.\n
    Parameters
    ----------
    name: str
    level: int
    logtofile: str

    Returns
    -------
    Logger
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    custom_formatter = CustomFormatter()

    if logtofile is not None:  # if not None but empty
        if len(logtofile) > 0:
            filename = logtofile
        else:  # use default with timestamp
            # Format current datetime as a string
            current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            # Append the formatted datetime to the log file name
            filename = f'network_info_{current_time}.log'
        print(f'Logging to {filename} enabled.')
        file_handler = logging.FileHandler(filename)
        file_handler.setFormatter(custom_formatter)
        logger.addHandler(file_handler)
    else:  # log to stdout
        stream_handler = logging.StreamHandler(sys.stdout)
        stream_handler.setFormatter(custom_formatter)
        logger.addHandler(stream_handler)

    return logger
