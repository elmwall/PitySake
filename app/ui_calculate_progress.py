import streamlit as st

def calculator(limit, component_key, height):
    _initiate()
    # Header
    with st.container(key=f"{component_key}_head", height=35):
        st.markdown("#### *Calculate*", text_alignment="left")
    # Main container
    with st.container(border=True, key=f"{component_key}_main", height="stretch"):
        curr_valid, prev_valid, msg = _validation(limit)
        st.markdown("")
        # Input field, UI structured as left for latest and right for previous
        with st.container():
            num_columns = [3, 3, 3]
            # Group labels
            with st.container():
                col_label, col_left, col_right = st.columns(num_columns)
                with col_left:
                    st.markdown("*Last*", text_alignment="center")
                with col_right:
                    st.markdown("*Previous*", text_alignment="center")
            # Input page for latest and previous
            with st.container(vertical_alignment="center"):
                col_label, col_left, col_right = st.columns(num_columns)
                with col_label:
                    st.button("*Page*", key="page_label", type="tertiary")
                with col_left:
                    st.selectbox("*Last event*", options=range(250)[1:], key="curr_page", label_visibility="collapsed")
                with col_right:
                    st.selectbox("*Previous event*", options=range(250)[1:], key="prev_page", label_visibility="collapsed")
            st.markdown("")
            # Input data row for latest and previous
            with st.container(vertical_alignment="center"):
                col_label, col_left, col_right = st.columns(num_columns)
                with col_label:
                    st.button("*Row*", key="row_label", type="tertiary")
                with col_left:
                    st.selectbox("Last event row", options=range(6)[1:], key="curr_row", label_visibility="collapsed")
                with col_right:
                    st.selectbox("Previous event row", options=range(6)[1:], key="prev_row", label_visibility="collapsed")      
                    st.markdown(f"")
            st.markdown("")

            # Field for submit and result
            # View settings depending on data validity
            if curr_valid and prev_valid:
                invalid, appearance = False, "primary"
            else:
                invalid, appearance = True, "secondary"
                st.session_state["calculation"] = None
            calc_columns = [0.2, 0.5, 0.2]
            left, mid, right = st.columns(calc_columns)
            # Submit button
            with mid:
                if st.button(f"{msg}", key="caculation", type=appearance, disabled=invalid, width="stretch"):
                    st.session_state["calculation"] = _submit(
                        st.session_state["prev_page"],
                        st.session_state["curr_page"],
                        st.session_state["prev_row"],
                        st.session_state["curr_row"],
                        invalid
                    )
            # Output viewer field - views tip for correcting data or result of calculation
            if st.session_state["calculation"] is not None:
                left, mid, right = st.columns(calc_columns)
                if st.session_state["calculation"]:
                    st.latex(f"{st.session_state["calculation"]-1}", width="stretch")
                else:
                    st.latex(f"{3}", width="stretch")
            else:
                with mid:
                    st.button(f"{st.session_state["message"]}", key="display_msg", type="tertiary", width="stretch")


def _initiate():
    init_values = {
        "curr_page": 1, 
        "curr_row": 1, 
        "prev_page": 1, 
        "prev_row": 2,
        "message": "",
        "calculation": None
    }
    for key, value in init_values.items():
        if key not in st.session_state.keys():
            st.session_state[key] = value
        elif not st.session_state[key]:
            st.session_state[key] = value


def _validation(limit):
    """
    Checks data for incompatible values and adjusts message, highlighting and control bools
    """
    msg = "Calculate"
    curr_valid = False
    # Conditions for latest data
    if int(st.session_state["curr_row"]) == 5: 
        prev_page_min = int(st.session_state["curr_page"]) + 1
    else: 
        prev_page_min = int(st.session_state["curr_page"])
    # Comparing latest data against previous data and conditions and highlights errors
    if int(st.session_state["prev_page"]) < prev_page_min: 
        st.html("<style> .st-key-curr_page * {color: red} </style>")
        st.html("<style> .st-key-curr_row * {color: red} </style>")
        msg, st.session_state["message"] = "Out of range", "Page of new must come after the previous"
    elif int(st.session_state["curr_page"]) == int(st.session_state["prev_page"]): 
        if st.session_state["curr_row"] >= st.session_state["prev_row"]:
            st.html("<style> .st-key-curr_row * {color: red} </style>")
            msg, st.session_state["message"] = "Out of range", "Row of new must come after the previous"
        else:
            curr_valid = True,
            st.session_state["message"] = ""
    else:
        curr_valid = True
        st.session_state["message"] = ""
    prev_valid = False
    # A general limit is utilized, exceptions rare
    max_value = limit
    # Conditions for latest data
    max_page = int(max_value/5 + int(st.session_state["curr_page"]))
    # Comparing latest data against previous data and conditions and highlights errors
    if "prev_page" in st.session_state.keys():
        if int(st.session_state["prev_page"]) > max_page:
            st.html("<style> .st-key-prev_page * {color: red} </style>")
            st.html("<style> .st-key-prev_row * {color: red} </style>")
            msg, st.session_state["message"] = "Out of range", "Page of previous event is too high"
        elif int(st.session_state["prev_page"]) == max_page:
            if st.session_state["curr_row"] < st.session_state["prev_row"]:
                st.html("<style> .st-key-prev_row * {color: red} </style>")
                msg, st.session_state["message"] = "Out of range", "Row of previous event is too high"
            else:
                curr_valid = True
                st.session_state["message"] = ""
        else:
            prev_valid = True
            st.session_state["message"] = ""
    return curr_valid, prev_valid, msg


def _submit(prev_page, curr_page, prev_row, curr_row, invalid):
    if not invalid: 
        event_plus1 = 5*(prev_page - curr_page) + prev_row - curr_row
        return event_plus1
    else:
        return None