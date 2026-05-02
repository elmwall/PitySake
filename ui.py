import os
import time

import streamlit as st

from app import Archivist
import app.ui_progress_tracker as prog
import app.ui_object_recorder as ore
import app.ui_calculate_progress as cal
import app.ui_data_analysis as stat
import app.ui_data_viewer as dave
import app.ui_timeline as tim
import app.ui_style as style

from app.data_access import Holder
from settings.config import TERMS, DIRECTORIES, DATAPATH


def get_library(object_type, database_key):
    object_database = arciv.reader(DATAPATH[TERMS[object_type]], join_path="data")
    if database_key not in st.session_state.keys():
        st.session_state[database_key] = object_database
    elif not st.session_state[database_key]:
        st.session_state[database_key] = object_database
    return object_database

# Set directory and file
arciv = Archivist(DIRECTORIES, DATAPATH, "nofile")
# Import files and options
hold = Holder()
attempts = hold.load_progress_data()
themes = arciv.reader(other_file="ui_themes.json", join_path="settings")
# active_theme = themes["active"]
data_options = arciv.reader(other_file="data_options.json", join_path="settings") ######## TODO add edit options
object_database_main = hold.load_main_database()
object_database_util = hold.load_utility_database()

# Set page style
style.layout()
col_panel, col_main = st.columns([0.03, 0.97])
feature_keys = ["reg_object", "progress", "calc", "smallstat", "main_object_data", "utility_object_data", "timeline"]
progress_calc_keys = ["tool", "attribute", "origin"]
registration_keys, prog_meter_keys, highlight_textstyle, highlight_html, table_style = style.style(feature_keys, progress_calc_keys, themes)

# Build layout
col_main.title(f"*{TERMS["ui_title"]}*", text_alignment="center")

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
                ore.register_object(data_options, attempts, "reg_object", registration_keys, width_left, highlight_textstyle, highlight_html)
            with col_mid:
                dave.table_view("main_data", "main", table_style)
            with col_right:
                dave.table_view("utility_data", "utility", table_style)
        st.space()
        with st.container(vertical_alignment="center"):
            col_left, col_mid, col_right = st.columns([width_left, width_mid_2, width_right_2])
            with col_left:
                height = prog.progress_meter(attempts, "progress", prog_meter_keys, width_left, themes[themes["active"]]["feature_background"], highlight_textstyle, highlight_html)
            with col_mid:
                cal.calculator(data_options["value_limits"]["general_limit"], "calc", height, highlight_textstyle, highlight_html)
            with col_right:
                stat.small_stats(data_options, "smallstat")
        tim.timeline("timeline")

with col_panel:
    st.space("large")
    if "show_theme_settings" not in st.session_state.keys():
        st.session_state["show_theme_settings"] = False
        st.session_state["theme_edited"] = 0
    if st.button("T"): 
        cooldown = 0.3
        st.session_state["show_theme_settings"] = True
    if st.session_state["show_theme_settings"]: 
        style.theme(themes)
        if st.session_state["theme_edited"] and time.time() - st.session_state["theme_edited"] > cooldown:
            st.session_state["show_theme_settings"] = False
            st.session_state["theme_edited"] = 0
