"""
Table viewer

Builds and manages:
- collecting pandas data for dataframe
- table for main or secondary object
"""

import logging

import streamlit as st

from app.initialize import TERMS
import app.data_access as hold


logger = logging.getLogger(__name__)


def table_view(component_key: str, object_type: str, 
               table_style: str, table_height: int | str):
    """
    Renders table feature for main or secondary object database, with tabs 
    for history or overview.
    """
    logger.info(f"Running for {object_type}") 

    # Feature header
    tab_key = f"{component_key}_select_view"
    if st.session_state["header_switch"]:
        with st.container(key=f"{component_key}_head", width="stretch", height=26):
            _tab(tab_key, object_type)
    else:
        _tab(tab_key, object_type)

    # Tab 
    # - Generated with st.segmented_control instead of st.tabs # due to limitations in customization, 
    #   with the tab field taking up too much space. 
    # - There is also an issue with jumping stretch layout when loading table data
    #   upon switching tabs, generating a tall view when loading data and then limiting it to stretch. 
    #   Instead both "tabs" and there tables are generated, but stacked on top of each other,
    #   the tab not shown is set to 1 pixel height. Switching can then adapt the stretch to already existing data.
    if st.session_state[f"{component_key}_select_view"] == f"{object_type}_history":
        st.space(1)
        history_height = "stretch"
        overview_height = 1
    else:
        history_height = 1
        overview_height = "stretch"

    # Collect relevant database
    if object_type == "main":
        database = hold.load_main_database()
        processed_database = hold.process_main_db(database)
        rows = processed_database["table_data"]
        overview = hold.process_main_db(database)["overview_data"]
    elif object_type == "secondary":
        database = hold.load_secondary_database()
        processed_database = hold.process_secondary_db(database)
        rows = processed_database["table_data"]
        overview = hold.process_secondary_db(database)["overview_data"]

    # History tab container
    with st.container(
            border=False, key=f"{component_key}_holder_history", width="stretch", height=history_height):
        
        if not processed_database["valid"]:
            st.error("Critical option data missing.")
            return

        # Send for processing or collect cache for data and pandas dataframe
        dataframe = hold.history_dataframe(rows, object_type)
        # Set dataframe style (should not be cached)
        style = table_style[1] if table_style else ""
        styled_dataframe = (
            dataframe.style.set_properties(**{"background-color": style})
            .set_properties(subset=["Name"], **{"width": "small"})
            .format(precision=0))
        
        # Generate table
        # Columns not fitting in view can be shown through scroll
        st.dataframe(
            styled_dataframe, height=table_height, hide_index=True,
            key=f"{component_key}_table_history", placeholder="")
    
    # Overview tab container
    with st.container(
            border=False, key=f"{component_key}_holder_overview", width="stretch", height=overview_height):
        # Send for processing or collect cache for data and pandas dataframe
        overview_dataframe = hold.overview_dataframe(overview)
        # Set dataframe style (should not be cached)
        styled_dataframe_overview = (
            overview_dataframe.style.set_properties(**{"background-color": style})
            .set_properties(subset=["Name"], **{"width": "small"})
            .format(precision=0))
        # Generate table
        st.dataframe(
            styled_dataframe_overview, height=table_height, hide_index=True,
            key=f"{component_key}_table_overview", placeholder="")


def _tab(key: str, object_type: str):
    "Generates tab view control via Streamlit segmented control element."
    st.html("""
    <style>
        .st-key-KEY_REF button[data-testid='stBaseButton-segmented_control'], 
        .st-key-KEY_REF button[data-testid='stBaseButton-segmented_controlActive'] {
            border-bottom-left-radius: 0px;
            border-bottom-right-radius: 0px;
            border-bottom: 2px solid;
            border-top: none; 
            border-left: none; 
            border-right: none; 
            min-height: 24px;
            height: 24px;
            padding: 0px 1.6px;
            margin: 0px 16px 0px 0px;
        }
        .st-key-KEY_REF button[data-testid='stBaseButton-segmented_control'] {
            border-bottom: 2px solid transparent;
        }
    </style>"""
    .replace("ELEMENT_REF", "button[data-testid='stBaseButton-segmented_control']")
    .replace("KEY_REF", key))

    # Tab titles
    view_options = {
        f"{object_type}_history": f"{TERMS[object_type]} history",
        f"{object_type}_overview": f"{TERMS[object_type]} overview"
    }
    st.segmented_control(
        "Select view", options=list(view_options.keys()),
        format_func=lambda x:view_options[x], key=key, label_visibility="collapsed")