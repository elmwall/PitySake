import time

import streamlit as st

import app.ui_progress_tracker as progress_tracker
import app.ui_object_recorder as object_recorder
import app.ui_calculate_progress as cal
import app.initialize as init
import app.ui_data_analysis as data_analysis
import app.ui_data_viewer as data_viewer
import app.ui_timeline as timeline
import app.ui_style as page
from settings.config import TERMS


CONTENT_WIDTH = 1800
WIDTH_TOT_LEFT = 950
WIDTH_TOT_RIGHT = CONTENT_WIDTH - WIDTH_TOT_LEFT
WIDTH_MID_1 = 450
WIDTH_RIGTH_1 = WIDTH_TOT_RIGHT - WIDTH_MID_1
WIDTH_MID_2 = 350
WIDTH_RIGTH_2 = WIDTH_TOT_RIGHT - WIDTH_MID_2


def border():
    """
    Generate top-side border with app name, theme options, and vertical/horizontal switch
    """
    reset_cooldown = 0.3
    with st.container(border=False, key="settings_main", width="stretch", height=40, vertical_alignment="center"):
        with st.container(border=False, width=500):
            col_sp1, col_head1, col_head2, col_head3, col_head4 = st.columns([0.1, 0.38, 0.1, 0.6, 1.9])
            col_head1.button(f"***{TERMS["title"]}***", type="tertiary")
            if col_head2.button("", key="reload_page", icon=":material/refresh:", type="tertiary"):
                init.refresh()
            with col_head3:
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
                        page.theme()
                        if st.session_state["theme_edited"] and time.time() - st.session_state["theme_edited"] > reset_cooldown:
                            st.session_state["show_theme_settings"] = False
                            st.session_state["theme_edited"] = 0
        col_head4.toggle("Vertical view", key="vertical_view")


def horizontal_view(registration_keys, prog_meter_keys, highlight_html, table_style):
    """
    Construct dash board view for horizontal layout.
    """
    st.html("<style> .st-key-main_content {width: 100vw; min-width: 1800px;} </style>")
    width_left = WIDTH_TOT_LEFT
    table_height = "stretch"

    with st.container(
        key="main_content", 
        height="stretch", 
        horizontal_alignment="center", 
        vertical_alignment="center"
    ):
        with st.container(width=CONTENT_WIDTH):
            st.space(15)
            col_left, col_mid, col_right = st.columns([width_left, WIDTH_MID_1, WIDTH_RIGTH_1])
            with col_left:
                object_recorder.register_object("reg_object", registration_keys, width_left, highlight_html)
            with col_mid:
                data_viewer.table_view("main_data", "main", table_style, table_height)
            with col_right:
                data_viewer.table_view("utility_data", "utility", table_style, table_height)
        st.space()
        with st.container(width=CONTENT_WIDTH, height="content"):
            col_left, col_right = st.columns([width_left, WIDTH_TOT_RIGHT])
            with col_left:
                height = progress_tracker.progress_meter("progress", prog_meter_keys, width_left, highlight_html)
            with col_right:
                tab_1, tab_2 = st.tabs(["Timeline", "Calculate"])
                with tab_1:
                    timeline.timeline("timeline", height)
                with tab_2:
                    col_mid, col_right = st.columns([WIDTH_MID_2, WIDTH_RIGTH_2])
                    with col_mid:
                        cal.calculator("calc", WIDTH_MID_2, highlight_html, height)
                    with col_right:
                        data_analysis.small_stats("smallstat", registration_keys, WIDTH_RIGTH_2, height)


def vertical_view(registration_keys, prog_meter_keys, highlight_html, table_style):
    """
    Construct piled vertical layout, optimal for more narrow screens/windows
    """
    st.html("<style> .st-key-main_content {width: 100vw; min-width: 800px; max-width: 1000px;} .st-key-content_frame {padding: 1rem;} </style>")
    table_height = 300
    with st.container(
        key="main_content", 
        height="stretch", 
        width="stretch", 
        horizontal_alignment="center", 
        vertical_alignment="center"
    ):
        width_left = "stretch"
        # st.space(50)
        # with col_left:
        with st.container(key="content_frame", width=width_left, horizontal_alignment="center"):
            object_recorder.register_object("reg_object", registration_keys, width_left, highlight_html)
            st.space()
            height = progress_tracker.progress_meter("progress", prog_meter_keys, width_left, highlight_html)
            col_mid, col_right = st.columns([WIDTH_MID_1, WIDTH_RIGTH_1])
            with col_mid:
                st.space("xxsmall")
                data_viewer.table_view("main_data", "main", table_style, table_height)
            with col_right:
                st.space("xxsmall")
                data_viewer.table_view("utility_data", "utility", table_style, table_height)
            tab_1, tab_2 = st.tabs(["Timeline", "Calculate"])
            with tab_1:
                timeline.timeline("timeline", height)
            with tab_2:
                col_mid, col_right = st.columns([WIDTH_MID_2, WIDTH_RIGTH_2])
                with col_mid:
                    cal.calculator("calc", WIDTH_MID_2, highlight_html, height)
                with col_right:
                    pass
                    data_analysis.small_stats("smallstat", registration_keys, WIDTH_RIGTH_2, height)

def tab_view(registration_keys, prog_meter_keys, highlight_html, table_style):
    tab_1, tab_2, tab_3 = st.tabs(["Register object", "Progress tracker", "View data"])
    width_left = 900
    table_height = "stretch"
    height = 300
    with tab_1:
        object_recorder.register_object("reg_object", registration_keys, width_left, highlight_html)
        cal.calculator("calc", WIDTH_MID_2, highlight_html, height)
    with tab_2:
        progress_tracker.progress_meter("progress", prog_meter_keys, width_left, highlight_html)
    with tab_3:
        data_viewer.table_view("main_data", "main", table_style, table_height)
        data_viewer.table_view("utility_data", "utility", table_style, table_height)
        data_analysis.small_stats("smallstat", registration_keys, WIDTH_RIGTH_2, height)
        timeline.timeline("timeline", height)
