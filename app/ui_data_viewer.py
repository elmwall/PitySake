import streamlit as st
import pandas as pd

from .data_access import Holder

from settings.config import TERMS


def table_view(component_key, object_type, table_style, set_width, table_height):
    hold = Holder()
    if st.session_state["header_switch"]:
        with st.container(key=f"{component_key}_head", width="stretch", height="content"):
            st.markdown(f"##### *{TERMS[object_type]} history*", text_alignment="left")
    with st.container(border=False, width="stretch", height=table_height):
        if object_type == "main":
            database = hold.load_main_database()
        if object_type == "utility":
            database = hold.load_utility_database()

        collected = dict()

        def data_to_df(object_database):
            rows = []
            for name, info in object_database.items():
                collected[name] = 0
                for index, details in info[TERMS["event"]].items():
                    date, idx = index.split("-")
                    if object_type == "main": 
                        view_coll = f"C{collected[name]}"

                    
                    attempt = details[TERMS["attempt"]]
                    source = details[TERMS["source"]] if details[TERMS["source"]] else None
                    state = details[TERMS["state"]] if details[TERMS["state"]] else None
                    if object_type == "main":
                        rows.append({
                            "Date": f"{date} | {view_coll}",
                            "Name": name,
                            "Index": idx,
                            TERMS["attempt"]: attempt,
                            "source": source,
                            TERMS["state"]: state
                        })
                    else:
                        rows.append({
                            "Date": date,
                            "Name": name,
                            "Index": idx,
                            TERMS["attempt"]: attempt,
                            "source": source,
                            TERMS["state"]: state
                        })
                    collected[name] += 1
            df = pd.DataFrame(rows)
            df = df.sort_values(["Date", "Index"], ascending=False).drop(columns=["Index", f"{TERMS["state"]}"]).fillna("")
            df[TERMS["attempt"]] = pd.to_numeric(df[TERMS["attempt"]], errors="coerce").astype("Int64")

            return df

        df = data_to_df(database)
        st.dataframe(
            df.style.set_properties(
                subset=[TERMS["attempt"]], 
                **{"text-align": "right"}
            )
            .set_properties(**{"background-color": table_style[1]}),
            column_config={
                TERMS["state"]: st.column_config.Column(width="small")
            },
            hide_index=True, 
            height="stretch",
            key="table"
        )
