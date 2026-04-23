import os

import pandas as pd
import streamlit as st

# # from settings.config import UITERMS, DIRECTORIES, DATAPATH, SETTINGS
from app import Archivist, Negotiator
from app.ui_progress_tracker import progress_meter
# from app.ui_object_recorder import register_object
import app.ui_object_recorder as ore

is_demo = False
if is_demo:
    from demo_settings.config import TERMS, UITERMS, DIRECTORIES, DATAPATH, SETTINGS
else:
    from settings.config import TERMS, UITERMS, DIRECTORIES, DATAPATH, SETTINGS

settings_file = os.path.join(DIRECTORIES["UIFolder"], SETTINGS["UISettings"])
arciv = Archivist(DIRECTORIES, DATAPATH, settings_file)
negotiator = Negotiator()

st.set_page_config(layout="wide")
st.markdown("<style> .block-container {padding-top: 2rem; padding-bottom: 0rem; padding-left: 5rem; padding-right: 5rem;}</style>", unsafe_allow_html=True)

st.title(f"*{UITERMS["title"]}*", text_alignment="center")

# def popinput(string_val):
#     st.popover(string_val)


attempts = arciv.reader(other_file="progress_data.json", join_path="data")
data_options = arciv.reader(other_file="data_options.json", join_path="settings")
# print(settings_file)
# col_main1, col_main2 = st.columns(2)


ore.register_object(arciv, negotiator, DIRECTORIES, DATAPATH, data_options, TERMS, attempts)
# print(data_options)
# st.divider()
progress_meter(arciv, negotiator, DATAPATH, TERMS, attempts)

# DRAFTS

# st.markdown(f"*{UITERMS["subtitle"]}*")

# def data_upload(file_list):
#     # df = pd.read_csv(file)
#     # return df
#     df_list = list()
#     for file in file_list:
#         report_path = os.path.join(DIRECTORIES["DataFolder"], file)
#         df = pd.read_csv(report_path)
#         df[UITERMS["attempts"]] = pd.to_numeric(UITERMS["attempts"], errors="coerce")
#         df_list.append(df)

#     return df_list

# files = [DATAPATH["CharReport"], DATAPATH["MiscReport"], DATAPATH["ToolReport"]]
# df_char, df_misc, df_tool = data_upload(files)

# st.subheader(f"Current {UITERMS["attempts"]}")
# st.markdown(
#     f"""
#     | {TERMS["Source"]} | {TERMS["Attempt"]} |
#     |-|-|
#     | {TERMS["Temp"]} | {attempts[f"Character {TERMS["Temp"]}"][TERMS["Attempt"]]} |
#     | {TERMS["Mix"]} | {attempts[TERMS["Mix"]][TERMS["Attempt"]]} |
#     | {TERMS["Standard source"]} | {attempts[f"{TERMS["Tool"]} {TERMS["Temp"]}"][TERMS["Attempt"]]} |
# """)

# def checking():
#     print("check")
# state = st.checkbox("Check", value=True, on_change=checking)

# select = st.selectbox("attribute", options=data_options[TERMS["Character"]][TERMS["Origin"]])

# # Initialize session state if it doesn't exist
# if 'count' not in st.session_state:
#     st.session_state.count = 0

# st.markdown("""
#     <style>
#     .st-key-green_btn button {
#         background-color: #262730;
#         color: white;
#         border: none;
#     }
#     .st-key-green_btn button:hover {
#         background-color: #353942;
#     }
#     </style>
# """, unsafe_allow_html=True)


# st.write(f"Current Value: {st.session_state.slider_val}")

# st.write("Count = ", st.session_state.count)

# col_1, col_2, col_3 = st.columns(3, width="stretch")
# with col_1:
#     st.markdown("---")
#     st.subheader(f"{UITERMS["datatable_char"]}")
#     st.dataframe(data=df_char)

# with col_2:
#     st.markdown("---")
#     st.subheader(f"{UITERMS["datatable_tool"]}")
#     st.dataframe(data=df_tool)

# with col_3:
#     st.markdown("---")
#     st.subheader(f"{UITERMS["datatable_misc"]}")
#     st.dataframe(data=df_misc)



