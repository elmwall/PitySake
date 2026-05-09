import streamlit as st

import app.ui_style as page
import app.initialize as init
import app.constructor as construct
from settings.config import TERMS, DIRECTORIES, DATAPATH



if "processed_edits" in st.session_state:
    if st.session_state["processed_edits"]: 
        init.refresh()

# Set directory and file
init.initialize()

# Set page style and settings
feature_keys, progress_calc_keys = page.settings()
registration_keys, prog_meter_keys, highlight_html, table_style = page.style(feature_keys, progress_calc_keys)


construct.border()
if st.session_state["cleared_cache"]:
    init.fetch_database()
elif not st.session_state["vertical_view"]:
    construct.horizontal_view(registration_keys, prog_meter_keys, highlight_html, table_style)
elif st.session_state["vertical_view"]:
    construct.vertical_view(registration_keys, prog_meter_keys, highlight_html, table_style)

