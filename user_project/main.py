"""
App main module
- 
- Direct cache and state key initialization
- Call modules for page setting and themes
- Call function for building features in horizontal/vertical layout

Streamlit session state maintains keys and values available across features.
The larger sets of data and options are kept in cache.

To avoid hickups in states and interface not updating, foundational changes in data forces a clean slate.
In a clean slate, essential values are initialized before building the features. 
"""

import sys
import os

import streamlit as st

current_project_dir = os.path.dirname(os.path.abspath(__file__))
root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, current_project_dir)
sys.path.insert(1, root_path)

from app import config_hub
import settings.config as project_config
config_hub.DIRECTORIES = project_config.DIRECTORIES
config_hub.SETTINGS = project_config.SETTINGS
config_hub.DATAPATH = project_config.DATAPATH
config_hub.TERMS = project_config.TERMS
import app.ui_style as page
import app.initialize as init
import app.constructor as construct


if "processed_edits" in st.session_state:
    if st.session_state["processed_edits"]: 
        init.refresh()

# Initialize keys and chache databases
init.initialize()

# Set settings and retrieve keys for connecting features to styling
feature_keys, progress_calc_keys = page.settings()
registration_keys, prog_meter_keys, highlight_html, table_style = page.style(feature_keys, progress_calc_keys)

# Build
construct.border()
if st.session_state["cleared_cache"]:
    init.fetch_databases()
elif not st.session_state["vertical_view"]:
    construct.horizontal_view(registration_keys, prog_meter_keys, highlight_html, table_style)
elif st.session_state["vertical_view"]:
    construct.vertical_view(registration_keys, prog_meter_keys, highlight_html, table_style)





