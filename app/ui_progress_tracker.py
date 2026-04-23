import streamlit as st

def progress_meter(arciv, negotiator, DATAPATH, TERMS, attempts):
    st.markdown("""
        <style>
        [data-testid="stVerticalBlock"] > div {
            margin-top: -0.2rem;
            margin-bottom: -0.2rem;
        }
        """, unsafe_allow_html=True)

    instr = """
        <style>
        .st-key-XXX button {
            background-color: transparent;
            border: none;
        }
        </style>
    """

    instr2 = """
        <style>
        .st-key-XXX button {
            background-color: darkblue;
        }
        </style>
    """

    def update_progress(category, value, option):
        if option == TERMS["Attempt"]:
            attempts[category][TERMS["Attempt"]] = value
        elif option == TERMS["State"]:
            attempts[category][TERMS["State"]] = value
        # print(attempts)
        if arciv.backup(negotiator, [101, 47, 19, 7], "progress_data", other_file=DATAPATH["Progress"]):
            arciv.writer(attempts, other_file=DATAPATH["Progress"], join_path="data")
            
    def columns():
        return st.columns([0.07, 0.22, 0.15, 0.07, 0.42, 0.08], gap="xxsmall", vertical_alignment="center")

    # with col_main1:
    with st.container(width=1000, height=340):
        st.subheader(f"{TERMS["Attempt"]}", text_alignment="center")
        init_values = list()
        for i, category in enumerate(attempts.keys()):
            # print(i, category)

            label_key = f"label_{i}"
            state_key = f"state_{i}"
            slider_key = f"slider_{i}"
            num_key = f"num_{i}"
            shared_key = f"val_{i}"
            button_key = f"but_{i}"
            add10_key = f"add10_{i}"
            
            
            init_values.append(attempts[category][TERMS["Attempt"]])
            for x in [shared_key, num_key, slider_key]:
                if x not in st.session_state: 
                    st.session_state[x] = init_values[i]
                elif st.session_state[x] is None:
                    st.session_state[x] = init_values[i]
            # if shared_key not in st.session_state: st.session_state[shared_key] = init_values[i]
            # if num_key not in st.session_state: st.session_state[num_key] = st.session_state[shared_key]
            # if slider_key not in st.session_state: st.session_state[slider_key] = st.session_state[shared_key]

            def sync_from_num(idx=i):
                new_val = st.session_state[f"num_{idx}"]
                st.session_state[f"val_{idx}"] = new_val
                st.session_state[f"slider_{idx}"] = new_val

            def sync_from_slider(idx=i):
                new_val = st.session_state[f"slider_{idx}"]
                st.session_state[f"val_{idx}"] = new_val
                st.session_state[f"num_{idx}"] = new_val

            def increment_counter(idx=i, increment_value=10):
                st.session_state[f"val_{idx}"] += increment_value
                st.session_state[f"num_{idx}"] += increment_value 
                st.session_state[f"slider_{idx}"] += increment_value 

            
            def reset(idx=i):
                for i, category in enumerate(attempts.keys()):
                    st.session_state[f"val_{i}"], st.session_state[f"num_{i}"], st.session_state[f"slider_{i}"] = [init_values[i]]*3



            css = instr.replace("XXX", label_key)
            st.markdown(css, unsafe_allow_html=True)
            col_state, col_cat, col_number, col_10, col_slider, col_apply = columns()
            limit = attempts[category]["Limit"]
            with col_state:
                
                if attempts[category]["State"]:
                    is_static = False
                    if attempts[category]["State"] == TERMS["StateRand"]:
                        symbol = ["**%**"]
                        is_active = None
                        switch_to = TERMS["StateDet"]
                    else:
                        symbol = ["**☆**"]
                        is_active = symbol
                        switch_to = TERMS["StateRand"]
                    state_values = (category, switch_to, TERMS["State"])
                else:
                    is_static = True
                    symbol = ["**⦸**"]
                    state_values = (None,)
                st.pills("state", options=symbol, default=is_active, key=state_key, width="stretch", on_change=update_progress, args=state_values, disabled=is_static, label_visibility="collapsed")
            with col_cat:
                st.button(category, key=label_key)
            with col_number:
                st.number_input("Number", min_value=0, max_value=limit, key=num_key, on_change=sync_from_num, label_visibility="collapsed")
            with col_10:
                if st.session_state[shared_key] < limit-10:
                    st.button("**+ 10**", key=add10_key, width="stretch", on_click=increment_counter)
                else:
                    st.button("**+ 10**", key=add10_key, width="stretch")
            with col_slider:
                st.slider("Slider", min_value=0, max_value=limit, key=slider_key, on_change=sync_from_slider, label_visibility="collapsed")
            with col_apply:
                if st.session_state[shared_key] != init_values[i]:
                    st.button(f"Save", key=button_key, type="primary", on_click=update_progress, args=(category, st.session_state[shared_key], TERMS["Attempt"]), width="stretch")
                else:
                    st.button(f"Save", key=button_key, type="secondary", width="stretch")
        reset_key = f"reset_key"
        col_apply = columns()[5]
        
        with col_apply:
            st.markdown("")
            st.button(f"**:green[Reset]**", key=reset_key, type="secondary", on_click=reset, width="stretch")