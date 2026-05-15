import logging

import pandas as pd
import streamlit as st

import app.data_access as hold


logger = logging.getLogger(__name__)
TERMS = st.session_state["TERMS"]


def table_view(component_key:str, 
               object_type:str, 
               table_style:str, 
               table_height:int|str):
    """
    Renders table feature for main or secondary object database

    Args:
        component_key (str):
            session state key for feature
        object_type (str):
            identifier for database
        table_style (str):
            styling settings
        table_height (int or str):
            int or str value for container height
    """

    logger.info(f"Running data_viewer.table_view for data: {object_type}")

    # Feature header
    if st.session_state["header_switch"]:
        with st.container(key=f"{component_key}_head", width="stretch", height="content"):
            st.markdown(f"##### *{TERMS[object_type]} history*", text_alignment="left")
    # Main container
    with st.container(
        border=False, 
        width="stretch", 
        height=table_height
    ):
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
            .set_properties(subset=[TERMS["attempt"]], **{"text-align": "right"})
            .format(precision=0))

        # Generate table
        st.dataframe(
            styled_dataframe,
            hide_index=True, 
            column_config={" ": st.column_config.Column(width=30, alignment="center")},
            height="stretch",
            key="table",
            placeholder="")
