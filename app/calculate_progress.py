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
from app.initialize import arciv


DATAPATH = st.session_state["DATAPATH"]
TERMS = st.session_state["TERMS"]
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
            feature_help = f"""Calculate {TERMS["attempt"]} from events.  
            Select a {TERMS["source"]} to define sections and max limit."""
            st.markdown("##### *Calculate*", help=feature_help, text_alignment="left")

    # Main container
    with st.container(
            border=True, key=f"{component_key}_main", 
            width=feature_width, height=feature_height):
        progress_data = hold.load_progress_data()
        for x in ["section_range", "position_range"]:
            if x not in st.session_state: _update_sections(progress_data)
        with st.container(horizontal_alignment="center"):
            # Select sections setts for calculation
            # Each progress tracking source has defined sets
            col_select, col_define = st.columns([3, 2.5])

            if st.session_state["calc_mode"]:
                set_options = [" ", ]
                mode_text = "Mode: values"
            else:
                set_options = [x for x in progress_data.keys() if progress_data[x][TERMS["attempt"]]]
                mode_text = "Mode: sets"
            help = """☐ calculate distance across sets  
                🗹 calculate: % + ×"""
            percent_mode = col_select.checkbox(mode_text, key="calc_mode", help=help)
            col_define.checkbox(
                "Start from 1", value=False, key="start_at_1", disabled=percent_mode,
                help="""When enabled, begins count from 1 instead of 0  
                for the first position after the start event.""")
            col_select.selectbox(
                f"Select {TERMS["source"]}", options=set_options, key="selected_set", 
                on_change=_update_sections, args=(progress_data,), 
                disabled=percent_mode, label_visibility="collapsed")
            # Empty field placeholder
            set_help = """Create custom sets by defining the  
                number of sections, and number of positions per section."""
            if col_define.button(
                "Define sets", help=set_help, disabled=percent_mode, type="secondary", width="stretch"):
                _define_sets(progress_data)
            st.space(1)
            col_left, col_right, col_label = st.columns([5, 5, 7])
            if not percent_mode:
                no_limit = True
                if st.session_state["selected_set"]:
                    options = hold.load_options()
                    if len(options) > 0:
                        limit = options["source_limit"][st.session_state["selected_set"]]
                    else:
                        limit = 0
                    no_limit = False
                
                # Value selector field: Enter values for calculation
                # UI structured as left for start and right for stop
                msg, appearance = "Lacking sets", "secondary"
                usertip_start, usertip_stop = "", ""
                _value_selector(col_left, col_right, col_label, no_limit)
                # Field for submit and result
                if not no_limit:
                    is_start_valid, is_stop_valid, msg, usertip_start, usertip_stop = _validation(limit)

                    # View settings depending on data validity
                    if is_start_valid and is_stop_valid:
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
                        st.session_state["start_section"], st.session_state["stop_section"], 
                        st.session_state["start_position"], st.session_state["stop_position"], 
                        is_invalid)
                else:
                    output = None
                # Output viewer field 
                # - views tip for correcting data or result of calculation
                _result_viewer(col_label, output, usertip_start, usertip_stop)

            else:
                _value_input(col_left, col_right, col_label, setting="percentage")


def _update_sections(progress_data):
    """
    Update sections and positions, and define ranges depending on case.
    - Uniform section/positions sets are defined by a dict with corresponding keys.  
    - Sections with varying positions are defined by a list. 
        The length defines number of sections while value at indices sets number of positions.
    """
    set_options = [x for x in progress_data.keys() if progress_data[x][TERMS["attempt"]]]
    st.session_state["sets"] = None
    if len(set_options) > 0:
        if "selected_set" not in st.session_state:
            st.session_state["selected_set"] = set_options[0]
        selected_set = st.session_state["selected_set"]
        if st.session_state["selected_set"]:
            if selected_set in progress_data:
                st.session_state["sets"] = progress_data[selected_set]["sets"]
                # Uniform sections/positions
                if type(st.session_state["sets"]) is dict:
                    st.session_state["section_range"] = range(st.session_state["sets"]["sections"] + 1)[1:]
                    st.session_state["position_range"] = st.session_state["sets"]["positions"]
                # Varying sections/positions
                # The list of sections is corrected to show list starting from 1
                # since lists starts with index 0
                elif type(st.session_state["sets"]) is list:
                    st.session_state["position_range"] = st.session_state["sets"]
                    st.session_state["section_range"] = range(len(st.session_state["position_range"]) + 1)[1:]


def _value_selector(col_left, col_right, col_label, no_limit: bool):
    """
    Selectboxes selecting start and stop section and position.

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
        # Input section (set) for start and stop event
        section_range = st.session_state["section_range"]
        position_range = st.session_state["position_range"]
    else:
        section_range, position_range = 0, 0
    col_left.selectbox(
        "Start", options=section_range, index=0,
        key="start_section", disabled=no_limit, label_visibility="collapsed")
    col_right.selectbox(
        "Stop", options=section_range, index=0, 
        key="stop_section", disabled=no_limit, label_visibility="collapsed")
            
    # Input data position for start and event
    if type(position_range) is int:
        position_range += 1
        stop_opt = range(position_range)[1:]
        start_opt = range(position_range) if int(st.session_state["start_section"]) == 1 else range(position_range)[1:]
    elif type(position_range) is list:
        stop_opt = range(position_range[st.session_state["stop_section"] - 1] + 1)[1:]
        if int(st.session_state["start_section"]) == 1:
            start_opt = range(position_range[st.session_state["start_section"] - 1] + 1)
        else:
            start_opt = range(position_range[st.session_state["start_section"] - 1] + 1)[1:]
    print(start_opt, start_opt[0])
    with col_left:
        st.selectbox(
            "Start event position", options=start_opt, index=0,
            key="start_position", disabled=no_limit, label_visibility="collapsed")
    with col_right:
        st.selectbox(
            "Stop event position", options=stop_opt, index=0, 
            key="stop_position", disabled=no_limit, label_visibility="collapsed")


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
    start_value = 1 if st.session_state["start_at_1"] else 0

    # Conditions for start data
    if type(st.session_state["sets"]) is list:
        position_range = st.session_state["position_range"][st.session_state["start_position"]]
    elif type(st.session_state["sets"]) is dict:
        position_range = st.session_state["position_range"]
    else:
        position_range = None

    if st.session_state["start_position"] == position_range: 
        stop_section_min = st.session_state["start_position"] + 1
    else: 
        stop_section_min = st.session_state["start_position"]
    # Comparing start data against stop data and conditions 
    # formats style highlights if needed
    if st.session_state["stop_section"] < stop_section_min: 
        st.html(
            "<style> .st-key-start_section * {color: COLOR_REF} </style>"
            .replace("COLOR_REF", st.session_state["negative_color"]))
        msg = "Out of range"
        if st.session_state["start_section"] == st.session_state["stop_section"]:
            st.html(
                "<style> .st-key-start_position * {color: COLOR_REF} </style>"
                .replace("COLOR_REF", st.session_state["negative_color"]))
            usertip_start = "Invalid selections. Start is at the last position, stop section must then be greater."
        else:
            usertip_start = "Invalid sections. Start section number cannot be higher than stop section."
    elif st.session_state["start_section"] == st.session_state["stop_section"]:
        if st.session_state["stop_position"] <= st.session_state["start_position"]:
            st.html(
                "<style> .st-key-stop_position * {color: COLOR_REF} </style>"
                .replace("COLOR_REF", st.session_state["negative_color"]))
            msg, usertip_start = "Out of range", "Invalid positions. Within the same section, start position must be less than stop position."
        else:
            is_start_valid = True
            usertip_start = None
    else:
        is_start_valid = True
        usertip_start = None

    max_section, max_position = None, None
    # Conditions for stop data
    if type(st.session_state["sets"]) is list:
        sections = len(st.session_state["sets"])
        idx = st.session_state["start_section"] - 1
        val = start_value + st.session_state["sets"][idx] - st.session_state["start_position"]
        while idx < sections:
            idx += 1
            # Loop until last section then set max beyond, i.e. no limit within range
            if idx + 1 == sections:
                max_section = idx + 1
                max_position = limit - val + 1
                break
            # If the upcoming section exceeds limit, set max section and position from here
            elif val + st.session_state["sets"][idx] > limit:
                max_section = idx + 1
                max_position = limit - val + 1
                break
            # Within limits, add value of whole sections
            else:
                val += st.session_state["sets"][idx]
    elif type(st.session_state["sets"]) is dict:
        positions = st.session_state["sets"]["positions"]
        # Max position is set from:
        #   positions * int(int(limit / positions) - 1): the value corresponding to all whole sections
        #   positions - st.session_state["start_position"]: the value from the start section start position
        #   - 1: the counter starts from 0, i.e. the first position is 0, then each position gives +1
        max_position = limit - positions * int(int(limit / positions) - 1) - int(positions - st.session_state["start_position"] - 1) - start_value
        if max_position > position_range:
            section_increase = 1
            max_position = 1
        else: 
            section_increase = 0

        # Max section is set from
        #   int(limit / positions): rounded down number of sections the limit translates to
        #   st.session_state["start_section"]: sets starting section 
        max_section = int(limit / positions) + st.session_state["start_section"] + section_increase

    # Comparing "start" data against stop data and conditions 
    # formats style highlights if needed
    is_stop_valid = True
    usertip_stop = None
    if max_section:
        if st.session_state["stop_section"] > max_section:
            st.html("<style> .st-key-stop_section * {color: COLOR_REF} </style>"
            .replace("COLOR_REF", st.session_state["negative_color"]))
            st.html("<style> .st-key-stop_position * {color: COLOR_REF} </style>"
            .replace("COLOR_REF", st.session_state["negative_color"]))
            msg, usertip_stop = "Out of range", "The stop section number exceeds value limit."
            is_start_valid = False
        elif st.session_state["stop_section"] == max_section:
            if st.session_state["stop_position"] > max_position:
                st.html("<style> .st-key-stop_position * {color: COLOR_REF} </style>"
            .replace("COLOR_REF", st.session_state["negative_color"]))
                msg, usertip_stop = "Out of range", "The stop position number exceeds value limit."
                is_start_valid = False
    return is_start_valid, is_stop_valid, msg, usertip_start, usertip_stop


def _value_input(col_left, col_right, col_label):
    """
    Number input fields for calculating percent, addition, multiplication.

    Args:
        col_left (DeltaGenerator):
            Streamlit column instance
        col_right (DeltaGenerator):
            Streamlit column instance
        col_label (DeltaGenerator):
            Streamlit column instance
    """
    col_label.space(23)
    # Calculate percent
    output = None
    part = col_left.number_input("Part", value=0, key="per1")
    total = col_right.number_input("Total", value=100, key="per2")
    if part is not None and total != 0: 
        output = part / total * 100
    result_output = f"—"
    if output is not None:
        result_output = (f"{int(output)} %")
    col_label.button(result_output, key="per3", width="stretch")
    st.space(5)

    col_1, col_sym, col_2, col_res = st.columns([4.3, 1.4, 4.3, 7])
    # Calculate addition
    add_1 = col_1.number_input("Add1", value=0, key="add1", label_visibility="collapsed", width="stretch")
    col_sym.button("+", type="tertiary")
    add_2 = col_2.number_input("Add2", value=0, key="add2", label_visibility="collapsed", width="stretch")
    addition = "-"
    if add_1 is not None and add_2 is not None:
        addition = add_1 + add_2
    col_res.button(str(addition), key="add3", width="stretch")

    # Calculate multiplication
    factor_1 = col_1.number_input("Mult1", value=0, key="mult1", label_visibility="collapsed", width="stretch")
    col_sym.button("×", type="tertiary")
    factor_2 = col_2.number_input("Mult2", value=0, key="mult2", label_visibility="collapsed", width="stretch")
    multiplied = "-"
    if factor_1 is not None and factor_2 is not None:
        multiplied = factor_1 * factor_2
    col_res.button(str(multiplied), key="mult3", width="stretch")


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
        # print(start_section, stop_section, start_position, stop_position)
        # start_section = st.session_state[start_section] if st.session_state[start_section] else 0
        # stop_section = st.session_state[stop_section] if st.session_state[stop_section] else 0
        # start_position = st.session_state[start_position] if st.session_state[start_position] else 0
        # stop_position = st.session_state[stop_position] if st.session_state[stop_position] else 0
        
        init_value = 1 if st.session_state["start_at_1"] else 0
        # Uniform size sections
        if type(st.session_state["sets"]) is dict:
            positions = st.session_state["sets"]["positions"]
            value = init_value + positions*(stop_section - start_section) + stop_position - start_position
        # Varying size sections
        elif type(st.session_state["sets"]) is list:
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
                value = init_value + st.session_state["sets"][idx] - start_position
                while idx < stop_section - 1:
                    idx += 1
                    if idx < stop_section - 1:
                        # Looped values for in-between sections
                        value += st.session_state["sets"][idx]
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
                    .st-key-warning_sign button {
                        margin-top: 6px; 
                        border-radius: 30px; 
                        border: solid 1.6px COLOR_REF;
                    } 
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
def _define_sets(progress_data):
    """
    User form for creating new sets of sections and positions for a specific source.
    """
    st.session_state["dialog_active"] = True
    set_options = [x for x in st.session_state["active_trackers"] if progress_data[x][TERMS["attempt"]] is not None]
    col1, col2 = st.columns(2)
    if not len(progress_data) > 0:
        st.info("No tracking data found.")
        return
    with st.container(border=False, height=330):
        selection = col1.selectbox(f"Select {TERMS["source"]} to edit", options=set_options)
        col2.space(32)
        st.space()
        is_invalid = True
        section_preset, position_preset, preset, placeholder = [None]*4
        disable = False
        if not selection:
            disable = True
        elif type(progress_data[selection]["sets"]) is dict:
            section_preset = progress_data[selection]["sets"]["sections"]
            position_preset = progress_data[selection]["sets"]["positions"]
            preset = ""
            placeholder = "Enter list of section sizes"
        elif type(progress_data[selection]["sets"]) is list:
            section_preset = 10
            position_preset = 10
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
        file = st.session_state["DATAPATH"]["progress"]
        error.catch_data(progress_data, file, TERMS["progress"])
        if arciv.backup(
                [101, 47, 19, 7, 3], TERMS["progress"], join_path="data",
                set_file=DATAPATH["progress"], empty_allowed=True):
            arciv.writer(
                progress_data, object_type=TERMS["progress"], 
                set_file=file, join_path="data")
        st.session_state["cleared_cache"] = True
        hold.load_progress_data.clear()
        st.rerun()


    