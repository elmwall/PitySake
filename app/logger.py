"""
Logging

Generates log files per project for debugging.  
Renders feature for user notification for non-critical errors.
"""

import logging
from pathlib import Path

import streamlit as st


def notify():
    """
    User notification of error.
    """
    error = st.session_state["error"]
    info = str()
    if error:
        if error["stage"]: info += f"Stage: {error["stage"]}:  \n"
        if error["name"]: info += f"Name: {error["name"]}  \n"
        if error["file"]: info += f"File: {error["file"]}  \n"
        if error["info_list"]:
            for x in error["info_list"]:
                info += f"- {x}  "

    col_1, col_2, col_3, col_4 = st.columns([2, 6, 6, 1.5])
    with col_1.container(border=True, width="stretch"):
        st.markdown("**:red[Error!]**", text_alignment="center")
    col_2.error(error["message"])
    with col_3.expander("Details"):
        st.markdown(info)

    if col_4.button("Ok", width="stretch"): 
        st.session_state["error"] = False
        st.rerun()


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
            "format": "%(asctime)s %(levelname)s | %(lineno)-3d %(module)-20s .%(funcName)-20s %(message)s"
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
            "maxBytes": 400000,
            "backupCount": 5
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