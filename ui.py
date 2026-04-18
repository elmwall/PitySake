import os

import pandas as pd
import streamlit as st

# from settings.config import UITERMS, DIRECTORIES, DATAPATH, SETTINGS
# from app import Archivist  

is_demo = True
if is_demo:
    from demo_settings.config import UITERMS, DIRECTORIES, DATAPATH, SETTINGS
else:
    from settings.config import UITERMS, DIRECTORIES, DATAPATH, SETTINGS

settings_file = os.path.join(DIRECTORIES["UIFolder"], SETTINGS["UISettings"])
# arciv = Archivist(DIRECTORIES, SETTINGS, settings_file)
# options = arciv.reader()

st.title(f"*{UITERMS["title"]}*")
st.markdown(f"*{UITERMS["subtitle"]}*")

def data_upload(file_list):
    # df = pd.read_csv(file)
    # return df
    df_list = list()
    for file in file_list:
        report_path = os.path.join(DIRECTORIES["DataFolder"], file)
        df = pd.read_csv(report_path)
        df[UITERMS["attempts"]] = pd.to_numeric(UITERMS["attempts"], errors="coerce")
        df_list.append(df)

    return df_list

files = [DATAPATH["CharReport"], DATAPATH["MiscReport"], DATAPATH["ToolReport"]]
df_char, df_misc, df_tool = data_upload(files)


st.markdown("---")
st.subheader(f"{UITERMS["datatable_char"]}")
st.dataframe(data=df_char)

st.markdown("---")
st.subheader(f"{UITERMS["datatable_tool"]}")
st.dataframe(data=df_tool)

st.markdown("---")
st.subheader(f"{UITERMS["datatable_misc"]}")
st.dataframe(data=df_misc)



