import streamlit as st
import os
import pandas as pd

def table_view(component_key, height, TERMS, object_type, arciv, negotiator, DIRECTORIES, DATAPATH, data_options, UITERMS):
    with st.container(key=f"{component_key}_head", height=35):
        st.markdown(f"#### *{TERMS[object_type]} data*", text_alignment="left")
    with st.container(border=True, key=f"{component_key}_main", height="stretch"):
        st.markdown("hello there")

        data_reference = TERMS["Character"]
        datafile = DATAPATH[data_reference]
        object_database = arciv.reader(datafile, join_path="data")

        def data_upload(file_list):
            # df = pd.read_csv(file)
            # return df
            df_list = list()
            for file in file_list:
                report_path = os.path.join(DIRECTORIES["DataFolder"], file)
                df = pd.read_csv(report_path)
                # df[UITERMS["attempts"]] = pd.to_numeric(UITERMS["attempts"], errors="coerce")
                df_list.append(df)

            return df_list
        
        files = [DATAPATH["CharReport"], DATAPATH["ToolReport"]]
        df_char, df_tool = data_upload(files)

        # col_1, col_2 = st.columns(2, width="stretch")
        # with col_1:
            # st.markdown("---")
            # st.subheader(f"{UITERMS["datatable_char"]}")
        if object_type == "Character":
            st.dataframe(data=df_char)
        else:
            st.dataframe(data=df_tool)

        # with col_2:
        #     st.markdown("---")
        #     st.subheader(f"{UITERMS["datatable_tool"]}")
        #     st.dataframe(data=df_tool)

