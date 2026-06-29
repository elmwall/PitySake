"""
Constructor module for page layout

Builds:
- Page header: layout/theme settings and title
- Main features in horizontal or vertical layout
"""

import logging

import streamlit as st

from app.initialize import set_orientation, refresh, TERMS
import app.progress_tracker as progress_tracker
import app.object_recorder as object_recorder
import app.calculate_progress as cal
import app.data_analysis as data_analysis
import app.data_viewer as data_viewer
import app.timeline as timeline
import app.style as page
import app.error_handler as error


# Constants for layout dimensions
CONTENT_WIDTH = 1850
WIDTH_TOT_LEFT = 950
WIDTH_TOT_RIGHT = CONTENT_WIDTH - WIDTH_TOT_LEFT
WIDTH_MID_1 = 450
WIDTH_RIGTH_1 = WIDTH_TOT_RIGHT - WIDTH_MID_1
WIDTH_MID_2 = 350
WIDTH_RIGTH_2 = WIDTH_TOT_RIGHT - WIDTH_MID_2

logger = logging.getLogger(__name__)


def header():
    """
    Header builder 
    - setup, placement and interactions for header elements.
    - title: display-only button
    - vertical toggle: adjusts session state key bool
    - refresh: triggers refresh of cache and session state keys
    - theme: preset theme keys and control theme dialog activation
    """
    if not st.session_state.get("initated", False):
        logger.info(f"Building header.")

    header_height = "content" if st.session_state["error"] else 40
    # Sets whole-page width area for header
    with st.container(
            border=False, key="settings_main",
            height=header_height, vertical_alignment="center"):
        # Creates columns
        c1, col_options, col_title, c3 = st.columns([0.1, 5, 2, 5])
        # Error message for user is rendered in top-right corner 
        # for visibility without being mixed up with other layout.
        # Placing it in the rendered layout instead of dialog is preferable, 
        # since only one dialog is allowed
        if st.session_state["error"]:
            with c3.container(border=True, key="error_field_main", width="stretch", height=header_height):
                error.notify()

        with col_options:
            with st.container(key="border_options"):
                col_view, col_refr, col_theme = st.columns([4, 3.5, 2])
        
        # Button is used for title display because:
        # markdown or write causes bad alignment of column contents
        col_title.button(
            f"***{TERMS["ui_title"]}***", key="page_title",
            type="tertiary", width="content")
        
        # View orientation selection - always horizontal at start
        col_view.toggle("Vertical view", key="vertical_view", on_change=set_orientation)

        if col_refr.button(
                "Refresh page", key="reload_page", 
                icon=":material/refresh:", type="tertiary", width="content"): 
            refresh()

        # Theme dialog is controlled via session state key "theme_edited" bool
        # "leave_theme_open" bool is set to prevent dialog closing prematurely during edits
        with col_theme:
            with st.container(key="tools"):
                leave_theme_open = st.session_state["leave_theme_open"]
                if not leave_theme_open:
                    st.session_state["show_theme_settings"] = False

                # Theme button
                if st.button("Theme", type="secondary", disabled=st.session_state["theme_missing"]):
                    st.session_state["show_theme_settings"] = True

                if st.session_state["show_theme_settings"]:
                    # Set theme temp keys here for editing to have them available when dialog is opened
                    st.session_state["active_theme_temp"] = st.session_state["themes"]["active"]
                    page.theme()
                    theme_edited = st.session_state.get("theme_edited", 0)
                    if theme_edited and not leave_theme_open:
                        st.session_state["show_theme_settings"] = True
                        st.session_state["theme_edited"] = 0


def horizontal_view(registration_keys: list, prog_meter_keys: list, 
                    highlight_html: str, table_style: str):
    """
    Horizontal view builder 
    
    Manages setup and placement for main content features 
    in placement:
    - row 1: 
        - columnt 1: update library
        - columnt 2: main object history tables
        - columnt 3: secondary object history tables
    - row 2: 
        - columnt 1: progress tracker
        - columnt 2:
            - tab 1: timline
            - tab 2: calculator and statistics

    Args:
        registration_keys (list): 
            keys for object registration settings
        prog_meter_keys (list): 
            keys for object progress tracker settings
    """
    if not st.session_state.get("initated", False):
        logger.info(f"Building horizontal view.")

    st.html("""
            <style> 
                .st-key-main_content {width: 100vw; min-width: 1800px;} 
            </style>""")
    width_left = WIDTH_TOT_LEFT
    table_height = "stretch"

    # Main container
    with st.container(
            key="main_content", height="stretch", 
            horizontal_alignment="center", vertical_alignment="center"):
        # Row 1
        with st.container(width=CONTENT_WIDTH):
            st.space(15)
            col_left, col_mid, col_right = st.columns(
                [width_left, WIDTH_MID_1, WIDTH_RIGTH_1])
            # Column 1 - object registration
            with col_left:
                object_recorder.register_object(
                    "reg_object", registration_keys, width_left, highlight_html)
            # Column 2 - main object table
            with col_mid:
                data_viewer.table_view(
                    "main_data", "main", table_style, table_height)
            # Column 3 - secondary object table
            with col_right:
                data_viewer.table_view(
                    "secondary_data", "secondary", table_style, table_height)
        st.space()

        # Row 2
        with st.container(width=CONTENT_WIDTH, height="content"):
            col_left, col_right = st.columns([width_left, WIDTH_TOT_RIGHT])
            # Column 1 - progress tracker
            with col_left:
                height = progress_tracker.progress_meter(
                    "progress", prog_meter_keys, width_left, highlight_html)
            # Column 2 - timeline / calculator and statistics
            with col_right:
                tab_1, tab_2 = st.tabs(["Timeline", "Calculate"])
                with tab_1:
                    timeline.timeline("timeline", height)
                with tab_2:
                    col_mid, col_right = st.columns([WIDTH_MID_2, WIDTH_RIGTH_2])
                    with col_mid:
                        cal.calculator("calc", WIDTH_MID_2, highlight_html, height)
                    with col_right:
                        data_analysis.small_stats(
                            "smallstat", registration_keys, WIDTH_RIGTH_2, height)


def vertical_view(registration_keys: list[str], prog_meter_keys: list[str], 
                  highlight_html: str, table_style: str):
    """
    Vertical view builder 
    
    Manages setup and placement for main content features 
    in stacked placement:
    - update library
    - main and secondary object history tables
    - progress tracker
    - bottom tabs:
        - tab 1: timline
        - tab 2: calculator and statistiscs

    Args:
        registration_keys (list): 
            keys for object registration settings
        prog_meter_keys (list): 
            keys for object progress tracker settings
    """
    if not st.session_state.get("initated", False):
        logger.info(f"Building vertical view.")

    st.html("""
        <style> 
            .st-key-main_content {width: 100vw; min-width: 800px; max-width: WIDTH_REFpx;} 
            .st-key-content_frame {padding: 16px;} 
        </style>""".replace("WIDTH_REF", f"{WIDTH_TOT_LEFT}"))
    table_height = 350

    # Main container
    with st.container(
            key="main_content", height="stretch", width="stretch", 
            horizontal_alignment="center", vertical_alignment="center"):
        width_left = "stretch"
        # Content frame
        with st.container(
                key="content_frame", width=width_left, horizontal_alignment="center"):
            # Object registration
            object_recorder.register_object(
                "reg_object", registration_keys, 
                width_left, highlight_html)
            st.space()

            # Progress tracker
            height = progress_tracker.progress_meter(
                "progress", prog_meter_keys, width_left, highlight_html)
            col_mid, col_right = st.columns([WIDTH_MID_1, WIDTH_RIGTH_1])

            # Main and secondary object history
            with col_mid:
                st.space("xxsmall")
                data_viewer.table_view("main_data", "main", table_style, table_height)
            with col_right:
                st.space("xxsmall")
                data_viewer.table_view("secondary_data", "secondary", table_style, table_height)
            
            # Timeline / calculator and statistics
            tab_1, tab_2 = st.tabs(["Timeline", "Calculate"])
            with tab_1:
                timeline.timeline("timeline", height)
            with tab_2:
                col_mid, col_right = st.columns([WIDTH_MID_2, WIDTH_RIGTH_2])
                with col_mid:
                    cal.calculator("calc", WIDTH_MID_2, highlight_html, height)
                with col_right:
                    pass
                    data_analysis.small_stats(
                        "smallstat", registration_keys, WIDTH_RIGTH_2, height)