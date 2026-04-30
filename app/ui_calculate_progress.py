import streamlit as st

def calculator(limit, component_key, height, highlight_textstyle, highlight_html):
    _initiate()
    # Header
    with st.container(key=f"{component_key}_head", height="content"):
        st.markdown("##### *Calculate*", text_alignment="left")
    # Main container
    with st.container(border=True, key=f"{component_key}_main", height="stretch"):
        curr_valid, prev_valid, msg, tip_last, tip_prev = _validation(limit)
        st.markdown("")
        # Input field, UI structured as left for latest and right for previous
        with st.container(horizontal_alignment="center",):
            num_columns = [3, 7, 7]
            num_width = 250
            # Group labels
            with st.container(width=num_width):
                col_label, col_left, col_right = st.columns(num_columns)
                with col_left:
                    st.markdown("*Last*", text_alignment="center")
                with col_right:
                    st.markdown("*Previous*", text_alignment="center")
            # Input page for latest and previous
            with st.container(width=num_width):
                col_label, col_left, col_right = st.columns(num_columns)
                with col_label:
                    st.button("*Page*", key="page_label", type="tertiary")
                with col_left:
                    st.selectbox("*Last event*", options=range(250)[1:], key="curr_page", label_visibility="collapsed")
                with col_right:
                    st.selectbox("*Previous event*", options=range(250)[1:], key="prev_page", label_visibility="collapsed")
            st.markdown("")
            # Input data row for latest and previous
            with st.container(width=num_width):
                curr_opt = range(6) if int(st.session_state["curr_page"]) == 1 else range(6)[1:]
                col_label, col_left, col_right = st.columns(num_columns)
                with col_label:
                    st.button("*Row*", key="row_label", type="tertiary")
                with col_left:
                    st.selectbox("Last event row", options=curr_opt, key="curr_row", label_visibility="collapsed")
                with col_right:
                    st.selectbox("Previous event row", options=range(6)[1:], key="prev_row", label_visibility="collapsed")      
                    st.markdown(f"")
            st.markdown("")

            # Field for submit and result
            # View settings depending on data validity
            if curr_valid and prev_valid:
                st.html(highlight_html.replace("KEY_REF", "calc_button").replace("COLOR_REF", highlight_textstyle))
                invalid, appearance = False, "primary"
            else:
                invalid, appearance = True, "secondary"
                st.session_state["calculation"] = None
            calc_columns = [0.2, 0.5, 0.2]
            left, mid, right = st.columns(calc_columns)
            # Submit button
            with mid:
                if st.button(f"{msg}", key="calc_button", type=appearance, disabled=invalid, width="stretch"):
                    output = _submit(
                        st.session_state["prev_page"],
                        st.session_state["curr_page"],
                        st.session_state["prev_row"],
                        st.session_state["curr_row"],
                        invalid
                    )
                else:
                    output = None
            # Output viewer field - views tip for correcting data or result of calculation
            # st.html("<style> .st-key-result_disp {margin: 0 0; padding: 0} .st-key-result_disp * {margin: 0; padding: 0; text-align: center} </style>")
            # st.space("xxsmall")
            left, mid, right = st.columns(calc_columns)
            with mid:
                with st.container(border=True, key="result_disp", width="stretch", height="stretch", horizontal_alignment="center", vertical_alignment="center"):
                    html_output = "<div style='font-size: 50px; margin: 0; padding: 0; line-height: 1; text-align: center;'>REF</div>"
                    if output is not None:
                        result_output = f"-"
                        if output:
                            result_output = f"{output-1}"
                        st.html(html_output.replace("REF", result_output))
                    else:
                        if tip_last: 
                            st.markdown(f"{tip_last}", text_alignment="center")
                        elif tip_prev: 
                            st.markdown(f"{tip_prev}", text_alignment="center")
                        else:
                            st.html(html_output.replace("REF", "-"))



def _initiate():
    init_values = {
        "curr_page": 1, 
        "curr_row": 0, 
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
    tip_last = None
    tip_prev = None
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
        msg, tip_last = "Out of range", "Page of last must be lower"
    elif int(st.session_state["curr_page"]) == int(st.session_state["prev_page"]): 
        if st.session_state["curr_row"] >= st.session_state["prev_row"]:
            st.html("<style> .st-key-curr_row * {color: red} </style>")
            msg, tip_last = "Out of range", "Row of last must be lower"
        else:
            curr_valid = True,
            tip_last = None
    else:
        curr_valid = True
        tip_last = None
    # if int(st.session_state["curr_page"]) 
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
            msg, tip_prev = "Out of range", "Page of previous too high"
        elif int(st.session_state["prev_page"]) == max_page:
            if st.session_state["curr_row"] < st.session_state["prev_row"]:
                st.html("<style> .st-key-prev_row * {color: red} </style>")
                msg, tip_prev = "Out of range", "Row of previous too high"
            else:
                curr_valid = True
                tip_prev = None
        else:
            prev_valid = True
            tip_prev = None
    return curr_valid, prev_valid, msg, tip_last, tip_prev


def _submit(prev_page, curr_page, prev_row, curr_row, invalid):
    if not invalid: 
        event_plus1 = 5*(prev_page - curr_page) + prev_row - curr_row
        return event_plus1
    else:
        return None