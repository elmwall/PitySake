"""
## PitySake main module

- Connects individual project databases to app structure
- Directs cache, state keys and UI style settings functions
- Call function for building features

Streamlit session state maintains keys and values accross feature files 
this allows for interactive UI responses.  

Larger sets of data and options are kept in cache.

To avoid hickups in states and interface not updating:
- Bool for previous changes in data is checked in main
- If true, forces a clean slate before re-building the app.
"""

import logging
import os
import datetime

import streamlit as st
# Initiate logger here makes configurations available accross modules
logger = logging.getLogger(__name__)
import app.logger as log
# Project initiation 
# File name of project main is key to project folder --> configuration and data 
from app.project_configuration import initialize_constants
project = os.path.splitext(os.path.basename(__file__))[0]
project_info = initialize_constants(project)
st.session_state["project"] = project
format_line = f"{"DATE":24}{"LEVEL":8}{"LINE "}{"MODULE":21}{"FUNCTION":22}ACTION"
if "initated" not in st.session_state:
    logger.info(f"\n\n{":"*100}\n{f"PITYSAKE: {project}":^100}\n{":"*100}\n{format_line}")
    now = datetime.datetime.now()
    logger.info(f"New session: {now}")
else:
    logger.info(f"\n{"."*100}\n{f"RERUN {project}":^100}\n{"."*100}\n{format_line}")
import app.initialize as init
import app.style as page
import app.constructor as construct


# Previous essential database/option changes resets system
if "processed_edits" in st.session_state:
    processed_edits = st.session_state["processed_edits"]
    if processed_edits: 
        clear_options = processed_edits.get("clear_options", True)
        clear_main = processed_edits.get("clear_main", True)
        clear_secondary = processed_edits.get("clear_secondary", True)
        clear_progress = processed_edits.get("clear_progress", True)
        logger.info("Edits declared")
        init.refresh(clear_options, clear_main, clear_secondary, clear_progress)

# Initialize keys and chache databases
init.initialize()

# Set settings and retrieve keys for connecting features to styling
feature_keys, progress_calc_keys = page.settings()
registration_keys, prog_meter_keys, highlight_html, table_style = page.style(feature_keys, progress_calc_keys)

# Build
construct.header()
if st.session_state["cleared_cache"]:
    # Refresh databases to get updated conditions in data environment
    init.fetch_databases()
elif not st.session_state["vertical_view"]:
    construct.horizontal_view(registration_keys, prog_meter_keys, highlight_html, table_style)
elif st.session_state["vertical_view"]:
    construct.vertical_view(registration_keys, prog_meter_keys, highlight_html, table_style)

logger.info(f"System complete.")
st.session_state["initated"] = True
# st.json(st.session_state)