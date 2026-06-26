"""
Connector to project data

Manages:
- retrieves project settings
- setup config values in Streamlit session state
- edit project options and limits
"""

import copy
import logging
import os

import streamlit as st

from app.file_manager import Archivist
import app.error_handler as error


logger = logging.getLogger(__name__)


def initialize_constants(project_name: str):
    """
    Collect and initialize project settings
    - collects settings dictionaries via file_manager Archivist
    - initializes configuration values in session state
    """

    logger.info("Collecting project")

    # Use case for Archivist for unique single path-file:
    # - setup None-values for irrelevant references
    # - join_path with project_name/settings and project-unique config.json
    settings_path = os.path.join(project_name, "settings")
    arch = Archivist(
        DIRECTORIES={
            "DataFolder": None,
            "SettingsFolder": settings_path,
            "BackupFolder": None},
        DATAPATH={"backup_meta": None},
        file="config.json",
        initialized=False)
    config = arch.reader(join_path="settings")
    if not config:
        config_location = os.path.abspath(settings_path)
        st.error("PROJECT CONFIGURATION FILE MISSING OR CORRUPT")
        with st.container(border=True):
            st.markdown(f"""Could not find config.json in:  \n{config_location}""")
            st.markdown("A generic version can be found [here](https://github.com/elmwall/PitySake/blob/main/user_project/settings/config.json). Place it in the folder above.")
        quit()

    # Store config dictionaries in session state
    for dictionary, content in config.items():
        st.session_state[dictionary] = content
    for key, path in st.session_state["DIRECTORIES"].items():
        st.session_state["DIRECTORIES"][key] = os.path.join(project_name, path)

    # Collect project-specific settings to check in initialize
    st.session_state["meta"] = arch.reader(set_file="meta.json")


@st.dialog("Edit options")
def edit_options(options: dict):
    """
    Project configuration of data options
    - new options can be added/removed for:
        object labels, sources, source limits
    - pre-defined options cannot be edited except for limit values

    Args:
        attempts (dict):
            deepcopy of database of progress/attempt values
        options (dict):
            project unique settings and alternatives
    """
    if not len(options) > 0:
        st.error("Critical data options missing.")
        return
    
    if not st.session_state["dialog_active"]:
        st.session_state["edit_options_complete"] = False
    st.session_state["dialog_active"] = True
    logger.info("Edit options dialog opened")
    TERMS = st.session_state["TERMS"]

    col_main, col_p = st.columns([1, 0.01])
    col_1, col_2, col_3, col_4, col_5 = st.columns([2, 3, 3, 3, 2])
    with col_main:
        with st.container(border=False, height=380):
            # User selection and configuration:
            # - collect databases and define references for editing
            # - set up session state environment and editable options for selection
            if st.session_state["reset_edits"] and st.session_state["changed_options"]:
                st.session_state["reset_edits"] = False
                _reset_changes()
            edit_named_option, selection, no_options, named_option_ref = _initiate_option_edit(TERMS)
            if edit_named_option:
                # Select to add new or remove option if available
                col_a, col_b = st.columns(2)
                if col_a.checkbox("Remove option", value=False, key="remove_option"):
                    _remove_option(col_2, selection, named_option_ref)
                else:
                    # If user selected to edit:
                    not_valid = True

                    # Selected: edit options of a label
                    if selection in [
                            named_option_ref["edit_utility"], 
                            named_option_ref["edit_attribute"], 
                            named_option_ref["edit_origin"]]:
                        not_valid = _edit_label(col_2, selection, not_valid)

                    # Selected: edit source
                    # Requires adding:
                    # - Name of source
                    # - Limit of progress/attempts
                    # - If fail/success states are relevant
                    elif selection == named_option_ref["edit_source"]:
                        _edit_source(col_b, col_2, selection, not_valid)

            # Selected: change limit of existing source
            elif selection == named_option_ref["change_limits"]:
                _edit_limit(col_2, selection)
        
        # Reset button - restores changed_options and changed_progress databases
        no_changes = not st.session_state["edit_options_complete"]
        if col_3.button("Reset", disabled=no_changes, width="stretch"):
            _reset_changes()
    
    # Save button - saves changed_options and changed_progress databases to file
    _save_changes(col_4)


def _initiate_option_edit(TERMS):
    """
    Intiate database deepcopies in session state, 
    create references and lists of editable options.

    Returns:
        Tuple (bool, str, bool, list):
            edit_named_option (bool): selection is a 
            text-based option

            selection (str): selected by user to edit

            no_options (bool): control value if there's nothing to edit

            named_option_ref (list): text-based options and 
            corresponding project term

    """
    # To avoid causing early stage initialization issues,
    # data_access module function are imported here 
    from app.data_access import load_options, load_progress_data
    
    # Setup new databases specifically for editing
    if "changed_options" not in st.session_state:
        st.session_state["changed_options"] = copy.deepcopy(load_options())
    elif not st.session_state["changed_options"]:
        st.session_state["changed_options"] = copy.deepcopy(load_options())
    
    if "changed_options" not in st.session_state:
        st.session_state["changed_progress"] = copy.deepcopy(load_progress_data())
    elif not st.session_state["changed_progress"]:
        st.session_state["changed_progress"] = copy.deepcopy(load_progress_data())

    # Text-based options and project reference
    named_option_ref = {
        "edit_utility": TERMS["utility"],
        "edit_attribute": TERMS["attribute"],
        "edit_origin": TERMS["origin"],
        "edit_source": TERMS["source"],
        "change_limits": f"{TERMS["attempt"]} settings"
    }

    # User selection: what to edit
    selection = st.selectbox(
        "Select option to edit", options=list(named_option_ref.values()), 
        key="options_to_edit", on_change=_reset_changes)
    st.space()
    
    # Initial states
    edit_named_option = False
    remove_options, no_options, requirements = [None]*3
    named_options = list(named_option_ref.values())
    named_options.remove(named_option_ref["change_limits"])
    object_options = named_options.copy()
    object_options.remove(named_option_ref["edit_source"])
    if selection in named_options: 
        # Text-based options
        # selectable options are defined from existing options not in requirements
        edit_named_option = True
        options = st.session_state["changed_options"]
        # Label edits
        if selection in object_options:
            remove_options = options[TERMS["main"]][selection]
        # Source edits
        elif selection == named_option_ref["edit_source"]:
            remove_options = st.session_state["active_trackers"]
        no_options = len(remove_options) < 1
    st.session_state["remove_options"] = remove_options

    return edit_named_option, selection, no_options, named_option_ref


def _reset_changes():
    "Resets databases for editing."
    # To avoid causing early stage initialization issues,
    # data_access module function are imported here 
    from app.data_access import load_options, load_progress_data
    st.session_state["changed_options"] = copy.deepcopy(load_options())
    st.session_state["changed_progress"] = copy.deepcopy(load_progress_data())
    st.session_state["edit_options_complete"] = False
    st.session_state["edited_options"] = list()
    st.session_state["edit_options_complete"] = False
    st.session_state["progress_changed"] = None


def _remove_option(col_2, selection, named_option_ref):
    TERMS = st.session_state["TERMS"]

    # If user selected to remove:
    single_option = False
    if len(st.session_state["remove_options"]) < 2:
        no_options = True
        single_option = True
    else:
        no_options = False
    placeholder = "No removable options" if no_options else None
    
    st.selectbox(
        "Select option", options=st.session_state["remove_options"], 
        key="selected_removal", on_change=_reset_changes, 
        disabled=no_options, placeholder=placeholder)
    if single_option: 
        st.markdown("At least one option required. Add a new one first.")
    if selection == named_option_ref["edit_source"]:
        st.markdown(f"{TERMS["source"]} cannot be removed due to data dependencies, but are instead deactivated. You can re-activate again here.")
    
    # Render confirm button
    # - is disabled if no options exist that isn't in requirements
    if col_2.button("Confirm", disabled=no_options, width="stretch"):
        if selection == named_option_ref["edit_source"]:
            source_selection = st.session_state["selected_removal"]
            # Removing source: remove in both options and progress databases
            # In progress_data: 
            st.session_state["changed_progress"][source_selection]["active"] = False
            st.session_state["progress_changed"] = True
            st.session_state["options_are_edited"] = False
        else:
            st.session_state["progress_changed"] = False
            # Removing labels: remove from selected label's list 
            st.session_state["changed_options"][TERMS["main"]][selection].remove(
                st.session_state["selected_removal"])
        st.session_state["edit_options_complete"] = True
    

def _edit_label(col_2, selection, not_valid):
    TERMS = st.session_state["TERMS"]
    st.session_state["progress_changed"] = False
    st.text_input(
        "Enter name for new option. Mind spelling.", key="new_option")
    
    if st.session_state["new_option"]:
        not_valid, msg = _validity_check(
            name=st.session_state["new_option"])
        if msg: st.markdown(f":red[{msg}]")

    # Confirm input
    if col_2.button(
            "Confirm", disabled=not_valid, width="stretch"): 
        # Adjust format and add to editing database
        st.session_state["changed_options"][TERMS["main"]][selection].append(
            st.session_state["new_option"].capitalize())
        st.session_state["edited_options"].append(selection)
        st.session_state["edit_options_complete"] = True
    
    return not_valid


def _edit_source(col_b, col_2, selection, not_valid):
    TERMS = st.session_state["TERMS"]
    st.session_state["progress_changed"] = True
    reactivate = False
    # Source name
    if not col_b.checkbox(f"Re-activate an inactive", value=False):
        st.text_input(f"Enter name", key="new_option")
    else:
        reactivate = True
        options = [x for x in st.session_state["changed_progress"].keys() if x not in st.session_state["active_trackers"]]
        to_reactivate = st.selectbox(f"Select among inactive {TERMS["source"]}", options=options)
    col_left, col_right = st.columns(2)
    # Source attempt limit
    progress_is_selected = col_left.checkbox(f"Track {TERMS["attempt"]}?", value=True, disabled=reactivate)
    if progress_is_selected:
        new_limit = col_left.number_input(
            f"Enter new max value.", min_value=1, value=100, disabled=reactivate)
    else:
        col_left.number_input(
            f"Enter new max value.", min_value=1, value=100, disabled=True)
        new_limit = None

    # Source states or not
    state_is_selected = col_right.checkbox("Selectable outcomes?", value=True, disabled=reactivate)
    if state_is_selected:
        new_state = f"{TERMS["state_rand"]}" 
    else:
        new_state = None 
        
    if st.session_state["new_option"]:
        not_valid, msg = _validity_check(
            name=st.session_state["new_option"], number=new_limit)
        if msg: st.markdown(f":red[{msg}]")
    elif reactivate and to_reactivate:
        not_valid = False
    
    st.markdown("""***Note:** pages and rows for calculation can be 
                defined in 'Calculate' feature.*""")
    
    # Confirm input
    if col_2.button("Confirm", disabled=not_valid, width="stretch"):
        # Ajust format and add to editing database
        new_option = st.session_state["new_option"]
        st.session_state["changed_options"]["source_limit"][new_option] = new_limit
        st.session_state["changed_options"]["states"][new_option] = state_is_selected
        # Compile and add to editing progress data
        if reactivate:
            st.session_state["changed_progress"][to_reactivate]["active"] = True
            st.session_state["options_are_edited"] = False
        elif progress_is_selected:
            st.session_state["changed_progress"][new_option] = {
                f"{TERMS["attempt"]}": 0,
                "State": new_state,
                "active": True,
                "sets": {
                    "pages": 200,
                    "rows": 5
                }
            }
        else:
            st.session_state["changed_progress"][new_option] = {
                f"{TERMS["attempt"]}": None,
                "State": None,
                "active": True,
                "sets": None
            }

        st.session_state["edited_options"].append(selection)
        st.session_state["edit_options_complete"] = True
    
    return not_valid


def _edit_limit(col_2, selection):
    st.session_state["progress_changed"] = False
    change_general = st.checkbox("Change general settings")
    if change_general:
        
        st.divider()
        col1, col2 = st.columns(2)
        previous_highlight = st.session_state["changed_options"]["user_indicators"]["use_highlights"]
        use_highlights = col1.checkbox("Highlights enabled", value=previous_highlight)
        st.space("small")
        
        disabled_highlights = not use_highlights
        reverse = col2.checkbox(
            """Reverse evaluation:  \n- low is positive  \n- high is negative""",
            value=st.session_state["changed_options"]["user_indicators"]["reverse_positive"], 
            disabled=disabled_highlights)

        col1, col2 = st.columns(2)
        col1.space()
        col2.space()
        previous_low = st.session_state["changed_options"]["user_indicators"]["low_highlight"]
        new_low_text = f"Indication limit for low values. Current value: {previous_low}"
        new_low = col1.number_input(
            new_low_text, min_value=0, max_value=100, 
            value=previous_low, disabled=disabled_highlights)
        
        previous_high = st.session_state["changed_options"]["user_indicators"]["high_highlight"]
        new_high_text = f"Indication limit for high values. Current value: {previous_high}"
        new_high = col2.number_input(
            new_high_text, min_value=0, max_value=100, 
            value=previous_high, disabled=disabled_highlights)
    else:
        all_options = st.session_state["changed_options"]["source_limit"]
        limit_options = list()
        st.space()
        col1, col2 = st.columns(2)
        for x in limit_options:
            if st.session_state["changed_options"]["states"][x]:
                limit_options.append(x)
        source_selection = col1.selectbox(
            "Select source to change", options=limit_options)
        if source_selection:
            current_value = all_options[source_selection]
            new_limit = col2.number_input(
                f"Enter new max value. Current value: {current_value}", min_value=0, value=current_value)
        else:
            new_limit = col2.number_input(
                f"Enter new max value.", min_value=0, disabled=True)

    # Confirm input
    if col_2.button("Confirm", width="stretch"):
        if change_general:
            st.session_state["changed_options"]["user_indicators"]["use_highlights"] = use_highlights
            st.session_state["changed_options"]["user_indicators"]["reverse_positive"] = reverse
            st.session_state["changed_options"]["user_indicators"]["high_highlight"] = new_high
            st.session_state["changed_options"]["user_indicators"]["low_highligh"] = new_low
        else:
            category = source_selection
            st.session_state["changed_options"]["source_limit"][category] = new_limit
        st.session_state["edited_options"].append(selection)
        st.session_state["edit_options_complete"] = True


def _validity_check(name: str = False, number: int = False) -> tuple:
    """Checks if input meets requirement in format
    
    Returns:
        Tuple (bool, str | None):
            (bool): confirm all requirements are met
            (str | None): message for user tip
    """
    # Message values for all potential errors
    msg, msg_len, msg_sym, msg_ini, msg_val = [str()]*5
    
    # Text requirements checks:
    # - length
    # - extra whitespaces
    # - invalid symbols
    if name:
        valid_symbols = ("-", " ")
        max_length = 40
        min_length = 0
        msg_len = "Too long. "
        length_check = len(name) > min_length and len(name) < max_length

        if length_check:
            symbol_check = True
            if not name.isalnum():
                for symbol in name:
                    if not symbol.isalnum() and symbol not in valid_symbols:
                        symbol_check = False
                        msg_sym = "Invalid characters. "
            if "  " in name:
                symbol_check = False
                msg_sym = "Double whitespace. "
            if name[0] in ("-", " "):
                symbol_check = False
                msg_ini = "Invalid first character. "
        else:
            symbol_check = None        
    else:
        symbol_check = True
        length_check = True
    # Number requirement checks: min and max values
    if number:
        num_check = True
        max_value = None
        min_value = 0
        if min_value:
            if number < min_value:
                num_check = False
                msg_val = "Too low. "
        if max_value:
            if number > max_value:
                num_check = False
                msg_val = "Too high. "
    else:
        num_check = True

    # Construct message of all errors, if any
    msg += f"{msg_len}{msg_sym}{msg_ini}{msg_val}"
    if all([length_check, symbol_check, num_check]):
        return False, None
    else:
        return True, msg


def _save_changes(col_4):
    from app.initialize import arciv

    DATAPATH = st.session_state["DATAPATH"]
    SETTINGS = st.session_state["SETTINGS"]
    TERMS = st.session_state["TERMS"]

    not_complete = any([not st.session_state["edit_options_complete"], 
                        st.session_state["progress_changed"] is None])
    if col_4.button("Save", disabled=not_complete, type="primary", width="stretch"):
        # Saving progress data
        if st.session_state["progress_changed"]:
            logger.info(f"Update was requrested for {DATAPATH["progress"]}")
            error.catch_data(
                st.session_state["changed_progress"], 
                DATAPATH["progress"], TERMS["progress"])
            if arciv.backup(
                    [101, 47, 19, 7, 3], TERMS["progress"], 
                    set_file=DATAPATH["progress"], empty_allowed=True):
                arciv.writer(
                    st.session_state["changed_progress"], object_type=TERMS["progress"], 
                    set_file=DATAPATH["progress"], join_path="data")
        # Saving options data
        if st.session_state["options_are_edited"]:
            logger.info(f"Update was requrested for {SETTINGS["Options"]}")
            error.catch_data(
                st.session_state["changed_options"], 
                SETTINGS["Options"], "options")
            if arciv.backup(
                    [7, 5, 3, 1], "options", 
                    set_file=SETTINGS["Options"], empty_allowed=True): 
                arciv.writer(
                    st.session_state["changed_options"], 
                    set_file=SETTINGS["Options"], join_path="settings")
        st.session_state["processed_edits"] = True
        st.rerun()