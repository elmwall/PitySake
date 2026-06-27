"""
Tracker module for progress in all registered sources

Manages:
- automatic generation of keys and rendering of a progress subfeature per source
- collect, view and edit current progress within source
"""

import logging

import streamlit as st

import app.data_access as hold
import app.error_handler as error
from app.initialize import arciv


DATAPATH = st.session_state["DATAPATH"]
DIRECTORIES = st.session_state["DIRECTORIES"]
SETTINGS = st.session_state["SETTINGS"]
TERMS = st.session_state["TERMS"]
logger = logging.getLogger(__name__)
attempt_ref = TERMS["attempt"]
progress_ref = TERMS["progress"]
staterand_ref = TERMS["state_rand"]
statedet_ref = TERMS["state_det"]


def progress_meter(component_key: list, sub_keys: list, 
                   feature_size_left: str, highlight_html: str): 
    """
    Render progress tracker feature  
    - changes in attempts/progress in any source is managed here
    - visualizes sources with state and progress with individual save
    - syncing multiple modes of input

    Args:
        component_key (str):
            session state key for feature
        sub_keys (list):
            session state keys for subfeatures
    """
    logger.info("Running")

    # Feature header
    if st.session_state["header_switch"]:
        with st.container(
                key=f"{component_key}_head", 
                width=feature_size_left, height="content"):
            col_title, col_res = st.columns([23, 2])
            feature_help_text = f"""Indicate {TERMS["source"]} status by left-most icon.  
                Press Save after changing any value to store it.  
                Reset: restore all values, or re-sync if all values are 0.""" 
            col_title.markdown(
                f"##### *{attempt_ref} tracker*", 
                help=feature_help_text, text_alignment="left")
    else:
        col_title, col_res = st.columns([23, 2])
    # Main container
    with st.container(
            border=True, key=f"{component_key}_main", 
            width=feature_size_left, height=340):
        themes = st.session_state["themes"]
        theme_missing = st.session_state["theme_missing"]
        if not theme_missing:
            active_theme = themes["active"]
            widget_color = themes[active_theme]["input_field"]
        else:
            widget_color = ""

        state_rand_symbol = TERMS["state_rand_symbol"]
        state_det_symbol = TERMS["state_det_symbol"]
        if not theme_missing:
            active_theme_settings = themes[active_theme]
            highlight_color = active_theme_settings["highlights"]
            text_color = active_theme_settings["text_color"]
        else:
            highlight_color, text_color = [""]*2
        progress_data = hold.load_progress_data()
        reset_key = f"reset_key"
        height, html_label, html_add10 = _feature_style(component_key, widget_color, reset_key)
        
        # Generate a subfeature for every source category in file
        # Each utilizes a unique key generated in style module
        init_values = dict()
        accepted_trackers = list()
        active_trackers = st.session_state["active_trackers"]
        for i, category in enumerate(progress_data.keys()):
            # Per source:
            if any([category not in active_trackers,
                    progress_data[category][TERMS["attempt"]] is None]):
                continue
            else:
                accepted_trackers.append(i)
            st.space("xxsmall")
            # Define a key for each subfeature and initiate their init value
            init_values, shared_init, keys = _initiate(progress_data, category, init_values, i)
            options = hold.load_options()
            if not len(options) > 0:
                st.error("Critical option data missing.")
                return
            limit = options["source_limit"][category]
            state = progress_data[category]["State"]
            with st.container(key=sub_keys[i]):
                col_state, col_cat, col_number, col_10, col_slider, col_apply = _column_style()
                with col_state:
                    is_static = False
                    if not theme_missing:
                        color = text_color
                    else:
                        color = ""
                    # Indicate prognisis state of source
                    if state:
                        if state == staterand_ref:
                            symbol = f"**{state_rand_symbol}**"
                            switch_to = statedet_ref
                        elif state == statedet_ref:
                            symbol = f"**{state_det_symbol}**"
                            switch_to = staterand_ref
                            color = highlight_color
                        state_values = (progress_data, category, switch_to, "State")
                    # Disable state for static state sources
                    else:
                        is_static = True
                        symbol = "**⦸**"
                        state_values = (None,)
                    state_key = keys["state"]
                    st.html("""
                        <style>
                            .st-key-KEY_REF button {
                                border-radius: 30px;
                                border-color: COLOR_REF;
                                color: COLOR_REF;
                            }
                        </style>
                        """.replace("KEY_REF", state_key).replace("COLOR_REF", color))
                    st.button(
                        f"{symbol}", key=state_key, 
                        width="stretch", on_click=_update_progress, args=state_values, 
                        disabled=is_static)
                
                # Category title
                label_key = keys["label"]
                label_style = html_label.replace("REF", label_key)
                st.html(label_style)
                with col_cat:
                    st.button(f"*{category}*", key=label_key, width="stretch") 
                
                # Enter number / change by increments
                # Syncs to slider
                num_key = keys["num"]
                with col_number:
                    st.number_input(
                        "Number", min_value=0, max_value=limit, key=num_key, 
                        on_change=_sync_from_num, args=(accepted_trackers,), label_visibility="collapsed")
                
                # Increase-by-10 button
                # Syncs to slider and number input
                add10_key = keys["add10"]
                add10_style = html_add10.replace("REF", add10_key)
                st.html(add10_style)
                with col_10:
                    disable = st.session_state[num_key] > limit - 10
                    st.button(
                        "**+ 10**", key=add10_key, disabled=disable, width="stretch", 
                        on_click=_increment_counter, args=(init_values, accepted_trackers, i))
                
                # Slider view/interface
                # Syncs to number input
                with col_slider:
                    st.slider(
                        "Slider", min_value=0, max_value=limit, key=keys["slider"], 
                        on_change=_sync_from_slider, args=(accepted_trackers,), label_visibility="collapsed")
                # Apply and call save function
                shared_key = keys["shared"]
                shared_button_key = keys["button"]
                with col_apply:
                    if st.session_state[shared_key] != shared_init:
                        st.html(highlight_html.replace("KEY_REF", shared_button_key))
                        st.button(
                            f"Save", key=shared_button_key, type="primary", 
                            on_click=_update_progress, 
                            args=(
                                progress_data, category, 
                                st.session_state[shared_key], attempt_ref), 
                            width="stretch")
                    else:
                        st.button(f"Save", key=shared_button_key, type="secondary", width="stretch")
        # Reset all values
        with col_res:
            st.markdown("")
            st.button(
                "**Reset**", key=reset_key, type="tertiary", on_click=_reset, 
                args=(init_values, accepted_trackers), width="stretch")
        return height
    
    
def _feature_style(component_key: str, widget_color: str, reset_key:str):
    "Runs HTML/CSS settings for components"
    height = 282
    if not st.session_state["theme_missing"]:
        positive_color = st.session_state["positive_color"]
    else:
        positive_color = ""

    st.html("""
            <style> 
                .st-key-REF {min-width: 1000px;} 
            </style>"""
            .replace("REF", component_key))
    html_label = """
        <style> 
            .st-key-REF button {
                background-color: 
                transparent; border: none;
            } 
        </style>"""
    html_add10 = """
        <style> 
            .st-key-REF button {
                background-color: COLOR_REF; 
                border: none; 
                padding-left: -14.4px;
            } 
        </style>""".replace("COLOR_REF", widget_color)
    st.html("""
            <style> 
                .st-key-KEY_REF button * {color: COLOR_REF} 
                .st-key-KEY_REF button {margin: -32px 0px;}
            </style>"""
            .replace("KEY_REF", reset_key)
            .replace("COLOR_REF", positive_color))
    return height, html_label, html_add10


def _initiate(progress_data: dict, category: str, 
              init_values: dict, i: int):
    """
    Initiates unique keys for each input widget per source progress tracker.
    
    Args:
        progress_data (dict):
            database of progress in all sources
        category (str):
            identifier of current source to build tracker for
        init_values (dict):
            container to store earlier value of progress at corresponding index
        i (int):
            index for the current sub-feature to build
    """
    init_values[i] = progress_data[category][attempt_ref]
    keys = {
        "label": f"label_{i}",
        "state": f"state_{i}",
        "slider": f"slider_{i}",
        "num": f"num_{i}",
        "shared": f"val_{i}",
        "button": f"but_{i}",
        "add10": f"add10_{i}"
    }
    
    shared_init = progress_data[category][attempt_ref]

    st.session_state.setdefault(keys["shared"], shared_init)
    st.session_state.setdefault(keys["slider"], shared_init)
    st.session_state.setdefault(keys["num"], shared_init)
    
    return init_values, shared_init, keys


def _sync_from_num(accepted_trackers: list):
    "Syncs values from number input to slider."
    for idx in accepted_trackers:
        new_val = st.session_state[f"num_{idx}"]
        st.session_state[f"val_{idx}"] = new_val
        st.session_state[f"slider_{idx}"] = new_val

def _sync_from_slider(accepted_trackers: list):
    "Syncs values from slider to number input."
    for idx in accepted_trackers:
        new_val = st.session_state[f"slider_{idx}"]
        st.session_state[f"val_{idx}"] = new_val
        st.session_state[f"num_{idx}"] = new_val

def _increment_counter(init_values: dict, accepted_trackers: list, idx: int, increment_value: int = 10):
    "Syncs values from increment button to number input and slider."
    st.session_state[f"val_{idx}"] += increment_value
    st.session_state[f"num_{idx}"] += increment_value 
    st.session_state[f"slider_{idx}"] += increment_value 
    for i in accepted_trackers:
        if i != idx:
            st.session_state[f"val_{i}"] = init_values[i]
            st.session_state[f"num_{i}"] = init_values[i]
            st.session_state[f"slider_{i}"] = init_values[i]
        

def _reset(init_values: dict, accepted_trackers: list): 
    """Resets the values for all subfeatures to the current registered progress.
    
    Interates through indexes and updates session state 
    for shared value, number input, and slider
    """
    for i in accepted_trackers:
        st.session_state[f"val_{i}"] = init_values[i]
        st.session_state[f"num_{i}"] = init_values[i]
        st.session_state[f"slider_{i}"] = init_values[i]


def _column_style():
    "Standardized column size for each subfeature."
    proggroup_column_size = [0.05, 0.22, 0.15, 0.08, 0.42, 0.08]
    return st.columns(
        proggroup_column_size, gap="xxsmall", vertical_alignment="center")


def _update_progress(progress_data: dict, category: str, 
                     attempt_value: int, option: str):
    """
    Saves updated progress or state values in progress database.

    Args:
        progress_data (dict):
            progress database
        category (str):
            source to be updated
        attempt_value (int):
            new value for progress in source
        option (str):
            sets progress or state to be updated
    """    
    if option == attempt_ref:
        progress_data[category][attempt_ref] = attempt_value
    elif option == "State":
        progress_data[category]["State"] = attempt_value
    file = DATAPATH["progress"]
    logger.info(f"Update called for {file}")
    error.catch_data(progress_data, file, progress_ref)
    if arciv.backup(
            [101, 47, 19, 7, 3], progress_ref, 
            set_file=file, empty_allowed=True):
        arciv.writer(
            progress_data, object_type=progress_ref, 
            set_file=file, join_path="data")
        st.session_state["cleared_cache"] = True
        hold.load_progress_data.clear()
        