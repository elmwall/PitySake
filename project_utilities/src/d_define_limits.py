"""
Page D: Create sources and set value settings

Guide: explain sources and value limits, highlights and unit  
Example image: timeline feature (high/mid/low values)

Manages:
- Form: 
    - Collect all sources with limit, enabled evaluation, enabled values
    - Highlights enabling, high or low positive, threshold values
    - Selected unit
"""

import streamlit as st

from utils import tools


# Step 4: define limits
def define_event_limits(set_width: int|str):
    """
    Define sources and value settings - present user info and collect details.

    Behavior:
    - disables save button until until at least one source is registered, re-enables if changed
    - disables next button until first save
    """
    with st.container(
            border=False, width=set_width, 
            height="stretch", horizontal_alignment="center"):
        if not all(st.session_state["submitted"]["progress_details"].values()):
            st.session_state["page_incomplete"] = True
        else:
            st.session_state["page_incomplete"] = False

        # Header
        st.progress(80, width="stretch")
        col_prev, col_space, col_title, col_apply, col_next = st.columns(
            [2, 2, 5, 2, 2])
        tools.navigate(col_prev, col_next)
        col_title.markdown(
            "#### Sources and value limits", text_alignment="center")
        st.space()

        # Form
        submission_key = "progress_details"
        button_format_key = "progress_need_save"
        is_changed_key = "progress_is_changed"
        with st.container(horizontal_alignment="center"):
            submission = _define_sources(button_format_key, is_changed_key)
        with col_apply:
            if st.session_state["page_initial_state"]:
                tools.need_update(button_format_key, is_changed_key, invalid_data=True)
            tools.apply("progress_save", button_format_key, is_changed_key, submission_key, submission)

        # Demo
        col_d1, col_d2 = st.columns(2)
        with col_d1.expander("Explanation"):
            with st.container(border=False):
                st.markdown("""
                ##### Sources:
                - Group related events
                - Each event registered belong to a source
                - Sources control whether events store values (with separate range limits) and if they are included in statistics (success/fail counts)
                - You can add or remove sources and adjust limits later
                - Effect on highlight:
                    - A source limit of 1000 and limits of 10% and 80%  
                    will highlight values below 100 and above 800
                
                ##### Timeline highlights
                - Mark values you consider notable
                - Mark 'success' and 'fail' outcomes
                - They do not affect calculations
                            
                Behavior:
                - If high values are 'positive': 
                    - low value → negative color
                    - high value → positive color
                - If low values are 'positive': 
                    - high value → negative color
                    - low value → positive color
                
                ##### Value rules  
                - Values are optional depending on source settings
                - Values must be integers (no decimal values)
                - Recommended range: 1-99999 
                - Unit suffix affects is only a display indicator of your value sizes, 
                values themselves are displayed exactly as you enter them """)
        with col_d2.expander("View example", width=set_width):
            with st.container(border=False):
                st.image(
                    "../accessories/progress2_notes.png",  
                    output_format="PNG")
                st.image(
                    "../accessories/timeline2_notes2.png",  
                    output_format="PNG")
                st.markdown("""
                Appearance affected by settings:  
                - 'High values are positive': would reverse red and green if selected  
                - Values above the high threshold: red lines
                - Values below the low threshold: green lines
                - All in between: grey lines
                - Values disabled: no lines, arrow symbol instead of object indocator 
                            
                Independent appearance: 
                - Main objects denoted by circle, secondary by square.  
                - Color of symbol indicates positive (green), negative (red), or neutral (grey) outcomes.
                
                The color for high/positive, low/negative, and neutral/in-between can be changed in theme settings.
                """)


def _define_sources(button_format_key: str, is_changed_key: str) -> dict:
    """
    User info and input fields for sources and value settings.  
    - Define number of sources  
    - Corresponding number of input groups are generated   
    Generate error message for invalid names.

    Args:
        button_format_key (str):
            format key, setting discrete or highlighted save button
        is_changed_key (str): 
            control key for behavior upon change

    Returns:
        (dict):
            sources, switches, high_limit, low_limit"""
    col_1, col_2, col_3 = st.columns([1, 1.5, 1.5])

    # User info
    col_1.markdown("""
        Define how events are categorized and adjust their value limits.
        - Each source is a separate category for logging events and tracking values
        - Limit sets a max value that can be registered in that source.""")
    col_1.markdown("""
        - Timline highlights: to distiguish notable values and outcomes  
            - Set from % of the limit  
            calculated separately for each source
        - Unit suffix affects display only. Stored values are not converted.""")
    
    # Input fields
    # - Sources and limits
    source_dict = dict()
    checks = list()
    names = dict()
    has_empty, first = False, True
    with col_2.container(border=True, height="stretch"):
        st.markdown("##### Sources", text_alignment="center")
        num_msg = """Number of event sources  
        *Create at least 1 - can be edited later*"""
        source_count = st.number_input(num_msg, min_value=1)

        # Generate number of groups of input fields corresponding to selected number of sources
        key = "source"
        source_list = list()
        duplicates = list()
        for x in range(source_count):
            st.divider()
            with st.container():
                col_left, col_right = st.columns(2)
                key_txt = f"{key}_{x + 1}_name"
                key_evaluation = f"{key}_{x + 1}_evaluation"
                key_disable_value = f"{key}_{x + 1}_disable_value"
                key_num = f"{key}_{x + 1}_limit"
                # Name source
                source_name = col_left.text_input(
                    "Source name", 
                    key=key_txt, 
                    help="",
                    on_change=tools.need_update, 
                    args=(button_format_key, is_changed_key))
                # Source settings
                col_right.checkbox("Outcome evaluation", key=key_evaluation, value=True)
                disable_values = not col_right.checkbox("Include values", key=key_disable_value, value=True)
                col_right.number_input(
                    "Source-specific value limit", 
                    key=key_num, 
                    min_value=1, 
                    value=100,
                    on_change=tools.need_update, 
                    args=(button_format_key, is_changed_key),
                    disabled=disable_values)
                
                # Validations: word format and duplicates
                # Disable save if invalid word
                word_is_invalid = tools.symbol_validation(source_name)
                if word_is_invalid:
                    tools.need_update(button_format_key, is_changed_key, invalid_data=True)
                    name_value = None
                elif len(source_name) == 0:
                    name_value = None
                else:
                    name_value = source_name
                if word_is_invalid: 
                    col_left.error(word_is_invalid)
                names[key_txt] = name_value
                source_list.append(name_value)
                is_duplicate = tools.check_duplicates(source_list, message=False)
                duplicates.append(is_duplicate)
                if not source_name: has_empty = True

                # Define source with settings
                # Empty or duplicate fields are ignored unless checklist is empy
                # then checklist receives a False
                if not is_duplicate and name_value:
                    checks.append(name_value)
                    if False in checks: checks.remove(False)
                    if disable_values:
                        limit_value = None
                        checks.append(True)
                    else:
                        limit_value = st.session_state[key_num]
                        checks.append(limit_value)
                    source_dict[source_name] = {
                        "limit": limit_value,
                        "evaluate": st.session_state[key_evaluation]}
                elif len(source_dict) == 0:
                    if False not in checks:
                        checks.append(False)
        # User notifications
        if any(duplicates): st.warning("Multiples excluded")
        if has_empty and source_count > 1: st.info("Empty fields are not saved")
    
    # - Highlights
    with col_3.container(border=True):
        st.markdown("##### Timeline highlights", text_alignment="center")
        col_left, col_right = st.columns(2)

        disable_highlights = col_left.checkbox("Use highlights", value=True, key="use_highlights") == False
        col_right.checkbox("High values are positive", key="reverse_positive", disabled=disable_highlights)
        col_left.number_input("Low value % threshold", min_value=-1, value=10, key="low_value", disabled=disable_highlights)
        col_right.number_input("High value % threshold", min_value=0, value=90, key="high_value", disabled=disable_highlights)
        if not disable_highlights:
            checks.append(st.session_state["low_value"])
            checks.append(st.session_state["high_value"])

    # - Units
    with col_3.container(border=True):
        st.markdown("##### Display units", text_alignment="center")
        col_left, col_right = st.columns(2)
        text = """Use suffix to signify:  
            M: Mega (× 1 000 000)  
            k: kilo (× 1 000)  
            None: skip  
            m: milli (÷ 1 000)  
            µ: micro (÷ 1 000 000)
            """     
        col_left.markdown(text)
        col_right.selectbox(
            "suffix", 
            options=["M", "k", "None", "m", "µ"], 
            index=2, 
            key="unit",
            on_change=tools.need_update, 
            args=(button_format_key, is_changed_key)
        )
    
    unit = None if st.session_state["unit"] == "None" else st.session_state["unit"]
    st.session_state["checklists"]["progress_save"] = checks

    switches = {
        "unit": unit,
        "reverse_positive": not st.session_state["reverse_positive"],
        "use_highlights": st.session_state["use_highlights"]
    }

    # Return preliminary submission
    return  {
        "sources": source_dict,
        "switches": switches,
        "high_limit": st.session_state["high_value"],
        "low_limit": st.session_state["low_value"]
    }







