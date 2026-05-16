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

from app.project_configuration import initialize_constants
if "SETTINGS" not in st.session_state:
    project = os.path.splitext(
        os.path.basename(__file__))[0]
    initialize_constants(project)
    st.session_state["project"] = project
    import app.logger
    logger = logging.getLogger(__name__)
    logger.info(f"\n\n::::: {"PITYSAKE":^35} :::::")
    now = datetime.datetime.now()
    logger.info(f"New session: {now}")
else:
    import app.logger
    logger = logging.getLogger(__name__)
    logger.info("")
    now = datetime.datetime.now()
    logger.info(f"Rerun: {now}")

import app.initialize as init
import app.style as page
import app.constructor as construct




# Previous essential database/option changes resets system
if "processed_edits" in st.session_state:
    if st.session_state["processed_edits"]: 
        init.refresh()

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

st.json(st.session_state)




