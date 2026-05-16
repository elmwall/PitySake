"""
add info
"""

import logging
import time

import streamlit as st

from .file_manager import Archivist
import app.data_access as hold


DATAPATH = st.session_state["DATAPATH"]
DIRECTORIES = st.session_state["DIRECTORIES"]
SETTINGS = st.session_state["SETTINGS"]
TERMS = st.session_state["TERMS"]
logger = logging.getLogger(__name__)


def settings():
    logger.info("Running style.settings")

    st.set_page_config(
        page_title='PitySake', page_icon = "accessories/icon1.ico", layout="wide")
    st.html("""
        <style> 
            
            .block-container {
                margin: 0rem 0rem; 
                padding: 0rem 0rem;
            } 

            [data-testid='stVerticalBlock'] {
                gap: 0.2rem;
            } 

        </style>""")
    st.html("""
        <style> 
            .st-key-settings_main, .st-key-smallstat > div {
                white-space: nowrap;
            } 

            header {
                visibility: hidden;
            } 

            .st-key-border_options {
                width: 400px; min-width: 350px;
            } 

            .st-key-border_options button {
                min-width: 80px;
            } 

            .st-key-page_title button {
                width: 280px; 
                margin: 0rem 1rem;
            } 
        </style>""")

    feature_keys = [
        "reg_object", "progress", "calc", "smallstat", "main_object_data", 
        "secondary_object_data", "timeline", "settings"]
    progress_calc_keys = ["tool", "attribute", "origin"]

    return feature_keys, progress_calc_keys


def style(feature_keys, keylist_prog_calc):
    logger.info("Running style.style")
    themes = st.session_state["themes"]
    active_theme = themes["active"]
    active_theme_settings = themes[active_theme]
    html_main_container = """
        <style> 
            .st-key-REF {
                background-color: BGR_COLOR_REF;
            } 
        </style>""".replace("BGR_COLOR_REF", active_theme_settings["main_container"])
    html_header = """
        <style> 
            .st-key-REF {
                background-color: COLOR_REF; 
                border: none; 
                margin-bottom: 0rem; 
                padding: 0rem 1rem 0rem; 
                border-top-left-radius: 10px; 
                border-top-right-radius: 30px;
            } 
        </style>""".replace("COLOR_REF", active_theme_settings["feature_header"])
    
    for x in feature_keys:
        style_main_container = html_main_container.replace("REF", f"{x}_main")
        st.html(style_main_container)
        style_html_header = html_header.replace("REF", f"{x}_head")
        st.html(style_html_header)
    st.html(html_header)

    # Subcontainer style
    html_subcontainer = """
        <style> 
            .st-key-REF {
                background-color: COLOR_REF;
            } 
        </style>""".replace("COLOR_REF", active_theme_settings["sub_container"])

    # Object registration feature
    registration_keys = list()
    for x in range(10):
        key = f"sub1_{str(x)}"
        x = registration_keys.append(key)
        style_subcontainer = html_subcontainer.replace("REF", key)
        st.html(style_subcontainer)
    html_widget = """
        <style> 
            .st-key-REF {
                background-color: COLOR_REF; 
                margin: 0rem 0rem; 
                padding: 0.1rem 0rem 0.1rem 0.2rem; 
                border-radius: 30px;
            } 
        </style>""".replace("COLOR_REF", active_theme_settings["small_widget"])
    
    # Progress meter feature
    prog_meter_keys = list()
    for x in range(10):
        key = f"sub2_{str(x)}"
        x = prog_meter_keys.append(key)
        style_subcontainer = html_widget.replace("REF", key)
        st.html(style_subcontainer)

    # Data viewer feature tables "ch_data", "secondary_data", 
    table_style = [active_theme_settings["background"], 
                   active_theme_settings["main_container"]]

    # Highlights and inicators
    highlight_html = """
        <style> 
            .st-key-KEY_REF button * {
                color: COLOR_REF
            } 

            .st-key-KEY_REF p {
                font-size: 1.05rem; 
                font-weight: 700;
            } 
        </style>""".replace("COLOR_REF", active_theme_settings["highlight_text"])

    # Progress calculator feature
    st.html("""
        <style> 
            span.katex-display span.katex span.katex-html {
                font-size: 3rem; 
                margin-top: 0rem;
            } 

            .st-key-result_disp {
                overflow-y: hidden;
            } 
        </style>
        """)
    # Feature details
    detail_pill_style = """
        <style>  
            .st-key-REF * {
                justify-content: center;
            } 
            .st-key-REF button {
                flex: 1; 
                min-width: 90px; 
                max-width: 160px;
            }
        </style>"""
    for x in keylist_prog_calc:
        st.html(detail_pill_style.replace("REF", x))

    return registration_keys, prog_meter_keys, highlight_html, table_style


@st.dialog(f"Change theme", width="small")
def theme():
    logger.info("Running style.theme @st.dialog")

    arciv = Archivist(DIRECTORIES, DATAPATH, "nofile")
    themes = st.session_state["themes"]
    active_theme = themes["active"]

    st.write(f"Select theme")
    col_left, col_right = st.columns([0.6, 0.4])
    active_theme = themes["active"]
    theme_options = list(themes.keys())
    theme_options.remove("active")

    with col_left:
        selected_theme = st.selectbox(
            "themes", options=theme_options, key="active_theme_temp", 
            on_change=_reset_colors, args=(themes,), 
            label_visibility="collapsed")
    if col_right.checkbox("Dont close on change"):
        st.session_state["leave_theme_open"] = True
    with col_right:
        select_colors = st.checkbox(
            "Edit theme", key="change_colors", 
            on_change=_reset_colors, args=(themes,))
    
    if select_colors:
        with st.container(horizontal_alignment="center"):
            if "background_temp" in st.session_state.keys():
                _color_selector(themes, active_theme)

    st.space()
    col_1, col_2, col_3, col_4 = st.columns([1, 1, 1, 1])

    with st.container(width="stretch", horizontal_alignment="center"):
        if col_2.button("Apply", type="secondary", width="stretch"):
            st.session_state["show_theme_settings"] = True
            themes["active"] = selected_theme
            config_base = """
                [server]\n
                runOnSave = true\n\n
            """
            if select_colors:
                themes[selected_theme] = {
                    "background": st.session_state["background_temp"],
                    "input_field": st.session_state["input_field_temp"],
                    "highlights": st.session_state["highlights_temp"],
                    "highlight_text": st.session_state["highlight_text_temp"],
                    "text_color": st.session_state["text_color_temp"],
                    "main_container": st.session_state["main_container_temp"],
                    "feature_header": st.session_state["feature_header_temp"],
                    "sub_container": st.session_state["sub_container_temp"],
                    "small_widget": st.session_state["small_widget_temp"],
                    "positive_color": st.session_state["positive_color_temp"],
                    "neutral_color": st.session_state["neutral_color_temp"],
                    "negative_color": st.session_state["negative_color_temp"],
                    "header_switch": st.session_state["header_switch_temp"]
                }

                config = config_base + f"""
                    [theme]\n
                    backgroundColor = '{st.session_state["background_temp"]}'\n
                    secondaryBackgroundColor = '{st.session_state["input_field_temp"]}'\n
                    primaryColor = '{st.session_state["highlights_temp"]}'\n
                    textColor = '{st.session_state["text_color_temp"]}'\n
                    font = 'sans serif'
                """
            else:
                config = config_base + f"""
                    [theme]\n
                    backgroundColor = '{themes[selected_theme]["background"]}'\n
                    secondaryBackgroundColor = '{themes[selected_theme]["input_field"]}'\n
                    primaryColor = '{themes[selected_theme]["highlights"]}'\n
                    textColor = '{themes[selected_theme]["text_color"]}'\n
                    font = 'sans serif'
                """
            for x in themes[selected_theme].keys():
                st.session_state[x] = st.session_state[f"{x}_temp"]
            st.session_state["theme_edited"] = time.perf_counter()
            try:
                with open(".streamlit/config.toml", "w") as f:
                    f.write(config.strip())
            except Exception as e:
                raise RuntimeError(f"Error from {e} occurred while attempting to write to config.toml")
            arciv.writer(themes, other_file="ui_themes.json", join_path="settings")
            print("Theme updated.")

        if col_3.button("Done", type="secondary", width="stretch"):
            select_colors = False
            st.session_state["show_theme_settings"] = False
            st.rerun()


def _reset_colors(themes):
    for cat, col in themes[st.session_state["active_theme_temp"]].items():
        st.session_state[f"{cat}_temp"] = col


def _color_selector(themes, active_theme):
    for x in themes[active_theme].keys():
        if f"{x}_temp" not in st.session_state:
            st.session_state[f"{x}_temp"] = themes[st.session_state["active_theme_temp"]][x]

    st.space("small")
    col_1, col_2, col_3, col_4 = st.columns([0.6, 0.4, 0.6, 0.4])

    # Background color - in config
    st.html("""
        <style> 
            .st-key-bgr_col button {
                background-color: COLOR_REF; 
                border-color: transparent;
            } 
        </style>""".replace("COLOR_REF", themes[active_theme]["background"]))
    col_1.button("Background", key="bgr_col", width="stretch")
    col_2.color_picker("Background", key="background_temp", label_visibility="collapsed")
    
    # Main feature container - in json
    st.html("""
        <style> 
            .st-key-ft_col button {
                background-color: COLOR_REF; 
                border-color: transparent;
            } 
        </style>""".replace("COLOR_REF", themes[active_theme]["main_container"]))
    col_1.button("Feature", key="ft_col", width="stretch")
    col_2.color_picker("Feature", key="main_container_temp", label_visibility="collapsed")
    
    # Feature sub-container - in json
    st.html("""
        <style> 
            .st-key-gr_col button {
                background-color: COLOR_REF; 
                border-color: transparent;
            } 
        </style>""".replace("COLOR_REF", themes[active_theme]["sub_container"]))
    col_1.button("Group", key="gr_col", width="stretch")
    col_2.color_picker("Group", key="sub_container_temp", label_visibility="collapsed")
    
    # Feature sub-widget - in json
    st.html("""
        <style> 
            .st-key-sw_col button {
                background-color: COLOR_REF; 
                border-color: transparent;
            } 
        </style>""".replace("COLOR_REF", themes[active_theme]["small_widget"]))
    col_1.button("Widget", key="sw_col", width="stretch")
    col_2.color_picker("Widget", key="small_widget_temp", label_visibility="collapsed")

    # Feature header - in json
    st.html("""
        <style> 
            .st-key-fhd_col button {
                background-color: COLOR_REF; 
                border-color: VIS_REF;
            } 
        </style>""".replace("COLOR_REF", themes[active_theme]["feature_header"]))
    col_1.button("Header", key="fhd_col", width="stretch")
    col_2.color_picker("Headers", key="feature_header_temp", label_visibility="collapsed")

    # Input field - in config
    st.html("""
        <style> 
            .st-key-ip_col button {
                background-color: COLOR_REF; 
                border-color: transparent;
            } 
        </style>""".replace("COLOR_REF", themes[active_theme]["input_field"]))
    col_1.button("Input field", key="ip_col", width="stretch")
    col_2.color_picker("Input field", key="input_field_temp", label_visibility="collapsed")
    
    # Highlights - in config
    st.html("""
        <style> 
            .st-key-hl_col button {
                background-color: VIS_REF; 
                color: COLOR_REF; 
                border-color: COLOR_REF;
            } 
        </style>""".replace("COLOR_REF", themes[active_theme]["highlights"]).replace("VIS_REF", themes[active_theme]["main_container"]))
    col_3.button("Highlights", key="hl_col", width="stretch")
    col_4.color_picker("Highlights", key="highlights_temp", label_visibility="collapsed")
    
    # Highligh text - in json
    st.html("""
        <style> 
            .st-key-hl_txt button {
                background-color: VIS_REF; 
                color: COLOR_REF; 
                border-color: 
                COLOR_REF;
            } 
            
            .st-key-hl_txt button * {
                font-weight: 600;
            } 
        </style>""".replace("COLOR_REF", themes[active_theme]["highlight_text"]).replace("VIS_REF", themes[active_theme]["highlights"]))
    col_3.button("Highlight text", key="hl_txt", width="stretch")
    col_4.color_picker("Highlight text", key="highlight_text_temp", label_visibility="collapsed")

    # Positive indicators - in json
    st.html("""
        <style> 
            .st-key-pos_col button {
                background-color: VIS_REF; 
                color: COLOR_REF; 
                border-color: 
                COLOR_REF;
            } 
        </style>""".replace("COLOR_REF", themes[active_theme]["positive_color"]).replace("VIS_REF", themes[active_theme]["main_container"]))
    col_3.button("Positive", key="pos_col", width="stretch")
    col_4.color_picker("Positive", key="positive_color_temp", label_visibility="collapsed")
    
    # Neutral indicators - in json
    st.html("""
        <style> 
            .st-key-neu_col button {
                background-color: VIS_REF; 
                color: COLOR_REF; 
                border-color: COLOR_REF;
            } 
        </style>""".replace("COLOR_REF", themes[active_theme]["neutral_color"]).replace("VIS_REF", themes[active_theme]["main_container"]))
    col_3.button("Neutral", key="neu_col", width="stretch")
    col_4.color_picker("Neutral", key="neutral_color_temp", label_visibility="collapsed")
    
    # Negative indicators - n json
    st.html("""
        <style> 
            .st-key-neg_col button {
                background-color: VIS_REF; 
                color: COLOR_REF; 
                border-color: COLOR_REF;
            } 
        </style>""".replace("COLOR_REF", themes[active_theme]["negative_color"]).replace("VIS_REF", themes[active_theme]["main_container"]))
    col_3.button("Negative", key="neg_col", width="stretch")
    col_4.color_picker("Negative", key="negative_color_temp", label_visibility="collapsed")
    
    # General text - in config
    st.html("""
        <style> 
            .st-key-tx_col button {
                color: COLOR_REF; 
                border-color: transparent;
            } 
        </style>""".replace("COLOR_REF", themes[active_theme]["text_color"]))
    col_3.button("Text", key="tx_col", width="stretch")
    col_4.color_picker("Text", key="text_color_temp", label_visibility="collapsed")

    col_l, col_r = st.columns(2)
    col_l.space()
    col_l.checkbox("Feature header", key="header_switch_temp")
