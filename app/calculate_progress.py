"""
Interactive calculation assistant

Builds and manages:
- progress_display_value calculator interface
- input validation logic and processing
- result display of progress_display_value value
"""

import logging

import streamlit as st

import app.data_access as hold


logger = logging.getLogger(__name__)


def calculator(component_key: str, feature_width: int | str, 
               highlight_html: str, feature_height: int | str):
    """
    Render calculation assistant feature
    - compare progress_display_value states based on pages and rows
    - highlight ivalid combinations 
    - blocks impossible processing 
    - displays calculated result from valid input

    Args:
        component_key (str): 
            session state key for feature
    """
    logger.info("Running calculate_progress_display_value.calculator")
    st.error("test")

    # Feature header
    if st.session_state["header_switch"]:
        with st.container(
                key=f"{component_key}_head", 
                width=feature_width, height="content"):
            st.markdown("##### *Calculate*", text_alignment="left")

    # Main container
    with st.container(
            border=True, key=f"{component_key}_main", 
            width=feature_width, height=feature_height):

        # Evaluate validity of UI selection
        limit = hold.load_options()["value_limits"]["general_limit"]
        is_current_valid, is_previous_valid, msg, usertip_current, usertip_previous = _validation(limit)
        
        # Input field: UI structured as left for "current" and right for "previous"
        with st.container(horizontal_alignment="center"):
            num_columns = [3, 7, 7]
            num_width = 250

            # Group labels
            with st.container(width=num_width):
                col_label, col_left, col_right = st.columns(num_columns)
                with col_left:
                    st.markdown("*Current*", text_alignment="center")
                with col_right:
                    st.markdown("*Previous*", text_alignment="center")

            # Input page for "current" and "previous" event
            with st.container(width=num_width):
                col_label, col_left, col_right = st.columns(num_columns)
                with col_label:
                    st.button("*Page*", key="page_label", type="tertiary")
                with col_left:
                    st.selectbox(
                        "*Last event*", options=range(250)[1:], 
                        key="curr_page", label_visibility="collapsed")
                with col_right:
                    st.selectbox(
                        "*Previous event*", options=range(250)[1:], 
                        key="prev_page", label_visibility="collapsed")
                    
            # Input data row for latest and previous
            with st.container(width=num_width):
                curr_opt = range(6) if int(st.session_state["curr_page"]) == 1 else range(6)[1:]
                col_label, col_left, col_right = st.columns(num_columns)
                with col_label:
                    st.button("*Row*", key="row_label", type="tertiary")
                with col_left:
                    st.selectbox(
                        "Last event row", options=curr_opt, 
                        key="curr_row", label_visibility="collapsed")
                with col_right:
                    st.selectbox(
                        "Previous event row", options=range(6)[1:], 
                        key="prev_row", label_visibility="collapsed")
                st.space(5)

            # Field for submit and result
            # View settings depending on data validity
            if is_current_valid and is_previous_valid:
                st.html(highlight_html.replace("KEY_REF", "calc_button"))
                is_invalid, appearance = False, "primary"
            else:
                is_invalid, appearance = True, "secondary"
                st.session_state["calculation"] = None
            calc_columns = [0.2, 0.5, 0.2]
            left, mid, right = st.columns(calc_columns)

            # Submit button
            with mid:
                if st.button(
                    f"{msg}", 
                    key="calc_button", 
                    type=appearance, 
                    disabled=is_invalid, 
                    width="stretch"
                ):
                    output = _submit(
                        st.session_state["prev_page"], st.session_state["curr_page"],
                        st.session_state["prev_row"], st.session_state["curr_row"],
                        is_invalid)
                else:
                    output = None
                st.space(5)

            # Output viewer field 
            # - views tip for correcting data or result of calculation
            left, mid, right = st.columns(calc_columns)
            with mid:
                with st.container(
                    border=True, 
                    key="result_disp", 
                    width="stretch", 
                    height=60, 
                    horizontal_alignment="center", 
                    vertical_alignment="center"
                ):
                    html_output = """<div style=' font-size: 30px; margin: 0; padding: 0; 
                                line-height: 1; text-align: center;'>REF</div>"""
                    if output is not None:
                        result_output = f"-"
                        if output:
                            result_output = f"{output-1}"
                        st.html(html_output.replace("REF", result_output))
                    else:
                        if usertip_current: 
                            st.markdown(f"{usertip_current}", text_alignment="center")
                        elif usertip_previous: 
                            st.markdown(f"{usertip_previous}", text_alignment="center")
                        else:
                            st.html(html_output.replace("REF", "-"))


def _validation(limit: int) -> tuple:
    """
    Data validation for calculator input, checks
    - distance current-to-previous not exceeding project limit
    - logically possible row and page combinations

    Args:
        limit (int):
            Maximum allowed progress_display_value value from project settings
    
    Returns:
        Tuple (bool, bool, str, str, str):
            bools: current and previous validity  
            message string for button display  
            user tip strings for correcting input
    """

    msg = "Calculate"
    usertip_current = None
    usertip_previous = None
    is_current_valid = False

    # Conditions for current data
    if int(st.session_state["curr_row"]) == 5: 
        prev_page_min = int(st.session_state["curr_page"]) + 1
    else: 
        prev_page_min = int(st.session_state["curr_page"])

    # Comparing current data against previous data and conditions 
    # formats style highlights if needed
    if int(st.session_state["prev_page"]) < prev_page_min: 
        st.html(
            "<style> .st-key-curr_page * {color: COLOR_REF} </style>"
            .replace("COLOR_REF", st.session_state["negative_color"]))
        st.html(
            "<style> .st-key-curr_row * {color: COLOR_REF} </style>"
            .replace("COLOR_REF", st.session_state["negative_color"]))
        msg, usertip_current = "Out of range", "Page of last must be lower"
    elif int(st.session_state["curr_page"]) == int(st.session_state["prev_page"]): 
        if st.session_state["curr_row"] >= st.session_state["prev_row"]:
            st.html(
                "<style> .st-key-curr_row * {color: COLOR_REF} </style>"
                .replace("COLOR_REF", st.session_state["negative_color"]))
            msg, usertip_current = "Out of range", "Row of last must be lower"
        else:
            is_current_valid = True,
            usertip_current = None
    else:
        is_current_valid = True
        usertip_current = None
    is_previous_valid = False

    # A general limit is utilized, exceptions rare
    max_value = limit
    # Conditions for "current" data
    max_page = int(max_value/5 + int(st.session_state["curr_page"]))
    # Comparing "current" data against "previous" data and conditions 
    # formats style highlights if needed
    if "prev_page" in st.session_state.keys():
        if int(st.session_state["prev_page"]) > max_page:
            st.html("<style> .st-key-prev_page * {color: red} </style>")
            st.html("<style> .st-key-prev_row * {color: red} </style>")
            msg, usertip_previous = "Out of range", "Page of previous too high"
        elif int(st.session_state["prev_page"]) == max_page:
            if st.session_state["curr_row"] < st.session_state["prev_row"]:
                st.html("<style> .st-key-prev_row * {color: red} </style>")
                msg, usertip_previous = "Out of range", "Row of previous too high"
            else:
                is_current_valid = True
                usertip_previous = None
        else:
            is_previous_valid = True
            usertip_previous = None
    return is_current_valid, is_previous_valid, msg, usertip_current, usertip_previous


def _submit(prev_page: int, curr_page: int, 
            prev_row: int, curr_row: int, 
            is_invalid: bool) -> (int | None):
    """
    Calculate progress_display_value from validated selectbox input
    
    For valid input, calculates:  
    `Amount = 5⋅( [previous page] - [current page] ) 
            + [previous row] - [current row]`
    """

    if not is_invalid: 
        progress_display_value = 5*(prev_page - curr_page) + prev_row - curr_row
        return progress_display_value
    else:
        return None