import time

import streamlit as st

from .file_manager import Archivist

from settings.config import DIRECTORIES, DATAPATH


def layout():
    st.set_page_config(page_title='PitySake', page_icon = "accessories/icon1.ico", layout="wide")
    st.markdown("<style> .block-container {padding: 2rem;}</style>", unsafe_allow_html=True)




# def set_color(html, color):
#     return html.replace("COLOR_REF", color)


def style(feature_keys, keylist_prog_calc, themes):
    active_theme = themes["active"]
    theme = themes[active_theme]
    # Main container style
    html_main_container = "<style> .st-key-REF {background-color: BGR_COLOR_REF;} </style>".replace("BGR_COLOR_REF", theme["main_container"])
    html_header = "<style> .st-key-REF {background-color: COLOR_REF; border: none; margin-bottom: -1rem; padding: 0.4rem 1rem 1rem; border-top-left-radius: 10px; border-top-right-radius: 30px;} </style>".replace("COLOR_REF", theme["feature_header"])
    
    for x in feature_keys:
        style_main_container = html_main_container.replace("REF", f"{x}_main")
        st.html(style_main_container)
        style_html_header = html_header.replace("REF", f"{x}_head")
        st.html(style_html_header)
    st.html("<style> [data-testid='stVerticalBlock'] > div {margin: -0.2rem 0rem -0.2rem; padding: 0rem 0rem 0rem;} </style>")
    st.html(html_header)

    # Subcontainer style
    html_subcontainer = "<style> .st-key-REF {background-color: COLOR_REF;} </style>".replace("COLOR_REF", theme["sub_container"])
    # Object registration feature
    registration_keys = list()
    for x in range(6):
        key = f"sub1_{str(x)}"
        x = registration_keys.append(key)
        style_subcontainer = html_subcontainer.replace("REF", key)
        st.html(style_subcontainer)
    html_widget = "<style> .st-key-REF {background-color: COLOR_REF; margin: 0.2rem 0rem; padding: 0.5rem 0 0.5rem 0.5rem; border-radius: 30px;} </style>".replace("COLOR_REF", theme["small_widget"])
    # Progress meter feature
    prog_meter_keys = list()
    for x in range(10):
        key = f"sub2_{str(x)}"
        x = prog_meter_keys.append(key)
        style_subcontainer = html_widget.replace("REF", key)
        st.html(style_subcontainer)
    # Data viewer feature tables "ch_data", "utility_data", 
    table_style = [theme["background"], theme["main_container"]]
    highlight_html = "<style> .st-key-KEY_REF button {color: COLOR_REF} .st-key-KEY_REF p {font-size: 1.05rem; font-weight: 700;} </style>"
    highlight_color = theme["highlight_text"]


    # Progress calculator feature
    st.html("<style>span.katex-display span.katex span.katex-html {font-size: 3rem; margin-top: -0.4rem;} </style>")
    # Feature details
    detail_pill_style = "<style>  .st-key-REF * {justify-content: center;} .st-key-REF button {flex: 1 1 110px; max-width: 160px;}</style>"
    for x in keylist_prog_calc:
        st.html(detail_pill_style.replace("REF", x))

    st.html("<style> .st-key-main_content {min-width: 1800px;} </style>")

    return registration_keys, prog_meter_keys, highlight_color, highlight_html, table_style


@st.dialog(f"Change theme", width="small")
def theme(themes):
    arciv = Archivist(DIRECTORIES, DATAPATH, "nofile")
    active_theme = themes["active"]
    _init(themes, active_theme)

    st.write(f"Select theme")
    col_left, col_right = st.columns([0.6, 0.4])
    active_theme = themes["active"]
    theme_options = list(themes.keys())
    theme_options.remove("active")
    active_option = theme_options.index(active_theme)
    with col_left:
        selected_theme = st.selectbox("themes", options=theme_options, key="set_theme", on_change=_reset_colors, args=(themes,), label_visibility="collapsed")
        # selected_theme = st.selectbox("themes", options=theme_options, index=active_option, key="set_theme", on_change=_reset_colors, args=(themes,), label_visibility="collapsed")
    with col_right:
        select_colors = st.checkbox("Edit theme", key="change_colors",  on_change=_reset_colors, args=(themes,))
    
    # color_keys = {
    #     "background": bgr_col,
    #     "feature_background": ip_col,
    #     "highlights": hl_col,
    #     "text_color": tx_col,
    #     "main_container": ft_col,
    #     "feature_header": hd_col,
    #     "sub_container": gr_col,
    #     "small_widget": sw_col
    # }
    
    col_1, col_2, col_3, col_4 = st.columns([0.6, 0.4, 0.6, 0.4])
    if select_colors:
        with st.container(horizontal_alignment="center"):

            # config
            st.html("<style> .st-key-bgr_col button {background-color: COLOR_REF; border-color: transparent;} </style>".replace("COLOR_REF", themes[active_theme]["background"]))
            col_1.button("Background", key="bgr_col", width="stretch")
            col_2.color_picker("Background", key="background", label_visibility="collapsed")
            
            # json
            st.html("<style> .st-key-ft_col button {background-color: COLOR_REF; border-color: transparent;} </style>".replace("COLOR_REF", themes[active_theme]["main_container"]))
            col_1.button("Feature", key="ft_col", width="stretch")
            col_2.color_picker("Feature", key="main_container", label_visibility="collapsed")
            
            # json
            st.html("<style> .st-key-hd_col button {background-color: COLOR_REF; border-color: transparent;} </style>".replace("COLOR_REF", themes[active_theme]["feature_header"]))
            col_1.button("Header", key="hd_col", width="stretch")
            col_2.color_picker("Header", key="feature_header", label_visibility="collapsed")
            
            # json
            st.html("<style> .st-key-gr_col button {background-color: COLOR_REF; border-color: transparent;} </style>".replace("COLOR_REF", themes[active_theme]["sub_container"]))
            col_1.button("Group", key="gr_col", width="stretch")
            col_2.color_picker("Group", key="sub_container", label_visibility="collapsed")
            
            # json
            st.html("<style> .st-key-sw_col button {background-color: COLOR_REF; border-color: transparent;} </style>".replace("COLOR_REF", themes[active_theme]["small_widget"]))
            col_3.button("Widget", key="sw_col", width="stretch")
            col_4.color_picker("Widget", key="small_widget", label_visibility="collapsed")
            
            # config
            st.html("<style> .st-key-hl_col button {background-color: transparent; color: COLOR_REF; border-color: COLOR_REF;} </style>".replace("COLOR_REF", themes[active_theme]["highlights"]))
            col_3.button("Highlights", key="hl_col", width="stretch")
            col_4.color_picker("Highlights", key="highlights", label_visibility="collapsed")
            
            # json
            st.html("<style> .st-key-hl_txt button {background-color: transparent; color: COLOR_REF; border-color: COLOR_REF;} </style>".replace("COLOR_REF", themes[active_theme]["highlight_text"]))
            col_3.button("Highlight text", key="hl_txt", width="stretch")
            col_4.color_picker("Highlight text", key="highlight_text", label_visibility="collapsed")
            
            # config
            st.html("<style> .st-key-tx_col button {color: COLOR_REF; border-color: transparent;} </style>".replace("COLOR_REF", themes[active_theme]["text_color"]))
            col_3.button("Text", key="tx_col", width="stretch")
            col_4.color_picker("Text", key="text_color", label_visibility="collapsed")

            # config
            st.html("<style> .st-key-ip_col button {background-color: COLOR_REF; border-color: transparent;} </style>".replace("COLOR_REF", themes[active_theme]["feature_background"]))
            col_3.button("Input", key="ip_col", width="stretch")
            col_4.color_picker("Input", key="feature_background", label_visibility="collapsed")


    st.space()
    col_1, col_2, col_3, col_4 = st.columns([1, 1, 1, 1])
    with st.container(width="stretch", horizontal_alignment="center"):
        if col_2.button("Apply", type="secondary", width="stretch"):
            st.session_state["show_theme_settings"] = True
            themes["active"] = selected_theme
            if select_colors:
                themes[selected_theme] = {
                    "background": st.session_state["background"],
                    "feature_background": st.session_state["feature_background"],
                    "highlights": st.session_state["highlights"],
                    "highlight_text": st.session_state["highlight_text"],
                    "text_color": st.session_state["text_color"],
                    "main_container": st.session_state["main_container"],
                    "feature_header": st.session_state["feature_header"],
                    "sub_container": st.session_state["sub_container"],
                    "small_widget": st.session_state["small_widget"]
                }
                config = f'[theme]\nbackgroundColor = "{st.session_state["background"]}"\nsecondaryBackgroundColor = "{st.session_state["feature_background"]}"\nprimaryColor = "{st.session_state["highlights"]}"\ntextColor = "{st.session_state["text_color"]}"\nfont = "sans serif"'
            else:
                config = f'[theme]\nbackgroundColor = "{themes[selected_theme]["background"]}"\nsecondaryBackgroundColor = "{themes[selected_theme]["feature_background"]}"\nprimaryColor = "{themes[selected_theme]["highlights"]}"\ntextColor = "{themes[selected_theme]["text_color"]}"\nfont = "sans serif"'
            st.session_state["theme_edited"] = time.time()
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


def _init(themes, active_theme):
    themes[active_theme]["background"]
    if "set_theme" not in st.session_state.keys():
        st.session_state["set_theme"] = active_theme
    if st.session_state["set_theme"] == active_theme:
        # print("theme")
        for cat, col in themes[active_theme].items():
            if cat not in st.session_state.keys():
                st.session_state[cat] = col
            # elif not st.session_state[cat]:
            #     st.session_state[cat] = col
    else:
        for cat, col in themes[st.session_state["set_theme"]].items():
            st.session_state[cat] = col


def _reset_colors(themes):
    # st.session_state["change_colors"] = False
    # print()
    for cat, col in themes[st.session_state["set_theme"]].items():
        st.session_state[cat] = col
        # print(col)