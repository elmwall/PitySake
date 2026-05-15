"""
Connector to project data

Manages:
- retrieves project settings
- setup config values in Streamlit session state
"""

import logging

import streamlit as st

from app.file_manager import Archivist


logger = logging.getLogger(__name__)


def initialize_constants(project: str):
    """
    Collect and initialize project settings

    Args:
        project (str):
            project file reference
    
    Actions:
    - collects settings dictionaries via file_manager Archivist
    - initializes configuration values in session state
    """

    logger.info("Running config_hub.initialize_constants")

    # Use case for Archivist for unique single path-file:
    # - setup None-values for irrelevant references
    # - join_path with project/settings and project-unique config.json
    arch = Archivist(
        DIRECTORIES={
            "DataFolder": None,
            "SettingsFolder": f"{project}/settings",
            "BackupFolder": None
        },
        DATAPATH={"backup_meta": None},
        file="config.json",
        initialized=False)
    config = arch.reader(join_path="settings")

    # Store config dictionaries in session state
    for dictionary, content in config.items():
        st.session_state[dictionary] = content