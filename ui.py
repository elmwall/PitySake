import os

import pandas as pd
import streamlit as st

from settings.config import PATHWAYS
from file_manager import Archivist


settings_file = os.path.join(PATHWAYS["UIFolder"], PATHWAYS["UISettings"])
arciv = Archivist(PATHWAYS, settings_file)
options = arciv.reader()

st.title(f"*{options["terms"]["title"]}*")
st.markdown(f"*{options["terms"]["subtitle"]}*")

def data_upload(file_list):
    # df = pd.read_csv(file)
    # return df
    df_list = list()
    for file in file_list:
        report_path = os.path.join(PATHWAYS["DataFolder"], file)
        df = pd.read_csv(report_path)
        df[options["terms"]["attempts"]] = pd.to_numeric(df[options["terms"]["attempts"]], errors="coerce")
        df_list.append(df)

    return df_list

files = [PATHWAYS["CharReport"], PATHWAYS["MiscReport"], PATHWAYS["ToolReport"]]
df_char, df_misc, df_tool = data_upload(files)


st.markdown("---")
st.subheader(f"{options["terms"]["datatable_char"]}")
st.dataframe(data=df_char)

st.markdown("---")
st.subheader(f"{options["terms"]["datatable_tool"]}")
st.dataframe(data=df_tool)

st.markdown("---")
st.subheader(f"{options["terms"]["datatable_misc"]}")
st.dataframe(data=df_misc)



