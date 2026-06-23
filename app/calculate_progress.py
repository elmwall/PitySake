"""
Interactive calculation assistant

Builds and manages:
- progress_display_value calculator interface
- input validation logic and processing
- result display of progress_display_value value
- edit dialog box to define and save equal/variable sets per source
"""

import logging

import streamlit as st

import app.data_access as hold
import app.error_handler as error
from app.initialize import arciv


TERMS = st.session_state["TERMS"]
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
    logger.info("Running")

    if feature_width is None: feature_width = "stretch"
    if feature_height is None: feature_height = "stretch"
    # Feature header 
    if st.session_state["header_switch"]:
        with st.container(
                key=f"{component_key}_head",
                width=feature_width, height="content"):
            feature_help = f"""Calculate {TERMS["attempt"].lower()} from events.  
            Select a {TERMS["source"].lower()} to define sections and max limit."""
            st.markdown("##### *Calculate*", help=feature_help, text_alignment="left")

    # Main container
    with st.container(
            border=True, key=f"{component_key}_main", 
            width=feature_width, height=feature_height):

        for x in ["page_range", "row_range"]:
            if x not in st.session_state: _page_sets()
        # Evaluate validity of UI selection
        with st.container(horizontal_alignment="center"):
            # Select pages setts for calculation
            # Each progress tracking source has defined sets
            set_options = list(hold.load_progress_data().keys())
            col_select, col_define = st.columns([3, 2.5])

            col_select.selectbox(
                f"Select {TERMS["source"]}", options=set_options, 
                key="select_set", on_change=_page_sets, label_visibility="collapsed")
            # Empty field placeholder
            set_help = """Create custom sets by defining the  
                number of sections and positions per section."""
            if col_define.button(
                "Define sets", help=set_help, type="secondary", width="stretch"):
                _define_sets()
            col_define.checkbox(
                "Start from 1", value=False, key="start_at_1", 
                help="""When enabled, begins count from 1 instead of 0  
                for the first position after the start event.""")
            st.space(5)
            no_limit = True
            if st.session_state["select_set"]:
                options = hold.load_options()
                if len(options) > 0:
                    limit = options["source_limit"][st.session_state["select_set"]]
                else:
                    limit = 0
                no_limit = False
            
            # Value selector field: Enter values for calculation
            # UI structured as left for "current" and right for "previous"
            msg, appearance = "Lacking sets", "secondary"
            usertip_current, usertip_previous = "", ""
            col_left, col_right, col_label = st.columns([5, 5, 7])
            _value_selector(col_left, col_right, col_label, no_limit)
            # Field for submit and result
            if not no_limit:
                is_current_valid, is_previous_valid, msg, usertip_current, usertip_previous = _validation(limit)

                # View settings depending on data validity
                if is_current_valid and is_previous_valid:
                    st.html(highlight_html.replace("KEY_REF", "calc_button"))
                    is_invalid, appearance = False, "primary"
                else:
                    is_invalid, appearance = True, "secondary"
                    st.session_state["calculation"] = None
            else:
                is_invalid = True
            # Submit button
            if col_label.button(
                    f"{msg}", key="calc_button", type=appearance, 
                    disabled=is_invalid, width="stretch"):
                output = _submit(
                    st.session_state["prev_page"], st.session_state["curr_page"],
                    st.session_state["prev_row"], st.session_state["curr_row"],
                    is_invalid)
            else:
                output = None
            # Output viewer field 
            # - views tip for correcting data or result of calculation
            _result_viewer(col_label, output, usertip_current, usertip_previous)


def _page_sets():
    """
    Update pages (sets) and rows (positions), and define ranges depending on case.
    - Uniform page-row sets are defined by a dict with corresponding keys.  
    - Pages with varying rows are defined by a list. 
        The length sets no. of pages while value at indices sets no. of rows.
    """
    st.session_state["curr_page"]
    st.session_state["prev_page"]
    st.session_state["curr_row"]
    st.session_state["prev_row"]
    progress_data = hold.load_progress_data()
    set_options = list(progress_data.keys())
    if len(set_options) > 0:
        if "select_set" not in st.session_state:
            st.session_state["select_set"] = set_options[0]
        st.session_state["sets"] = progress_data[st.session_state["select_set"]]["sets"]
        # Uniform page-row
        if type(st.session_state["sets"]) is dict:
            st.session_state["page_range"] = range(st.session_state["sets"]["pages"] + 1)[1:]
            st.session_state["row_range"] = st.session_state["sets"]["rows"]
        # Varying page-row
        # The list of pages is corrected to show list starting from 1
        # since lists starts with index 0
        elif type(st.session_state["sets"]) is list:
            st.session_state["row_range"] = st.session_state["sets"]
            st.session_state["page_range"] = range(len(st.session_state["row_range"]) + 1)[1:]
    else:
        st.session_state["sets"] = None


def _value_selector(col_left, col_right, col_label, no_limit: bool):
    """
    Selectboxes selecting start and stop page (set) and row (position).

    Args:
        col_left (DeltaGenerator):
            Streamlit column instance
        col_right (DeltaGenerator):
            Streamlit column instance
        col_label (DeltaGenerator):
            Streamlit column instance
        no_limit (bool):
            control value to disable selection if no source is set
    """
    # Group labels
    col_left.markdown("*Start*", text_alignment="center")
    col_right.markdown("*Stop*", text_alignment="center")
    calculator_help = """- Top: section number   
Bottom: position within section  
- Select a section and a position for both start and end events.  
The calculation traverses all intermediate sections and returns the total value."""
    col_label.markdown(" ", help=calculator_help)
    if st.session_state["sets"]:
        # Input page (set) for start and stop event
        page_range = st.session_state["page_range"]
        row_range = st.session_state["row_range"]
    else:
        page_range, row_range = 0, 0
    col_left.selectbox(
        "Current", options=page_range, 
        key="curr_page", disabled=no_limit, label_visibility="collapsed")
    col_right.selectbox(
        "Previous", options=page_range, 
        key="prev_page", disabled=no_limit, label_visibility="collapsed")
            
    # Input data row (position) for start and event
    if type(row_range) is int:
        row_range += 1
        prev_opt = range(row_range)[1:]
        curr_opt = range(row_range) if int(st.session_state["curr_page"]) == 1 else range(row_range)[1:]
    elif type(row_range) is list:
        prev_opt = range(row_range[st.session_state["prev_page"] - 1] + 1)[1:]
        if int(st.session_state["curr_page"]) == 1:
            curr_opt = range(row_range[st.session_state["curr_page"] - 1] + 1)
        else:
            curr_opt = range(row_range[st.session_state["curr_page"] - 1] + 1)[1:]

    with col_left:
        st.selectbox(
            "Last event row", options=curr_opt, index=0,
            key="curr_row", disabled=no_limit, label_visibility="collapsed")
    with col_right:
        st.selectbox(
            "Previous event row", options=prev_opt, 
            key="prev_row", disabled=no_limit, label_visibility="collapsed")


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
    start_value = 1 if st.session_state["start_at_1"] else 0

    # Conditions for current data
    if type(st.session_state["sets"]) is list:
        row_range = st.session_state["row_range"][st.session_state["curr_row"]]
    elif type(st.session_state["sets"]) is dict:
        row_range = st.session_state["row_range"]
    if st.session_state["curr_row"] == row_range: 
        prev_page_min = st.session_state["curr_page"] + 1
    else: 
        prev_page_min = st.session_state["curr_page"]
    # Comparing current data against previous data and conditions 
    # formats style highlights if needed
    if st.session_state["prev_page"] < prev_page_min: 
        st.html(
            "<style> .st-key-curr_page * {color: COLOR_REF} </style>"
            .replace("COLOR_REF", st.session_state["negative_color"]))
        msg = "Out of range"
        if st.session_state["curr_page"] == st.session_state["prev_page"]:
            st.html(
                "<style> .st-key-curr_row * {color: COLOR_REF} </style>"
                .replace("COLOR_REF", st.session_state["negative_color"]))
            usertip_current = "Invalid selections. Start is at the last position, stop section must then be greater."
        else:
            usertip_current = "Invalid sections. Start section number cannot be higher than stop section."
    elif st.session_state["curr_page"] == st.session_state["prev_page"]:
        if st.session_state["prev_row"] <= st.session_state["curr_row"]:
            st.html(
                "<style> .st-key-curr_row * {color: COLOR_REF} </style>"
                .replace("COLOR_REF", st.session_state["negative_color"]))
            msg, usertip_current = "Out of range", "Invalid positions. Within the same section, start position must be less than stop position."
        else:
            is_current_valid = True
            usertip_current = None
    else:
        is_current_valid = True
        usertip_current = None

    max_page, max_row = None, None
    # Conditions for "previous" data
    if type(st.session_state["sets"]) is list:
        pages = len(st.session_state["sets"])
        idx = st.session_state["curr_page"] - 1
        val = start_value + st.session_state["sets"][idx] - st.session_state["curr_row"]
        while idx < pages:
            idx += 1
            # Loop until last page then set max beyond, i.e. no limit within range
            if idx + 1 == pages:
                max_page = idx + 1
                max_row = limit - val + 1
                break
            # If the upcoming page exceeds limit, set max page and row from here
            elif val + st.session_state["sets"][idx] > limit:
                max_page = idx + 1
                max_row = limit - val + 1
                break
            # Within limits, add value of whole pages
            else:
                val += st.session_state["sets"][idx]
    elif type(st.session_state["sets"]) is dict:
        rows = st.session_state["sets"]["rows"]
        # Max row is set from:
        #   rows * int(int(limit / rows) - 1): the value corresponding to all whole pages
        #   rows - st.session_state["curr_row"]: the value from the current page start row
        #   - 1: the counter starts from 0, i.e. the first row is 0, then each row gives +1
        max_row = limit - rows * int(int(limit / rows) - 1) - int(rows - st.session_state["curr_row"] - 1) - start_value
        if max_row > row_range:
            page_increase = 1
            max_row = 1
        else: 
            page_increase = 0

        # Max page is set from
        #   int(limit / rows): rounded down number of pages the limit translates to
        #   st.session_state["curr_page"]: sets starting page 
        max_page = int(limit / rows) + st.session_state["curr_page"] + page_increase

    # Comparing "current" data against "previous" data and conditions 
    # formats style highlights if needed
    is_previous_valid = True
    usertip_previous = None
    if max_page:
        if st.session_state["prev_page"] > max_page:
            st.html("<style> .st-key-prev_page * {color: COLOR_REF} </style>"
            .replace("COLOR_REF", st.session_state["negative_color"]))
            st.html("<style> .st-key-prev_row * {color: COLOR_REF} </style>"
            .replace("COLOR_REF", st.session_state["negative_color"]))
            msg, usertip_previous = "Out of range", "The stop section number exceeds value limit."
            is_current_valid = False
        elif st.session_state["prev_page"] == max_page:
            if st.session_state["prev_row"] > max_row:
                st.html("<style> .st-key-prev_row * {color: COLOR_REF} </style>"
            .replace("COLOR_REF", st.session_state["negative_color"]))
                msg, usertip_previous = "Out of range", "The stop position number exceeds value limit."
                is_current_valid = False
    return is_current_valid, is_previous_valid, msg, usertip_current, usertip_previous


def _submit(prev_page: int, curr_page: int, 
            prev_row: int, curr_row: int, 
            is_invalid: bool) -> (int | None):
    """
    Calculate progress_display_value from validated selectbox input  depending on case
    
    For uniform page sizes:  
    `Amount = [rows per page] ⋅ ( [previous page] - [current page] ) 
            + [previous row] - [current row]`
    
    For varying page sizes:  
    `Amount = [initial page remainder] 
            + Σ[page total until max limit exceeded]
            + [last page up to max]`
    """

    if not is_invalid: 
        start_value = 1 if st.session_state["start_at_1"] else 0
        # Uniform size pages
        if type(st.session_state["sets"]) is dict:
            rows = st.session_state["sets"]["rows"]
            value = start_value + rows*(prev_page - curr_page) + prev_row - curr_row
        # Varying size pages
        elif type(st.session_state["sets"]) is list:
            # List index counts from zero; subtract 1 from page selection value
            idx = st.session_state["curr_page"] - 1
            # Case: same page
            if idx == st.session_state["prev_page"] - 1:
                value = start_value + st.session_state["prev_row"] - st.session_state["curr_row"]
            # Case: different pages -> loop pages until selected previous page
            else:
                # Set value from starting page
                value = start_value + st.session_state["sets"][idx] - st.session_state["curr_row"]
                while idx < st.session_state["prev_page"] - 1:
                    idx += 1
                    if idx < st.session_state["prev_page"] - 1:
                        # Looped values for in-between pages
                        value += st.session_state["sets"][idx]
                    else:
                        # Value from last page
                        value += st.session_state["prev_row"]
        return value
    else:
        return None
    

def _result_viewer(col_label, output: int|None, 
                   usertip_current: str, usertip_previous: str):
    """
    View calculated result, or '-' in no result value.

    Args:
        col_label (DeltaGenerator):
            instance object of streamlit column class
        output (int|None):
            calculated result from current and previous page and row
        usertip_current (str):
            text for giving a hint if invalid input of current value
        usertip_previous (str):
            text for giving a hint if invalid input of previous value
    """
    result_output = f"—"
    if output is not None:
        if output:
            result_output = f"**{output-1}**"
        col_label.button(result_output, width="stretch")
    else:
        if usertip_current: 
            col_label.button(result_output, width="stretch")
            st.html("""
                <style> 
                    .st-key-warning {color: COLOR_REF;} 
                    .st-key-warning_sign button {
                        margin-top: 6px; 
                        border-radius: 30px; 
                        border: solid 0.1rem COLOR_REF;
                    } 
                </style>""")
                # .replace("COLOR_REF", st.session_state["negative_color"]))
            with st.container(key="warning", width="stretch", height="stretch"):
                st.markdown(f"*{usertip_current}*", width="stretch")
        elif usertip_previous: 
            col_label.button(result_output, width="stretch")
            with st.container(key="warning", width="stretch", height="stretch"):
                st.markdown(f"*{usertip_previous}*", width="stretch")
        else:
            col_label.button(result_output, width="stretch")
    

@st.dialog("Define sets of sections and sizes")
def _define_sets():
    """
    User form for creating new sets of pages and rows for a specific source.
    """
    st.session_state["dialog_active"] = True
    progress_data = hold.load_progress_data()
    set_options = list(progress_data.keys())
    col1, col2 = st.columns(2)
    if not len(progress_data) > 0:
        st.info("No tracking data found.")
        return
    with st.container(border=False, height=330):
        selection = col1.selectbox(f"Select {TERMS["source"].lower()} to edit", options=set_options)
        col2.space(32)
        st.space()
        is_invalid = True
        # if not selection:
        #     pass
        if type(progress_data[selection]["sets"]) is dict:
            page_preset = progress_data[selection]["sets"]["pages"]
            row_preset = progress_data[selection]["sets"]["rows"]
            preset = ""
            placeholder = "Enter list of section sizes"
        elif type(progress_data[selection]["sets"]) is list:
            page_preset = 10
            row_preset = 10
            placeholder = None
            preset = str()
            space = ""
            n = 1
            for x in progress_data[selection]["sets"]:
                preset += f"{space}{x}"
                if n == 10:
                    space = "\n" 
                    n = 1
                else:
                    space = " "
                    n += 1
        else:
            page_preset, row_preset = None, None

        if col2.checkbox("Same size for all sections", value=True):
            
            col1, col2 = st.columns(2)
            pages = col1.number_input("Section", min_value=1, value=page_preset)
            rows = col2.number_input("Section size", min_value=1, value=row_preset)
            if pages == page_preset and rows == row_preset:
                is_invalid = True
            elif pages and rows: 
                is_invalid = False
            sets = {
                "pages": pages,
                "rows": rows
            }
        else:
            text = """Enter section size in order of section separated by single space.  
                For many sections, you can separate them into lines."""

            text2 = """***Note:** sections are counted in continuous fashion 
            from the first value and up, 
            regardless of line separation.*"""
            
            example = """Example:  
                10 6 24 22 8 24 43  
                12 15 31 2 13"""
            
            st.markdown(text)
            st.markdown(text2)
            row_input = st.text_area(example, value=preset, placeholder=placeholder, label_visibility="visible")
            row_lineless = " ".join(row_input.splitlines())
            row_list = row_lineless.split()
            sets = list()
            is_invalid = False
            for x in row_list:
                if x.isnumeric():
                    sets.append(int(x))
                else:
                    st.markdown("Invalid character")
                    is_invalid = True
                    break

    col_1, col_2, col_3 = st.columns(3)
    appearance = "secondary" if is_invalid else "primary"
    if col_2.button("Save", type=appearance, disabled=is_invalid, width="stretch"):
        progress_data[selection]["sets"] = sets
        file = st.session_state["DATAPATH"]["progress"]
        error.catch_data(progress_data, file, TERMS["progress"])
        arciv.writer(
            progress_data, object_type=TERMS["progress"], 
            set_file=file, join_path="data")
        st.session_state["cleared_cache"] = True
        hold.load_progress_data.clear()
        st.rerun()


    