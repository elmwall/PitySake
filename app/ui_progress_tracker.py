import streamlit as st

from .file_manager import Archivist
from .data_access import Holder

from settings.config import TERMS, DIRECTORIES, DATAPATH


def progress_meter(attempts, component_key, sub_keys, feature_size_left, widget_color, highlight_textstyle, highlight_html): 
    hold = Holder()
    attempts = hold.load_progress_data()
    
    height, html_label, html_add10 = _feature_style(component_key, attempts, widget_color)
    arciv = Archivist(DIRECTORIES, DATAPATH, "nofile")
    # Header
    with st.container(key=f"{component_key}_head", width=feature_size_left, height="content"):
        st.markdown(f"##### *{TERMS["attempt"]}meter*", text_alignment="left")
    with st.container(border=True, key=f"{component_key}_main", width=feature_size_left, height="stretch"):
        # Initiate keys for all widgets to-be-made and initiate their init value
        # It is run in a separate loop to avoid syncing delay or conflicts
        init_values = list()
        if "initiated" not in st.session_state.keys():
            st.session_state["initated"] = False
        if not st.session_state["initated"]:
            for i, category in enumerate(attempts.keys()):
                init_values, shared_init, label_key, state_key, slider_key, num_key, shared_key, button_key, add10_key = _initiate(attempts, category, init_values, i)
                st.session_state.setdefault(shared_key, shared_init)
                st.session_state.setdefault(slider_key, shared_init)
                st.session_state.setdefault(num_key, shared_init)
            st.session_state["initated"] = True

        # Generate a widget for every category in file
        init_values = list()
        for i, category in enumerate(attempts.keys()):
            # Define the active key
            init_values, shared_init, label_key, state_key, slider_key, num_key, shared_key, button_key, add10_key = _initiate(attempts, category, init_values, i)

            limit = attempts[category]["limit"]
            # st.html("<style> .st-key-KEY_REF {padding: 0.7rem} </style>".replace("KEY_REF", sub_keys[i]))
            # st.html("<style> .st-key-KEY_REF {margin: 0.5rem} </style>".replace("KEY_REF", add10_key))
            with st.container(key=sub_keys[i]):
            
                col_state, col_cat, col_number, col_10, col_slider, col_apply = _column_style()
                with col_state:
                    is_static = False
                    is_active = None
                    # Indication only when applicable
                    if attempts[category][TERMS["state"]]:
                        if attempts[category][TERMS["state"]] == TERMS["state_rand"]:
                            symbol = ["**%**"]
                            # is_active = None
                            switch_to = TERMS["state_det"]
                        else:
                            symbol = ["**☆**"]
                            is_active = symbol
                            switch_to = TERMS["state_rand"]
                        state_values = (arciv, hold, attempts, category, switch_to, TERMS["state"])
                    # Disable for static
                    else:
                        is_static = True
                        symbol = ["**⦸**"]
                        state_values = (None,)
                    st.pills("state", options=symbol, default=is_active, key=state_key, width="stretch", on_change=_update_progress, args=state_values, disabled=is_static, label_visibility="collapsed")
                
                # Category title
                label_style = html_label.replace("REF", label_key)
                st.html(label_style)
                with col_cat:
                    st.button(f"*{category}*", key=label_key, width="stretch") 
                
                # Enter number / change by increments
                # Syncs to slider
                with col_number:
                    st.number_input("Number", min_value=0, max_value=limit, key=num_key, on_change=_sync_from_num, args=(i,), label_visibility="collapsed")
                
                # Increase-by-10 button
                # Syncs to slider and number input
                add10_style = html_add10.replace("REF", add10_key)
                st.html(add10_style)
                with col_10:
                    if st.session_state[num_key] < limit-10:
                        st.button("**+ 10**", key=add10_key, width="stretch", on_click=_increment_counter, args=(i,))
                    else:
                        st.button("**+ 10**", key=add10_key, width="stretch")
                
                # Slider view/interface
                # Syncs to number input
                with col_slider:
                    st.slider("Slider", min_value=0, max_value=limit, key=slider_key, on_change=_sync_from_slider, args=(i,), label_visibility="collapsed")
                # Apply and call save function
                with col_apply:
                    if st.session_state[shared_key] != shared_init:
                        st.html(highlight_html.replace("KEY_REF", button_key).replace("COLOR_REF", highlight_textstyle))
                        st.button(f"Save", key=button_key, type="primary", on_click=_update_progress, args=(arciv, hold, attempts, category, st.session_state[shared_key], TERMS["attempt"]), width="stretch")
                    else:
                        st.button(f"Save", key=button_key, type="secondary", width="stretch")
        
        # Reset all values
        reset_key = f"reset_key"
        col_apply = _column_style()[5]
        with col_apply:
            st.markdown("")
            st.button(f"**:green[Reset]**", key=reset_key, type="secondary", on_click=_reset, args=(attempts, init_values, i), width="stretch")
        # st.markdown("")
        return height


def _feature_style(component_key, attempts, widget_color):
    height = 55 * (len(attempts.keys()) - 0) + 65
    st.html("<style> .st-key-REF {min-width: 1000px;} </style>".replace("REF", component_key))
    html_label = "<style> .st-key-REF button {background-color: transparent; border: none;} </style>"
    html_add10 = "<style> .st-key-REF button {background-color: COLOR_REF; border: none; padding-left: -0.9rem;} </style>".replace("COLOR_REF", widget_color)
    return height, html_label, html_add10


def _initiate(attempts, category, init_values, i):
    init_values.append(attempts[category][TERMS["attempt"]])
    label_key = f"label_{i}"
    state_key = f"state_{i}"
    slider_key = f"slider_{i}"
    num_key = f"num_{i}"
    shared_key = f"val_{i}"
    button_key = f"but_{i}"
    add10_key = f"add10_{i}"
    
    shared_init = attempts[category][TERMS["attempt"]]
    return init_values, shared_init, label_key, state_key, slider_key, num_key, shared_key, button_key, add10_key


def _sync_from_num(idx):
    new_val = st.session_state[f"num_{idx}"]
    st.session_state[f"val_{idx}"] = new_val
    st.session_state[f"slider_{idx}"] = new_val
def _sync_from_slider(idx):
    new_val = st.session_state[f"slider_{idx}"]
    st.session_state[f"val_{idx}"] = new_val
    st.session_state[f"num_{idx}"] = new_val
def _increment_counter(idx, increment_value=10):
    st.session_state[f"val_{idx}"] += increment_value
    st.session_state[f"num_{idx}"] += increment_value 
    st.session_state[f"slider_{idx}"] += increment_value 
def _reset(attempts, init_values, idx): 
    for i in range(len(attempts.keys())):
        st.session_state[f"val_{i}"], st.session_state[f"num_{i}"], st.session_state[f"slider_{i}"] = [init_values[i]]*3


def _column_style():
    proggroup_column_size = [0.05, 0.22, 0.15, 0.08, 0.42, 0.08]
    return st.columns(proggroup_column_size, gap="xxsmall", vertical_alignment="center")


def _update_progress(arciv, hold, attempts, category, value, option):
    if option == TERMS["attempt"]:
        attempts[category][TERMS["attempt"]] = value
    elif option == TERMS["state"]:
        attempts[category][TERMS["state"]] = value

    arciv.catch_data(attempts, DATAPATH["progress"], TERMS["progress"])
    if arciv.backup([101, 47, 19, 7, 3], TERMS["progress"], other_file=DATAPATH["progress"]):
        arciv.writer(attempts, object_type=TERMS["progress"], other_file=DATAPATH["progress"], join_path="data")
        hold.load_progress_data.clear()
        