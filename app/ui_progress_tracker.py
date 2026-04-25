import streamlit as st

def progress_meter(component_key, sub_keys, arciv, negotiator, DATAPATH, TERMS, attempts): 
    height, html_label, html_add10 = _feature_style(component_key, attempts)

    # Header
    with st.container(key=f"{component_key}_head", width=1000, height=35):
        st.markdown(f"#### *{TERMS["Attempt"]}meter*", text_alignment="left")
    with st.container(border=True, key=f"{component_key}_main", width=1000, height=height):
        # Initiate keys for all widgets to-be-made and initiate their init value
        # It is run in a separate loop to avoid syncing delay or conflicts
        init_values = list()
        if "initiated" not in st.session_state.keys():
            st.session_state["initated"] = False
        if not st.session_state["initated"]:
            for i, category in enumerate(attempts.keys()):
                init_values, shared_init, label_key, state_key, slider_key, num_key, shared_key, button_key, add10_key = _initiate(TERMS, attempts, category, init_values, i)
                st.session_state.setdefault(shared_key, shared_init)
                st.session_state.setdefault(slider_key, shared_init)
                st.session_state.setdefault(num_key, shared_init)
            st.session_state["initated"] = True

        # Generate a widget for every category in file
        init_values = list()
        for i, category in enumerate(attempts.keys()):
            # Define the active key
            init_values, shared_init, label_key, state_key, slider_key, num_key, shared_key, button_key, add10_key = _initiate(TERMS, attempts, category, init_values, i)

            limit = attempts[category]["Limit"]
            
            with st.container(key=sub_keys[i]):
            
                col_state, col_cat, col_number, col_10, col_slider, col_apply = _column_style()
                with col_state:
                    is_static = False
                    is_active = None
                    # Indication only when applicable
                    if attempts[category]["State"]:
                        if attempts[category]["State"] == TERMS["StateRand"]:
                            symbol = ["**%**"]
                            # is_active = None
                            switch_to = TERMS["StateDet"]
                        else:
                            symbol = ["**☆**"]
                            is_active = symbol
                            switch_to = TERMS["StateRand"]
                        state_values = (arciv, negotiator, TERMS, DATAPATH, attempts, category, switch_to, TERMS["State"])
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
                        st.button(f"Save", key=button_key, type="primary", on_click=_update_progress, args=(arciv, negotiator, TERMS, DATAPATH, attempts, category, st.session_state[shared_key], TERMS["Attempt"]), width="stretch")
                    else:
                        st.button(f"Save", key=button_key, type="secondary", width="stretch")
        
        # Reset all values
        _reset_key = f"reset_key"
        col_apply = _column_style()[5]
        with col_apply:
            st.markdown("")
            st.button(f"**:green[Reset]**", key=_reset_key, type="secondary", on_click=_reset, args=(attempts, init_values, i), width="stretch")
        # st.markdown("")
        return height


def _feature_style(component_key, attempts):
    height = 55 * (len(attempts.keys()) - 0) + 65
    st.html("<style> .st-key-REF {min-width: 1000px;} </style>".replace("REF", component_key))
    html_label = "<style> .st-key-REF button {background-color: transparent; border: none;} </style>"
    html_add10 = "<style> .st-key-REF button {background-color: #2b272f; border: none; padding-left: -0.9rem;} </style>"
    return height, html_label, html_add10


def _initiate(TERMS, attempts, category, init_values, i):
    init_values.append(attempts[category][TERMS["Attempt"]])
    label_key = f"label_{i}"
    state_key = f"state_{i}"
    slider_key = f"slider_{i}"
    num_key = f"num_{i}"
    shared_key = f"val_{i}"
    button_key = f"but_{i}"
    add10_key = f"add10_{i}"
    
    shared_init = attempts[category][TERMS["Attempt"]]
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
    proggroup_column_size = [0.05, 0.22, 0.15, 0.06, 0.42, 0.08]
    return st.columns(proggroup_column_size, gap="xxsmall", vertical_alignment="center")


def _update_progress(arciv, negotiator, TERMS, DATAPATH, attempts, category, value, option):
    if option == TERMS["Attempt"]:
        attempts[category][TERMS["Attempt"]] = value
    elif option == TERMS["State"]:
        attempts[category][TERMS["State"]] = value

    if arciv.backup(negotiator, [101, 47, 19, 7], "progress_data", other_file=DATAPATH["Progress"]):
        arciv.writer(attempts, other_file=DATAPATH["Progress"], join_path="data")