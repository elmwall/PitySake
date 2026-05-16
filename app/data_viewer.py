"""
Table viewer

Builds and manages:
- collecting pandas data for dataframe
- table for main or secondary object
"""

import logging

import pandas as pd
import streamlit as st

import app.data_access as hold


TERMS = st.session_state["TERMS"]
logger = logging.getLogger(__name__)


def table_view(component_key: str, object_type: str, 
               table_style: str, table_height: int | str):
    """
    Renders table feature for main or secondary object database.
    """

    logger.info(f"Running data_viewer.table_view for data: {object_type}")

    # Feature header
    if st.session_state["header_switch"]:
        with st.container(key=f"{component_key}_head", width="stretch", height="content"):
            st.markdown(f"##### *{TERMS[object_type]} history*", text_alignment="left")
    # Main container
    with st.container(
            border=False, width="stretch", 
            height=table_height):
        # Collect relevant database
        if object_type == "main":
            database = hold.load_main_database()
        elif object_type == "secondary":
            database = hold.load_secondary_database()

        # Send for processing or collect cache for data and pandas dataframe
        rows = hold.process_collection_db(database, object_type)["table_data"]
        dataframe = hold.data_to_dataframe(rows, object_type)
        # Set dataframe style (should not be cached)
        styled_dataframe = (
            dataframe.style.set_properties(**{"background-color": table_style[1]})
            .set_properties(subset=["Name"], **{"width": "small"})
            .format(precision=0))

        # Generate table
        # Dimensions of columns giving:
        #   - In view: Date, # (number in collection), Name, "Event term", "Source term"
        #   - To the right of view: origin, attribute, utility
        # This way the view is not cluttered, 
        # while they can still be shown through scroll
        # and can be used for searching/sorting
        st.dataframe(
            styled_dataframe, hide_index=True, 
            column_config={
                "#": st.column_config.Column(width=40, alignment="center"),
                "Name": st.column_config.Column(width=150),
                TERMS["attempt"]: st.column_config.Column(width=50),
                TERMS["source"]: st.column_config.Column(width=140),},
            height="stretch", key="table", placeholder="")
