import streamlit as st
import pandas as pd

import app.data_access as hold

from app.config_hub import TERMS


def table_view(component_key, object_type, table_style, table_height):
    if st.session_state["header_switch"]:
        with st.container(key=f"{component_key}_head", width="stretch", height="content"):
            st.markdown(f"##### *{TERMS[object_type]} history*", text_alignment="left")
    with st.container(border=False, width="stretch", height=table_height):
        if object_type == "main":
            database = hold.load_main_database()
        elif object_type == "secondary":
            database = hold.load_secondary_database()

        rows = hold.process_collection_db(database, object_type)["table_data"]
        dataframe = hold.data_to_dataframe(rows, object_type)
        styled_dataframe = (
            dataframe.style.set_properties(
                **{"background-color": table_style[1]}
            )
            .set_properties(
                subset=[TERMS["attempt"]], 
                **{"text-align": "right"}
            )
            .format(precision=0)
        )
    
        st.dataframe(
            styled_dataframe,
            hide_index=True, 
            column_config={
                " ": st.column_config.Column(width=30, alignment="center")
            },
            height="stretch",
            key="table",
            placeholder=""
        )
