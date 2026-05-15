import logging

import streamlit as st

from .file_manager import Archivist
import app.data_access as hold


logger = logging.getLogger(__name__)
logger.info("Loading progress_tracker")

DATAPATH = st.session_state["DATAPATH"]
DIRECTORIES = st.session_state["DIRECTORIES"]
SETTINGS = st.session_state["SETTINGS"]
TERMS = st.session_state["TERMS"]



attempt_ref = TERMS["attempt"]
progress_ref = TERMS["progress"]
state_ref = TERMS["state"]
staterand_ref = TERMS["state_rand"]
statedet_ref = TERMS["state_det"]



def progress_meter(component_key, sub_keys, feature_size_left, highlight_html): 
    logger.info("Running progress_tracker.progress_meter")

    arciv = Archivist(DIRECTORIES, DATAPATH, "nofile")
    attempts = hold.load_progress_data()
    active_theme = st.session_state["themes"]["active"]
    widget_color = st.session_state["themes"][active_theme]["input_field"]
    height, html_label, html_add10 = _feature_style(component_key, widget_color)

    if st.session_state["header_switch"]:
        with st.container(key=f"{component_key}_head", width=feature_size_left, height="content"):
            col_title, col_res = st.columns([23, 2])
            col_title.markdown(
                f"##### *{attempt_ref}meter*", 
                help=f"Indicate {staterand_ref} or {statedet_ref.lower()} by left-most icon. Press Save after changing any value to store it. Use Reset to restore all values , or to re-sync if all values are 0.", 
                text_alignment="left"
            )
    with st.container(border=True, key=f"{component_key}_main", width=feature_size_left, height=340):
        # Generate a widget for every category in file
        init_values = list()
        for i, category in enumerate(attempts.keys()):
            st.space("xxsmall")
            # Define a key for each widget and initiate their init value
            init_values, shared_init, keys = _initiate(attempts, category, init_values, i)

            limit = attempts[category]["limit"]
            with st.container(key=sub_keys[i]):
            
                col_state, col_cat, col_number, col_10, col_slider, col_apply = _column_style()
                with col_state:
                    is_static = False
                    is_active = None
                    # Indication only when applicable
                    if attempts[category][state_ref]:
                        if attempts[category][state_ref] == staterand_ref:
                            symbol = ["**%**"]
                            # is_active = None
                            switch_to = statedet_ref
                        else:
                            symbol = ["**☆**"]
                            is_active = symbol
                            switch_to = staterand_ref
                        state_values = (arciv, hold, attempts, category, switch_to, state_ref)
                    # Disable for static
                    else:
                        is_static = True
                        symbol = ["**⦸**"]
                        state_values = (None,)
                    st.pills(
                        "state", 
                        options=symbol, 
                        default=is_active, 
                        key=keys["state"], 
                        width="stretch", 
                        on_change=_update_progress, 
                        args=state_values, 
                        disabled=is_static, 
                        label_visibility="collapsed"
                    )
                
                # Category title
                label_style = html_label.replace("REF", keys["label"])
                st.html(label_style)
                with col_cat:
                    st.button(f"*{category}*", key=keys["label"], width="stretch") 
                
                # Enter number / change by increments
                # Syncs to slider
                with col_number:
                    st.number_input(
                        "Number", 
                        min_value=0, 
                        max_value=limit, 
                        key=keys["num"], 
                        on_change=_sync_from_num, 
                        args=(i,), 
                        label_visibility="collapsed"
                    )
                
                # Increase-by-10 button
                # Syncs to slider and number input
                add10_style = html_add10.replace("REF", keys["add10"])
                st.html(add10_style)
                with col_10:
                    if st.session_state[keys["num"]] < limit-10:
                        st.button(
                            "**+ 10**", 
                            key=keys["add10"], 
                            width="stretch", 
                            on_click=_increment_counter, 
                            args=(i,)
                        )
                    else:
                        st.button("**+ 10**", key=keys["add10"], width="stretch")
                
                # Slider view/interface
                # Syncs to number input
                with col_slider:
                    st.slider(
                        "Slider", 
                        min_value=0, 
                        max_value=limit, 
                        key=keys["slider"], 
                        on_change=_sync_from_slider, 
                        args=(i,), 
                        label_visibility="collapsed"
                    )
                # Apply and call save function
                with col_apply:
                    if st.session_state[keys["shared"]] != shared_init:
                        st.html(highlight_html.replace("KEY_REF", keys["button"]))
                        st.button(
                            f"Save", 
                            key=keys["button"], 
                            type="primary", 
                            on_click=_update_progress, 
                            args=(arciv, hold, attempts, category, st.session_state[keys["shared"]], 
                            attempt_ref), 
                            width="stretch"
                        )
                    else:
                        st.button(f"Save", key=keys["button"], type="secondary", width="stretch")
        
        # Reset all values
        reset_key = f"reset_key"
        with col_res:
            with st.container(border=False):
                st.markdown("")
                st.html("<style> .st-key-KEY_REF button * {color: COLOR_REF} .st-key-KEY_REF button {margin: -2rem 0rem;}</style>"
                        .replace("KEY_REF", reset_key)
                        .replace("COLOR_REF", st.session_state["positive_color"]))
                st.button("Reset", key=reset_key, type="tertiary", on_click=_reset, args=(attempts, init_values, i), width="stretch")
        # st.markdown("")
        return height
    
    
def _feature_style(component_key, widget_color):
    logger.info("Running progress_tracker._feature_style")

    height = 282
    st.html("<style> .st-key-REF {min-width: 1000px;} </style>".replace("REF", component_key))
    html_label = "<style> .st-key-REF button {background-color: transparent; border: none;} </style>"
    html_add10 = "<style> .st-key-REF button {background-color: COLOR_REF; border: none; padding-left: -0.9rem;} </style>".replace("COLOR_REF", widget_color)
    return height, html_label, html_add10


def _initiate(attempts, category, init_values, i):
    logger.info("Running progress_tracker._initiate")

    init_values.append(attempts[category][attempt_ref])
    keys = {
        "label": f"label_{i}",
        "state": f"state_{i}",
        "slider": f"slider_{i}",
        "num": f"num_{i}",
        "shared": f"val_{i}",
        "button": f"but_{i}",
        "add10": f"add10_{i}"
    }
    
    shared_init = attempts[category][attempt_ref]

    st.session_state.setdefault(keys["shared"], shared_init)
    st.session_state.setdefault(keys["slider"], shared_init)
    st.session_state.setdefault(keys["num"], shared_init)
    
    return init_values, shared_init, keys


def _sync_from_num(idx):
    logger.info("Running progress_tracker._sync_from_num")
    new_val = st.session_state[f"num_{idx}"]
    st.session_state[f"val_{idx}"] = new_val
    st.session_state[f"slider_{idx}"] = new_val

def _sync_from_slider(idx):
    logger.info("Running progress_tracker._sync_from_slider")
    new_val = st.session_state[f"slider_{idx}"]
    st.session_state[f"val_{idx}"] = new_val
    st.session_state[f"num_{idx}"] = new_val

def _increment_counter(idx, increment_value=10):
    logger.info("Running progress_tracker._increment_counter")
    st.session_state[f"val_{idx}"] += increment_value
    st.session_state[f"num_{idx}"] += increment_value 
    st.session_state[f"slider_{idx}"] += increment_value 

def _reset(attempts, init_values, idx): 
    logger.info("Running progress_tracker._reset")
    for i in range(len(attempts.keys())):
        st.session_state[f"val_{i}"], st.session_state[f"num_{i}"], st.session_state[f"slider_{i}"] = [init_values[i]]*3


def _column_style():
    logger.info("Running progress_tracker._column_style")
    proggroup_column_size = [0.05, 0.22, 0.15, 0.08, 0.42, 0.08]
    return st.columns(proggroup_column_size, gap="xxsmall", vertical_alignment="center")


def _update_progress(arciv, hold, attempts, category, value, option):
    logger.info("Running progress_tracker._update_progress")
    
    if option == attempt_ref:
        attempts[category][attempt_ref] = value
    elif option == state_ref:
        attempts[category][state_ref] = value

    arciv.catch_data(attempts, DATAPATH["progress"], progress_ref)
    if arciv.backup([101, 47, 19, 7, 3], progress_ref, other_file=DATAPATH["progress"]):
        arciv.writer(attempts, object_type=progress_ref, other_file=DATAPATH["progress"], join_path="data")
        st.session_state["cleared_cache"] = True
        hold.load_progress_data.clear()
        