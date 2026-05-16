"""
Logging

Generates log files per project for debugging.
"""

import logging
from pathlib import Path

import streamlit as st


# Set log path/file
log_directory = Path("logs")
log_directory.mkdir(exist_ok=True)
project = st.session_state["project"]
logger = logging.getLogger(project)
# Set level of logging - silence irrelevant messages
logging.getLogger("PIL").setLevel(logging.WARNING)
logging.getLogger("streamlit").setLevel(logging.WARNING)

logging_config = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "simple": {
            "format": "%(levelname)s: %(message)s"
        }
    },
    "handlers": {
        "stderr": {
            "class": "logging.StreamHandler",
            "level": "WARNING",
            "formatter": "simple",
            "stream": "ext://sys.stderr"
        },
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "DEBUG",
            "formatter": "simple",
            "filename": f"logs/{project}.log",
            "maxBytes": 10000,
            "backupCount": 6
        }
    },
    "loggers": {
        "root": {
            "level": "DEBUG",
            "handlers": [
                "stderr",
                "file"
            ]
        }
    }
}

logging.config.dictConfig(config=logging_config)
# logger.debug("debug message")
# logger.info("info message")
# logger.warning("warning message")
# logger.error("error message")
# logger.critical("critical message")