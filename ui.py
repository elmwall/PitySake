import os
import time

import streamlit as st

from app.file_manager import Archivist
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
hold = Holder()
if "pending_backup" not in st.session_state.keys(): 
    st.session_state["pending_backup"] = False
if "pending_save" not in st.session_state.keys(): st.session_state["pending_save"] = False
if st.session_state["pending_backup"]: arciv.pending_backup()

# if "processed_edits" not in st.session_state.keys(): 
#     st.session_state["processed_edits"] = False
# elif st.session_state["processed_edits"]:
#     hold.dropper()

# Import files and options
attempts = hold.load_progress_data()
themes = arciv.reader(other_file="ui_themes.json", join_path="settings")
# active_theme = themes["active"]
# data_options = arciv.reader(other_file="data_options.json", join_path="settings") ######## TODO add edit options
data_options = hold.load_options()
object_database_main = hold.load_main_database()
object_database_util = hold.load_utility_database()
reset_cooldown = 0.3
config_base = "[server]\nrunOnSave = true\n\n"

# Set page style
style.layout()
col_panel, col_main = st.columns([0.03, 0.97])
feature_keys = ["reg_object", "progress", "calc", "smallstat", "main_object_data", "utility_object_data", "timeline", "settings"]
progress_calc_keys = ["tool", "attribute", "origin"]
registration_keys, prog_meter_keys, highlight_html, table_style = style.style(feature_keys, progress_calc_keys, themes)

# Build layout
# col_main.title(f"*{TERMS["ui_title"]}*", text_alignment="center")

content__width = 1800
width_total_left = 950
width_total_right = content__width - width_total_left
width_mid_1 = 450
width_right_1 = width_total_right - width_mid_1
width_mid_2 = 350
width_right_2 = width_total_right - width_mid_2
# with col_main:


# st.session_state.get("vertical_view", False)
with st.container(border=False, key="settings_main", width="stretch", height=40, vertical_alignment="center"):
    with st.container(border=False, width=250):
        col_sp1, col_head1, col_head2, col_head3 = st.columns([0.5, 2, 1.5, 1])
        col_head1.button(f"***{TERMS["title"]}***", type="tertiary")
        with col_head2:
            with st.container(key="tools"):
                if "show_theme_settings" not in st.session_state.keys():
                    st.session_state["show_theme_settings"] = False
                    st.session_state["theme_edited"] = 0
                else:
                    st.session_state["show_theme_settings"] = False
                    st.session_state["theme_edited"] = 0
                if st.button("Theme", type="tertiary", width=100): 
                    st.session_state["show_theme_settings"] = True
                if st.session_state["show_theme_settings"]: 
                    style.theme(themes, config_base)
                    if st.session_state["theme_edited"] and time.time() - st.session_state["theme_edited"] > reset_cooldown:
                        st.session_state["show_theme_settings"] = False
                        st.session_state["theme_edited"] = 0
    col_head3.toggle("Vertical view", value=False, key="vertical_view")

if not st.session_state.get("vertical_view", False):
    print("ok")
    st.html("<style> .st-key-main_content {width: 100vw; min-width: 1800px;} </style>")
    width_left = width_total_left
    with st.container(key="main_content", height="stretch", horizontal_alignment="center", vertical_alignment="center"):
        with st.container(width=content__width):
            st.space(15)
            table_height = "stretch"
            col_left, col_mid, col_right = st.columns([width_left, width_mid_1, width_right_1])
            with col_left:
                ore.register_object(data_options, attempts, "reg_object", registration_keys, width_left, highlight_html)
            with col_mid:
                dave.table_view("main_data", "main", table_style, width_mid_1, table_height)
            with col_right:
                dave.table_view("utility_data", "utility", table_style, width_right_1, table_height)
        st.space()
        with st.container(width=content__width, height="content"):
            col_left, col_right = st.columns([width_left, width_total_right])
            with col_left:
                # st.space(64)
                height = prog.progress_meter(attempts, "progress", prog_meter_keys, width_left, themes[themes["active"]]["feature_background"], highlight_html)
            with col_right:
                tab_1, tab_2 = st.tabs(["Timeline", "Calculate"])
                with tab_1:
                    # col_mid, col_right = st.columns([width_total_right - 1, 1])
                    # with col_mid:
                    tim.timeline("timeline", width_total_right, height)
                with tab_2:
                    col_mid, col_right = st.columns([width_mid_2, width_right_2])
                    with col_mid:
                        cal.calculator(data_options["value_limits"]["general_limit"], "calc", width_mid_2, highlight_html, height)
                    with col_right:
                        pass
                        stat.small_stats(data_options, "smallstat", width_right_2, height)
else:
    with st.container(key="main_content", height="stretch", width="stretch", horizontal_alignment="center", vertical_alignment="center"):
        st.html("<style> .st-key-main_content {width: 100vw; min-width: 800px; max-width: 1000px;} .st-key-content_frame {padding: 1rem;} </style>")
        width_left = "stretch"
        # st.space(50)
        # with col_left:
        with st.container(key="content_frame", width=width_left, horizontal_alignment="center"):
            ore.register_object(data_options, attempts, "reg_object", registration_keys, width_left, highlight_html)
            st.space()
            height = prog.progress_meter(attempts, "progress", prog_meter_keys, width_left, themes[themes["active"]]["feature_background"], highlight_html)
            table_height = 300
            col_mid, col_right = st.columns([width_mid_1, width_right_1])
            with col_mid:
                st.space("xxsmall")
                dave.table_view("main_data", "main", table_style, width_mid_1, table_height)
            with col_right:
                st.space("xxsmall")
                dave.table_view("utility_data", "utility", table_style, width_right_1, table_height)
            tab_1, tab_2 = st.tabs(["Timeline", "Calculate"])
            with tab_1:
                # col_mid, col_right = st.columns([width_total_right - 1, 1])
                # with col_mid:
                tim.timeline("timeline", width_total_right, height)
            with tab_2:
                col_mid, col_right = st.columns([width_mid_2, width_right_2])
                with col_mid:
                    cal.calculator(data_options["value_limits"]["general_limit"], "calc", width_mid_2, highlight_html, height)
                with col_right:
                    pass
                    stat.small_stats(data_options, "smallstat", width_right_2, height)
    
