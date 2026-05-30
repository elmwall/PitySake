"""
Table viewer

Builds and manages:
- collecting pandas data for dataframe
- table for main or secondary object
"""

import logging

import streamlit as st

import app.data_access as hold


TERMS = st.session_state["TERMS"]
logger = logging.getLogger(__name__)


def table_view(component_key: str, object_type: str, 
               table_style: str, table_height: int | str):
    """
    Renders table feature for main or secondary object database.
    """

    logger.info(f"Running for {object_type}") 

    # Feature header
    tab_key = f"{component_key}_select_view"
    if st.session_state["header_switch"]:
        with st.container(key=f"{component_key}_head", width="stretch", height=26):
            _tab(tab_key, object_type)
    else:
        _tab(tab_key, object_type)

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
    elif object_type == "secondary":
        database = hold.load_secondary_database()
        
    # History tab container
    with st.container(
            border=False, key=f"{component_key}_holder_history", width="stretch", height=history_height):

        # Send for processing or collect cache for data and pandas dataframe
        rows = hold.process_collection_db(database, object_type)["table_data"]
        dataframe = hold.history_dataframe(rows, object_type)
        # Set dataframe style (should not be cached)
        styled_dataframe = (
            dataframe.style.set_properties(**{"background-color": table_style[1]})
            .set_properties(subset=["Name"], **{"width": "small"})
            .format(precision=0))
        
        # Generate table
        #   - In view: Date, # (number in collection), Name, "Event term", "Source term"
        #   - To the right of view (scroll sideways): origin, attribute, utility
        # This way the view is not cluttered, 
        # while they can still be shown through scroll
        # and can be used for searching/sorting
        st.dataframe(
            styled_dataframe, height="stretch", hide_index=True,
            column_config={
                "#": st.column_config.Column(width=40, alignment="center"),
                "Name": st.column_config.Column(width=150),
                TERMS["attempt"]: st.column_config.Column(width=50),
                TERMS["source"]: st.column_config.Column(width=140),},
            key=f"{component_key}_table_history", placeholder="")
        
    # Overview tab container
    with st.container(
            border=False, key=f"{component_key}_holder_overview", width="stretch", height=overview_height):

        # Send for processing or collect cache for data and pandas dataframe
        overview = hold.process_collection_db(database, object_type)["overview_data"]
        overview_dataframe = hold.overview_dataframe(overview)
        # Set dataframe style (should not be cached)
        styled_dataframe_overview = (
            overview_dataframe.style.set_properties(**{"background-color": table_style[1]})
            .set_properties(subset=["Name"], **{"width": "small"})
            .format(precision=0))
        # Generate table
        st.dataframe(
            styled_dataframe_overview, height="stretch", hide_index=True,
            column_config={
                "Name": st.column_config.Column(width=125),
                "Total": st.column_config.Column(width=45),
                TERMS["attempt"]: st.column_config.Column(width=50),},
            key=f"{component_key}_table_overview", placeholder="")


def _tab(key, object_type):
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
            padding: 0rem 0.1rem;
            margin: 0rem 1rem 0rem 0rem;
        }
        .st-key-KEY_REF button[data-testid='stBaseButton-segmented_control'] {
            border-bottom: 2px solid transparent;
        }
    </style>"""
    .replace("ELEMENT_REF", "button[data-testid='stBaseButton-segmented_control']")
    .replace("KEY_REF", key))
    view_options = {
        f"{object_type}_history": f"{TERMS[object_type]} history",
        f"{object_type}_overview": f"{TERMS[object_type]} overview"
    }
    options = list(view_options.keys())
    st.segmented_control(
        "Select view", options=options,
        format_func=lambda x:view_options[x], key=key, label_visibility="collapsed")