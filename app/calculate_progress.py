"""
Interactive calculation assistant

Builds and manages:
- calculator setting:
    - progress value calculator interface
    - basic calculations: percent, addition, multiplication
- input validation logic and processing
- result display 
- edit dialog box to define sets per source
"""

import logging

import streamlit as st

import app.data_access as hold
import app.error_handler as error
from app.initialize import arciv, DATAPATH, TERMS


attempt_ref = TERMS["attempt"]
logger = logging.getLogger(__name__)


def calculator(component_key: str, feature_width: int | str, 
               highlight_html: str, feature_height: int | str):
    """
    Render calculation assistant feature
    - input set and position values
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
            feature_help = f"""Calculate {attempt_ref} from events.  
            Select a {TERMS["source"]} to define sections and max limit."""
            st.markdown("##### *Calculate*", help=feature_help, text_alignment="left")

    # Main container
    with st.container(
            border=True, key=f"{component_key}_main", 
            width=feature_width, height=feature_height):
        progress_data = hold.load_progress_data()
        value_trackers = list(st.session_state["value_trackers"].keys())
        for x in ["section_range", "position_range"]:
            if x not in st.session_state: _update_sections(progress_data, value_trackers)
        with st.container(horizontal_alignment="center"):
            col_select, col_define = st.columns([3, 2.5])
            
            # Mode 
            if st.session_state["calc_mode"]:
                mode_text = "Mode: values"
            else:
                mode_text = "Mode: sets"
            help = """☐ **Sets:** calculate distance across sets  
                🗹 **Values:** calculate % + ×"""
            percent_mode = col_select.checkbox(mode_text, key="calc_mode", help=help)
            
            # Calculator value start value setting
            # Select sections sets for calculation
            # Each progress tracking source has defined sets
            # Dropdown selection
            if not percent_mode:
                col_define.checkbox(
                    "Start from 1", value=False, key="start_at_1", disabled=percent_mode,
                    help="""When enabled, begins count from 1 instead of 0  
                    for the first position after the start event.""")
                selected_set = col_select.selectbox(
                    f"Select {TERMS["source"]}", options=value_trackers, key="selected_set", 
                    on_change=_update_sections, args=(progress_data, value_trackers), 
                    disabled=percent_mode, label_visibility="collapsed")
                # Edit sets button
                set_help = """Create custom sets by defining per set:  
                    - number of sections  
                    - number of positions per section."""
                if col_define.button(
                    "Define sets", help=set_help, disabled=percent_mode, type="secondary", width="stretch"):
                    _define_sets(progress_data, value_trackers)
                st.space(1)

            col_left, col_right, col_label = st.columns([5, 5, 7])
            if not percent_mode:
                no_limit = True
                if selected_set:
                    options = hold.load_options()
                    if options:
                        limit = options["source_limit"][selected_set]
                    else:
                        limit = 0
                    no_limit = False
                
                # Value selector field: Enter values for calculation
                # UI structured as left for start and right for stop
                msg, appearance = "Lacking sets", "secondary"
                usertip_start, usertip_stop = "", ""
                _value_selector(col_left, col_right, col_label, no_limit)
                if not no_limit:
                    is_start_valid, is_stop_valid, msg, usertip_start, usertip_stop = _validation(limit)
                    # View settings depending on data validity
                    if is_start_valid is not False and is_stop_valid is not False:
                        st.html(highlight_html.replace("KEY_REF", "calc_button"))
                        is_invalid, appearance = False, "primary"
                    else:
                        is_invalid, appearance = True, "secondary"
                        st.session_state["calculation"] = None
                else:
                    is_invalid = True
                # Field for submit and result
                # Submit button
                st.html("""
                        <style>
                            .st-key-calc_button button {
                                white-space: nowrap;
                            }
                        </style>""")
                if col_label.button(
                        f"{msg}", key="calc_button", type=appearance, 
                        disabled=is_invalid, width="stretch"):
                    output = _submit(
                        st.session_state["start_section"], st.session_state["stop_section"], 
                        st.session_state["start_position"], st.session_state["stop_position"], 
                        is_invalid)
                else:
                    output = None
                # Output viewer field 
                # - views tip for correcting data or result of calculation
                _result_viewer(col_label, output, usertip_start, usertip_stop)

            else:
                _value_input()


def _update_sections(progress_data: dict, value_trackers: list):
    """
    Update sections and positions, and define ranges depending on case.
    - Uniform section/positions sets are defined by a dict with corresponding keys.  
    - Sections with varying positions are defined by a list. 
        The length defines number of sections while value at indices sets number of positions.

    Args:
        progress_data (dict):
            data from all trackers
        value_tracker (list):
            active trackers with value
    """
    if value_trackers:
        selected_set = st.session_state.get("selected_set", value_trackers[0])
        if selected_set in progress_data:
            # The list of sections is corrected to show list starting from 1
            # since lists starts with index 0
            sets = st.session_state["sets"] = progress_data[selected_set]["sets"]
            # Uniform sections/positions
            if isinstance(sets, dict):
                st.session_state["section_range"] = list(range(sets["sections"] + 1))[1:]
                # Generates a list that can used directly for options
                st.session_state["position_range"] = list(range(sets["positions"] + 1))[1:]
            # Varying sections/positions
            elif isinstance(sets, list):
                st.session_state["section_range"] = list(range(len(sets) + 1))[1:]
                # Here the sets provide a list of positions for each section 
                # -> needs to be collected and adjusted for start and stop respectively


def _value_selector(col_left, col_right, col_label, disable: bool):
    """
    Selectboxes selecting start and stop section and position.

    Args:
        col_x (DeltaGenerator):
            Streamlit column instance
        disable (bool):
            control value to disable selection if no source is set
    """
    # Group labels
    col_left.markdown("*Start*", text_alignment="center")
    col_right.markdown("*Stop*", text_alignment="center")
    calculator_help = """Select a section and a position for both start and stop events.  
        The calculation traverses all intermediate sections and returns the total value.  
        - **Top:** section number   
        - **Bottom:** position within section"""
    col_label.markdown(" ", help=calculator_help)
    sets = st.session_state["sets"]
    # Input section for start and stop event
    section_range = st.session_state.get("section_range", [])
    if not section_range: 
        section_range = []
        disable = True

    start_section = col_left.selectbox(
        "Start", options=section_range, index=0,
        key="start_section", disabled=disable, label_visibility="collapsed")
    stop_section = col_right.selectbox(
        "Stop", options=section_range, index=0, 
        key="stop_section", disabled=disable, label_visibility="collapsed")
            
    # Input position for start and stop event
    # View options should show alternatives 1 and up 
    # and not the list default starting from 0
    position_range = st.session_state.get("position_range", [])
    start_opt, stop_opt = [None]*2
    if isinstance(sets, dict) and start_section:
        if not position_range: 
            position_range = []
            disable = True
        start_opt = position_range.copy()
        # Except for 1st page, keep the 0th
        if int(start_section) == 1: start_opt = [0,] + start_opt
        stop_opt = position_range
    elif isinstance(sets, list) and start_section and stop_section:
        # Sections in order from 0: correct index to start from 1
        start_index = start_section -1
        stop_index = stop_section - 1
        # Add 1 and drop the 0th
        stop_opt = list(range(sets[stop_index] + 1)[1:])
        if int(start_section) == 1:
            # For 1st page, keep the 0th
            start_opt = list(range(sets[stop_index] + 1))
        else:
            start_opt = list(range(sets[start_index] + 1)[1:])
    disable = not start_opt or not stop_opt
    with col_left:
        st.selectbox(
            "Start event position", options=start_opt, index=0,
            key="start_position", disabled=disable, label_visibility="collapsed")
    with col_right:
        st.selectbox(
            "Stop event position", options=stop_opt, index=0, 
            key="stop_position", disabled=disable, label_visibility="collapsed")


def _validation(limit: int) -> tuple:
    """
    Data validation for calculator input, checks
    - distance start-to-stop not exceeding project limit
    - logically possible position and section combinations

    Args:
        limit (int):
            Maximum allowed progress_display_value value from project settings
    
    Returns:
        Tuple (bool, bool, str, str, str):
            bools: start and stop validity  
            message string for button display  
            user tip strings for correcting input
    """

    msg = "Calculate"
    usertip_start = None
    usertip_stop = None
    is_start_valid = False
    negative_color = st.session_state.get("negative_color", "#FF0000")

    sets = st.session_state["sets"]
    start_value = 1 if st.session_state["start_at_1"] else 0

    start_section = st.session_state.get("start_section", 1)
    stop_section = st.session_state.get("stop_section", 1)
    start_position = st.session_state.get("start_position", 1)
    stop_position = st.session_state.get("stop_position", 2)
    if any([start_section is None, stop_section is None, start_position is None, stop_position is None]):
        return False, False, msg, "", ""

    # Conditions for start data
    if isinstance(sets, dict):
        start_pos_range = stop_pos_range = len(st.session_state["position_range"])
    elif isinstance(sets, list):
        start_index = start_section - 1
        stop_index = stop_section - 1
        start_pos_range = sets[start_index]
        stop_pos_range = sets[stop_index]

    if start_position == start_pos_range: 
        stop_section_min = start_position + 1
    else: 
        stop_section_min = start_section

    # Comparing start data against stop data and conditions 
    # formats style highlights if needed
    if stop_section < stop_section_min: 
        msg = "Out of range"
        if start_section == stop_section:
            st.html(
                "<style> .st-key-stop_section * {color: COLOR_REF} </style>"
                .replace("COLOR_REF", negative_color))
            st.html(
                "<style> .st-key-start_position * {color: COLOR_REF} </style>"
                .replace("COLOR_REF", negative_color))
            usertip_start = "Invalid selections. Start is at the last position, stop section must then be greater."
        else:
            st.html(
                "<style> .st-key-start_section * {color: COLOR_REF} </style>"
                .replace("COLOR_REF", negative_color))
            usertip_start = "Invalid sections. Start section number cannot be higher than stop section."
    elif start_section == stop_section:
        if stop_position <= start_position:
            st.html(
                "<style> .st-key-stop_position * {color: COLOR_REF} </style>"
                .replace("COLOR_REF", negative_color))
            msg, usertip_start = "Out of range", "Invalid positions. Within the same section, stop position must be higher than start position."
        else:
            is_start_valid = True
            usertip_start = None
    else:
        is_start_valid = True
        usertip_start = None
    max_section, max_position = None, None
    # Conditions for stop data
    if isinstance(sets, list):
        sections = len(sets)
        idx = start_section - 1
        val = start_value + sets[idx] - start_position
        while idx < sections:
            idx += 1
            # Loop until last section then set max beyond, i.e. no limit within range
            if idx + 1 == sections:
                max_section = idx + 1
                max_position = limit - val + 1
                break
            # If the upcoming section exceeds limit, set max section and position from here
            elif val + sets[idx] > limit:
                max_section = idx + 1
                max_position = limit - val + 1
                break
            # Within limits, add value of whole sections
            else:
                val += sets[idx]
    elif isinstance(sets, dict):
        positions = sets["positions"]
        # Max position is set from:
        #   positions * int(int(limit / positions) - 1): the value corresponding to all whole sections
        #   positions - start_position: the value from the start section start position
        #   - 1: the counter starts from 0, i.e. the first position is 0, then each position gives +1
        max_position = limit - positions * int(int(limit / positions) - 1) - int(positions - start_position - 1) - start_value
        if max_position > stop_pos_range:
            section_increase = 1
            max_position = 1
        else: 
            section_increase = 0

        # Max section is set from
        #   int(limit / positions): rounded down number of sections the limit translates to
        #   start_section: sets starting section 
        max_section = int(limit / positions) + start_section + section_increase

    # Comparing "start" data against stop data and conditions 
    # formats style highlights if needed
    is_stop_valid = True
    usertip_stop = None
    if max_section:
        if stop_section > max_section:
            st.html("<style> .st-key-stop_section * {color: COLOR_REF} </style>"
            .replace("COLOR_REF", negative_color))
            st.html("<style> .st-key-stop_position * {color: COLOR_REF} </style>"
            .replace("COLOR_REF", negative_color))
            msg, usertip_stop = "Out of range", "The stop section number exceeds value limit."
            is_start_valid = False
        elif stop_section == max_section:
            if stop_position > max_position:
                st.html("<style> .st-key-stop_position * {color: COLOR_REF} </style>"
            .replace("COLOR_REF", negative_color))
                msg, usertip_stop = "Out of range", "The stop position number exceeds value limit."
                is_start_valid = False
    return is_start_valid, is_stop_valid, msg, usertip_start, usertip_stop


def _value_input():
    """
    Number input fields for calculating percent, addition, multiplication, and division.
    """
    st.space()
    size = [5, 1.5, 5, 6]
    col_1, col_sym, col_2, col_res = st.columns(size)
    _calculate(col_1, col_sym, col_2, col_res, "percent", "of", 100)
    col_1, col_sym, col_2, col_res = st.columns(size)
    _calculate(col_1, col_sym, col_2, col_res, "add", "+")
    col_1, col_sym, col_2, col_res = st.columns(size)
    _calculate(col_1, col_sym, col_2, col_res, "multiply", "×")
    col_1, col_sym, col_2, col_res = st.columns(size)
    _calculate(col_1, col_sym, col_2, col_res, "divide", "÷", 160)

def _calculate(col_1, col_sym, col_2, col_res, 
               action: str, symbol: str, value: int|bool = 0):
    """
    Generate a field row for specified action.

    Args:
        col_x (DeltaGenerator):
            Streamlit column instance
        action (str):
            specify action
        symbol (str):
            word or operator shown
        value (int|bool):
            specifies preset value in number field
    """
    st.html("<style>.st-key-REF p {font-size: 18px}</style>".replace("REF", f"{action}_symbol"))
    input_1 = col_1.number_input(
        f"{action} input", value=0, key=f"{action}_1", 
        label_visibility="collapsed", width="stretch")
    col_sym.button(symbol, key=f"{action}_symbol", type="tertiary")
    input_2 = col_2.number_input(
        f"{action} input", value=value, key=f"{action}_2", 
        label_visibility="collapsed", width="stretch")
    
    result = "-"
    if input_1 is not None and input_2 is not None:
        suffix = ""
        precision = ".1f"
        if action == "percent" and input_2 != 0:
            result = 100 * input_1 / input_2
            suffix = " %"
        elif action == "add":
            result = input_1 + input_2
        elif action == "multiply":
            result = input_1 * input_2
        elif action == "divide" and input_2 != 0:
            result = input_1 / input_2
            precision = ".2f"
        output = f"{int(result)}{suffix}" if float(result).is_integer() else f"{result:{precision}}{suffix}"

    col_res.button(str(output), key=f"{action}_result", width="stretch")



def _submit(start_section: int, stop_section: int, 
            start_position: int, stop_position: int, 
            is_invalid: bool) -> int | None:
    """
    Calculate progress_display_value from validated selectbox input  depending on case
    
    For uniform section sizes:  
    `Amount = [positions per section] ⋅ ( [stop section] - [start section] ) 
            + [stop position] - [start position]`
    
    For varying section sizes:  
    `Amount = [initial section remainder] 
            + Σ[section total until max limit exceeded]
            + [last section up to max]`
    """
    if not is_invalid: 
        sets = st.session_state["sets"]
        init_value = 1 if st.session_state["start_at_1"] else 0
        # Uniform size sections
        if isinstance(sets, dict):
            value = init_value + sets["positions"]*(stop_section - start_section) + stop_position - start_position
        # Varying size sections
        elif isinstance(sets, list):
            if not stop_position: stop_position = 0
            if not start_position: start_position = 0
            # List index counts from zero; subtract 1 from section selection value
            idx = st.session_state["start_section"] - 1
            # Case: same section
            if idx == stop_section - 1:
                value = init_value + stop_position - start_position
            # Case: different sections -> loop sections until selected stop section
            else:
                # Set value from starting section
                value = init_value + sets[idx] - start_position
                while idx < stop_section - 1:
                    idx += 1
                    if idx < stop_section - 1:
                        # Looped values for in-between sections
                        value += sets[idx]
                    else:
                        # Value from last section
                        value += stop_position
        return value
    else:
        return None
    

def _result_viewer(col_label, output: int | None, 
                   usertip_start: str, usertip_stop: str):
    """
    View calculated result, or '-' in no result value.

    Args:
        col_label (DeltaGenerator):
            instance object of streamlit column class
        output (int|None):
            calculated result from start and stop section and position
        usertip_start (str):
            text for giving a hint if invalid input of start value
        usertip_stop (str):
            text for giving a hint if invalid input of stop value
    """
    result_output = f"—"
    if output is not None:
        if output:
            result_output = f"**{output-1}**"
        col_label.button(result_output, width="stretch")
    else:
        if usertip_start: 
            col_label.button(result_output, width="stretch")
            st.html("""
                <style> 
                    .st-key-warning {color: COLOR_REF;} 
                </style>""")
                # .replace("COLOR_REF", st.session_state["negative_color"]))
            with st.container(key="warning", width="stretch", height="stretch"):
                st.markdown(f"*{usertip_start}*", width="stretch")
        elif usertip_stop: 
            col_label.button(result_output, width="stretch")
            with st.container(key="warning", width="stretch", height="stretch"):
                st.markdown(f"*{usertip_stop}*", width="stretch")
        else:
            col_label.button(result_output, width="stretch")
    

@st.dialog("Define sets of sections and sizes")
def _define_sets(progress_data: dict, value_trackers: list):
    """
    User form for creating new sets of sections and positions for a specific source.

    Args:
        progress_data (dict):
            database of sources and tracking
        value_trackers (list):
            active trackers with value
    """
    st.session_state["dialog_active"] = True
    active_trackers = st.session_state.get("active_trackers", {})
    if not active_trackers: logger.warning("Cannot define sets without active trackers.")

    col1, col2 = st.columns(2)
    if not progress_data:
        logger.warning("No tracking data found.")
        st.info("No tracking data found.")
        return
    
    with st.container(border=False, height=330):
        selection = col1.selectbox(f"Select {TERMS["source"]} to edit", options=value_trackers)
        sets = progress_data[selection]["sets"]
        col2.space(32)
        st.space()
        is_invalid = True
        section_preset, position_preset, preset, placeholder = [None]*4
        disable = False
        if not selection:
            disable = True
        elif isinstance(sets, dict):
            section_preset = sets["sections"]
            position_preset = sets["positions"]
            preset = ""
            placeholder = "Enter list of section sizes"
        elif isinstance(sets, list):
            section_preset = 10
            position_preset = 10
            preset = str()
            space = ""
            n = 1
            for x in sets:
                preset += f"{space}{x}"
                if n == 10:
                    space = "\n" 
                    n = 1
                else:
                    space = " "
                    n += 1
        else:
            section_preset, position_preset = None, None

        if col2.checkbox("Same size for all sections", value=True):
            col1, col2 = st.columns(2)
            sections = col1.number_input(
                "Section", min_value=1, value=section_preset, disabled=disable)
            positions = col2.number_input(
                "Section size", min_value=1, value=position_preset, disabled=disable)
            if sections == section_preset and positions == position_preset:
                is_invalid = True
            elif sections and positions: 
                is_invalid = False
            sets = {
                "sections": sections,
                "positions": positions
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
            position_input = st.text_area(
                example, value=preset, placeholder=placeholder, 
                disabled=disable, label_visibility="visible")
            sets = list()
            if position_input:
                if len(position_input) > 1:
                    position_lineless = " ".join(position_input.splitlines())
                    position_list = position_lineless.split()
                    is_invalid = False
                    for x in position_list:
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
        file = DATAPATH["progress"]
        error.catch_data(progress_data, file, TERMS["progress"])
        if arciv.backup(
                [101, 47, 19, 7, 3], TERMS["progress"], join_path="data",
                set_file=file, empty_allowed=True):
            arciv.writer(
                progress_data, object_type=TERMS["progress"], 
                set_file=file, join_path="data")
        st.session_state["cleared_cache"] = True
        hold.load_progress_data.clear()
        st.rerun()


    