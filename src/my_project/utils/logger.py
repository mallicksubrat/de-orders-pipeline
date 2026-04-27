import logging


def get_logger(name: str = "my_project", level: str = "INFO") -> logging.Logger:
    root_logger = logging.getLogger()
    if not root_logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(
            logging.Formatter("%(asctime)s | %(levelname)s | %(name)s | %(message)s")
        )
        root_logger.addHandler(handler)

    root_logger.setLevel(getattr(logging, level.upper(), logging.INFO))
    return logging.getLogger(name)
