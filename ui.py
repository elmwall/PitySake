import os
import time

import streamlit as st

from app import Archivist, Negotiator
import app.ui_progress_tracker as prog
import app.ui_object_recorder as ore
import app.ui_calculate_progress as cal
import app.ui_data_analysis as stat
import app.ui_data_viewer as dave
import app.ui_timeline as tim
import app.ui_style as style

is_demo = False
if is_demo:
    from demo_settings.config import TERMS, UITERMS, DIRECTORIES, DATAPATH, SETTINGS
else:
    from settings.config import TERMS, UITERMS, DIRECTORIES, DATAPATH, SETTINGS


def get_library(object_type, database_key):
    object_database = arciv.reader(DATAPATH[TERMS[object_type]], join_path="data")
    if database_key not in st.session_state.keys():
        st.session_state[database_key] = object_database
    elif not st.session_state[database_key]:
        st.session_state[database_key] = object_database
    return object_database

# Set directory and file
placeholder = os.path.join(DIRECTORIES["UIFolder"], SETTINGS["UISettings"])
arciv = Archivist(DIRECTORIES, DATAPATH, placeholder)
negotiator = Negotiator()
# Import files and options
attempts = arciv.reader(other_file="progress_data.json", join_path="data")
themes = arciv.reader(other_file="ui_themes.json", join_path="settings")
# active_theme = themes["active"]
data_options = arciv.reader(other_file="data_options.json", join_path="settings")
object_database_main = get_library("Character", "main_database")
object_database_util = get_library("Tool", "utility_database")


# Set page style
style.layout()
col_panel, col_main = st.columns([0.03, 0.97])
feature_keys = ["reg_object", "progress", "calc", "smallstat", "ch_data", "tool_data", "timeline"]
progress_calc_keys = ["tool", "attribute", "origin"]
registration_keys, prog_meter_keys, highlight_textstyle, highlight_html, table_style = style.style(feature_keys, progress_calc_keys, themes)

# Build layout
col_main.title(f"*{UITERMS["title"]}*", text_alignment="center")

width_left = 900
width_total_right = 900
width_mid_1 = 450
width_right_1 = width_total_right - width_mid_1
width_mid_2 = 350
width_right_2 = width_total_right - width_mid_2
with col_main:
    with st.container(key="main_content", width=1800):
        with st.container():
            col_left, col_mid, col_right = st.columns([width_left, width_mid_1, width_right_1])
            with col_left:
                ore.register_object("reg_object", registration_keys, width_left, highlight_textstyle, highlight_html, arciv, negotiator, DIRECTORIES, DATAPATH, data_options, TERMS, attempts)
            with col_mid:
                dave.table_view("ch_data", 300, TERMS, "Character", table_style, arciv, negotiator, DIRECTORIES, DATAPATH, data_options, UITERMS)
            with col_right:
                dave.table_view("tool_data", 300, TERMS, "Tool", table_style, arciv, negotiator, DIRECTORIES, DATAPATH, data_options, UITERMS)
        st.space()
        with st.container(vertical_alignment="center"):
            col_left, col_mid, col_right = st.columns([width_left, width_mid_2, width_right_2])
            with col_left:
                height = prog.progress_meter("progress", prog_meter_keys, width_left, themes[themes["active"]]["feature_background"], highlight_textstyle, highlight_html, arciv, negotiator, DATAPATH, TERMS, attempts)
            with col_mid:
                cal.calculator(data_options["Value limits"]["Attempt general limit"], "calc", height, highlight_textstyle, highlight_html)
            with col_right:
                stat.small_stats("smallstat", height, "reg_object", registration_keys, arciv, negotiator, DIRECTORIES, DATAPATH, data_options, TERMS, attempts)
        tim.timeline("timeline", width_left, arciv, negotiator, DATAPATH, TERMS, attempts)

with col_panel:
    st.space("large")
    if "show_theme_settings" not in st.session_state.keys():
        st.session_state["show_theme_settings"] = False
        st.session_state["theme_edited"] = 0
    if st.button("T"): 
        cooldown = 0.3
        st.session_state["show_theme_settings"] = True
    if st.session_state["show_theme_settings"]: 
        style.theme(arciv, themes)
        if st.session_state["theme_edited"] and time.time() - st.session_state["theme_edited"] > cooldown:
            st.session_state["show_theme_settings"] = False
            st.session_state["theme_edited"] = 0
