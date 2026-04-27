import os

import pandas as pd
import streamlit as st

from app import Archivist, Negotiator
import app.ui_progress_tracker as prog
import app.ui_object_recorder as ore
import app.ui_calculate_progress as cal
import app.ui_data_analysis as stat
import app.ui_data_viewer as dave
import app.ui_timeline as tim

is_demo = False
if is_demo:
    from demo_settings.config import TERMS, UITERMS, DIRECTORIES, DATAPATH, SETTINGS
else:
    from settings.config import TERMS, UITERMS, DIRECTORIES, DATAPATH, SETTINGS

# Set directory and file
placeholder = os.path.join(DIRECTORIES["UIFolder"], SETTINGS["UISettings"])
arciv = Archivist(DIRECTORIES, DATAPATH, placeholder)
negotiator = Negotiator()
# Import data files
attempts = arciv.reader(other_file="progress_data.json", join_path="data")
data_options = arciv.reader(other_file="data_options.json", join_path="settings")

# Set page style and references
st.set_page_config(page_title='PitySake', page_icon = "icon1.ico", layout="wide")
st.markdown("<style> .block-container {padding: 2rem;}</style>", unsafe_allow_html=True)
# Feature - Progressmeter

# Main container style
# html_main_container = "<style> .dataframe td {white-space: nowrap;} </style>"
html_main_container = "<style> .st-key-REF {background-color: #2d0936} </style>"
html_header = "<style> .st-key-REF {background-color: rgba(100, 255, 140, 0.10); border: none; margin-bottom: -1rem; padding: 0.4rem 1rem 1rem; border-top-left-radius: 10px; border-top-right-radius: 30px;} </style>"
# html_main_container = "<style> .st-key-REF {background-color: #340b3e} </style>"
key_reg_obj, key_progress, key_calc, key_smallstat, key_tabc, key_tabt, key_time = "reg_object", "progress", "calc", "smallstat", "ch_data", "tool_data", "timeline"
key_list = [key_reg_obj, key_progress, key_calc, key_smallstat, key_tabc, key_tabt, key_time]
for x in key_list:
    style_main_container = html_main_container.replace("REF", f"{x}_main")
    st.html(style_main_container)
    style_html_header = html_header.replace("REF", f"{x}_head")
    st.html(style_html_header)
st.html("<style> [data-testid='stVerticalBlock'] > div {margin: -0.2rem 0rem -0.2rem; padding: 0rem 0rem 0rem;} </style>")
st.html(html_header)
# Subcontainer style
html_subcontainer = "<style> .st-key-REF {background-color: rgba(255, 255, 255, 0.03);} </style>"
# Object registration feature
key_list_reg = list()
for x in range(6):
    key = f"sub1_{str(x)}"
    x = key_list_reg.append(key)
    style_subcontainer = html_subcontainer.replace("REF", key)
    st.html(style_subcontainer)
html_subcontainer = "<style> .st-key-REF {background-color: rgba(0, 0, 0, 0.2); margin: 0.2rem 0rem; padding: 0.3rem 0rem; border-radius: 30px;} </style>"
# Progress meter feature
key_list_meter = list()
for x in range(10):
    key = f"sub2_{str(x)}"
    x = key_list_meter.append(key)
    style_subcontainer = html_subcontainer.replace("REF", key)
    st.html(style_subcontainer)
# Progress calculator feature
st.html("<style>span.katex-display span.katex span.katex-html {font-size: 3rem; margin-top: -0.4rem;} </style>")
# Feature details
detail_pill_style = "<style>  .st-key-REF * {justify-content: center;} .st-key-REF button {flex: 1 1 110px; max-width: 160px;}</style>"
for x in ["tool", "attribute", "origin"]:
    st.html(detail_pill_style.replace("REF", x))

st.title(f"*{UITERMS["title"]}*", text_alignment="center")
# Features
feature_size_left = 900
st.html("<style> .st-key-main_content {min-width: 1800px;} </style>")
# st.html("<style> .st-key-main_content {background-color: rgba(0, 0, 0, 0.2); margin: 0.2rem 0rem; padding: 0.3rem 0rem; border-radius: 30px;} </style>")
# col_features = [1000, 300, 500]
# width = 1000
with st.container(key="main_content", width=1800):
    with st.container():
        col_left, col_mid, col_right = st.columns([feature_size_left, 450, 450])
        with col_left:
            ore.register_object(key_reg_obj, key_list_reg, feature_size_left, arciv, negotiator, DIRECTORIES, DATAPATH, data_options, TERMS, attempts)
        with col_mid:
            dave.table_view(key_tabc, 300, TERMS, "Character", arciv, negotiator, DIRECTORIES, DATAPATH, data_options, UITERMS)
        with col_right:
            dave.table_view(key_tabt, 300, TERMS, "Tool", arciv, negotiator, DIRECTORIES, DATAPATH, data_options, UITERMS)
    st.space()
    with st.container(vertical_alignment="center"):
        col_left, col_mid, col_right = st.columns([feature_size_left, 350, 550])
        with col_left:
            height = prog.progress_meter(key_progress, key_list_meter, feature_size_left, arciv, negotiator, DATAPATH, TERMS, attempts)
        with col_mid:
            cal.calculator(data_options["Value limits"]["Attempt general limit"], key_calc, height)
        with col_right:
            stat.small_stats(key_smallstat, height, key_reg_obj, key_list_reg, arciv, negotiator, DIRECTORIES, DATAPATH, data_options, TERMS, attempts)
    tim.timeline(key_time, feature_size_left, arciv, negotiator, DATAPATH, TERMS, attempts)

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



