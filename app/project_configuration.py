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


@st.cache_data
def initialize_constants(project_name: str) -> tuple:
    """
    Collect and initialize project settings
    - collects settings dictionaries via file_manager Archivist
    - initializes configuration values in session state

    Args:
        project_name (str):
            name of main file and folder for the specific project
        
    Returns:
        DATAPATH (dict):
            names of data files
        DIRECTORIES (dict):
            names of folders
        SETTINGS (dict):
            names settings files
        TERMS (dict):
            project unique terms
        
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
            st.markdown("""A generic version can be found 
                        [here](https://github.com/elmwall/PitySake/blob/main/user_project/settings/config.json). 
                        Place it in the folder above.""")
        quit()

    # Store config dictionaries in session state
    for dictionary, content in config.items():
        st.session_state[dictionary] = content

    DATAPATH = config["DATAPATH"]
    DIRECTORIES = config["DIRECTORIES"]
    SETTINGS = config["SETTINGS"]
    TERMS = config["TERMS"]

    # DIRECTORIES = st.session_state.get("DIRECTORIES", None)
    if DIRECTORIES:
        for key, path in DIRECTORIES.items():
            config["DIRECTORIES"][key] = os.path.join(project_name, path)
            # st.session_state["DIRECTORIES"][key] = os.path.join(project_name, path)
    else:
        msg = "Collecting directories failed."
        logger.error("File directories could not be retrieved from config.json.")
        if not "error" in st.session_state:
            error.message(
                message=msg, stage="Project configuration", 
                file="settings\\config.json")

    return DATAPATH, DIRECTORIES, SETTINGS, TERMS


@st.dialog("Edit options")
def edit_options(options: dict):
    """
    Project configuration of data options
    - new options can be added/removed for:
        object labels, sources, source limits  
        (removed sources are simply disabled)
    - pre-defined options can be edited for:  
        source limits, highlights enabling and triggers

    Args:
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

    from app.initialize import DATAPATH, DIRECTORIES, SETTINGS, TERMS

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
            edit_named_option, selection, source_options = _initiate_option_edit(TERMS)
            if edit_named_option:
                # Select to add new or remove option if available
                col_a, col_b = st.columns(2)
                if col_a.checkbox("Remove option", value=False, key="remove_option"):
                    _remove_option(col_2, TERMS, selection)
                else:
                    # If user selected to edit
                    # Selected: edit options of a label
                    if selection in ["utility", "attribute", "origin"]:
                        _edit_label(col_2, TERMS, selection)

                    # Selected: edit source
                    # Requires adding:
                    # - Name of source
                    # - Limit of progress/attempts
                    # - If fail/success states are relevant
                    elif selection == "edit_source":
                        _edit_source(col_b, col_2, TERMS, source_options)

            # Selected: change limit of existing source
            elif selection == "change_limits":
                _edit_value_settings(col_2, TERMS, source_options)
        
        # Reset button - restores changed_options and changed_progress databases
        no_changes = not st.session_state["edit_options_complete"]
        if col_3.button("Reset", disabled=no_changes, width="stretch"):
            _reset_changes()
    
    # Save button - saves changed_options and changed_progress databases to file
    _save_changes(col_4, DATAPATH, SETTINGS, TERMS)


def _initiate_option_edit(TERMS: dict) -> tuple:
    """
    Intiate database deepcopies in session state, 
    create references and lists of editable options.

    Returns:
        Tuple (bool, str):
            edit_named_option (bool): selection is a 
            text-based option

            selection (str): selected by user to edit
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
    source_options = list(st.session_state["changed_progress"].keys())

    # Text-based options and project reference
    named_option_ref = {
        "utility": f"Label: {TERMS["utility"]}",
        "attribute": f"Label: {TERMS["attribute"]}",
        "origin": f"Label: {TERMS["origin"]}",
        "edit_source": f"Source: {TERMS["source"]}",
        "change_limits": f"{TERMS["source"]} and {TERMS["attempt"]} settings"
    }

    # User selection: what to edit
    named_options = list(named_option_ref.keys())
    selection = st.selectbox(
        "Select option to edit", options=named_options, 
        format_func=lambda x:named_option_ref[x],
        key="options_to_edit", on_change=_reset_changes)
    st.space()
    
    # Initial states
    edit_named_option = False
    remove_options = list()
    named_options.remove("change_limits")
    object_options = named_options.copy()
    object_options.remove("edit_source")
    if selection in named_options: 
        # Text-based options
        # selectable options are defined from existing options not in requirements
        edit_named_option = True
        options = st.session_state["changed_options"]
        # Label edits
        if selection in object_options:
            remove_options = options[TERMS["main"]][TERMS[selection]]
        # Source edits
        elif selection == "edit_source":
            remove_options = st.session_state["active_trackers"].keys()
    st.session_state["remove_options"] = remove_options

    return edit_named_option, selection, source_options


def _reset_changes():
    "Resets databases for editing."
    # To avoid causing early stage initialization issues,
    # data_access module function are imported here 
    from app.data_access import load_options, load_progress_data
    st.session_state["changed_options"] = copy.deepcopy(load_options())
    st.session_state["changed_progress"] = copy.deepcopy(load_progress_data())
    st.session_state["edit_options_complete"] = False
    st.session_state["edit_options_complete"] = False
    # Value for progress_is_changed is set to None to separate initial state
    # and edited states (True/False)
    st.session_state["progress_is_changed"] = None


def _remove_option(col_2, TERMS: dict, selection: str):
    """
    For labels: removes from data_options  
    For sources: sets source inactive in progress

    Args:
        col_2 (DeltaGenerator):
            Streamlit column instance
        selection (str):
            selected editing option

    Updates for: 
    - Progress: sources
    - Options: labels
    """
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
    if selection in ["utility", "attribute", "origin"]:
        st.markdown("Removing labels will not change labels on registered objects.")
        st.markdown("To change labels on objects, use 'Edit details' in *Update library*.")
    elif selection == "edit_source":
        st.markdown(f"""{TERMS["source"]} cannot be removed due to data dependencies, 
                    but are instead deactivated.""")
        st.markdown("You can re-activate here by choosing 'Re-activate an inactive.'")
    
    # Render confirm button
    # - is disabled if no options exist that isn't in requirements
    if col_2.button("Confirm", disabled=no_options, width="stretch"):
        if selection == "edit_source":
            source_selection = st.session_state["selected_removal"]
            # Removing source: set active as False
            # Timeline is dependent on source data refered to by registered objects
            # even if they are removed
            st.session_state["changed_progress"][source_selection]["active"] = False
            st.session_state["progress_is_changed"] = True
            st.session_state["options_are_edited"] = False
        else:
            # Removing labels: remove from selected label's list 
            # Data views are not dependent on labels in option, 
            # only on the labels attached to objects
            st.session_state["changed_options"][TERMS["main"]][TERMS[selection]].remove(
                st.session_state["selected_removal"])
            st.session_state["progress_is_changed"] = False
        st.session_state["edit_options_complete"] = True
    

def _edit_label(col_2, TERMS: dict, selection: str) -> bool:
    """
    Change object labels available

    Args:
        col_2 (DeltaGenerator):
            Streamlit column instance
        selection (str):
            selected editing option

    Updates for: 
    - Options: labels
    """
    st.session_state["progress_is_changed"] = False
    
    add_blank = st.checkbox("Add a blank")
    new_option = st.text_input(
        "Enter name for new option. Mind spelling and case.", 
        key="new_option", on_change=_changed, disabled=add_blank)
    if add_blank: new_option = "_Blank_"
    
    not_valid = True
    existing_options = st.session_state["changed_options"][TERMS["main"]][TERMS[selection]]
    if new_option and existing_options and st.session_state["field_changed"]:
        not_valid, msg = _validity_check(
            name=new_option, existing_options=existing_options)
        if msg: st.markdown(f":red[{msg}]")

    # Confirm input
    if col_2.button(
            "Confirm", on_click=_change_confirmed, disabled=not_valid, width="stretch"): 
        # Adjust format and add to editing database
        st.session_state["changed_options"][TERMS["main"]][TERMS[selection]].append(new_option)
        st.session_state["edit_options_complete"] = True


def _edit_source(col_b, col_2, TERMS: dict, source_options) -> bool:
    """
    Adding a new source or re-activating an inactive

    Args:
        col_b (DeltaGenerator):
            Streamlit column instance
        col_2 (DeltaGenerator):
            Streamlit column instance

    Updates for: 
    - Progress: adding new source; shifting active
    - Options: adding new source
    """
    st.session_state["progress_is_changed"] = True
    reactivate = False
    col_left, col_right = st.columns(2)
    # Source name
    if not col_b.checkbox(f"Re-activate an inactive", value=False):
        new_option = col_left.text_input(f"Enter name", key="new_option", on_change=_changed)
    else:
        reactivate = True
        options = [x for x in source_options if x not in st.session_state["active_trackers"]]
        to_reactivate = st.selectbox(f"Select among inactive {TERMS["source"]}", options=options)
        new_option = None
    # col_left, col_right = st.columns(2)

    # Source attempt limit
    col_L, col_R = st.columns(2)
    col_right.space(30)

    progress_is_selected = col_L.checkbox(
        f"Track {TERMS["attempt"]}?", value=True, disabled=reactivate)
    if progress_is_selected:
        new_limit = col_L.number_input(
            f"Enter new max value.", min_value=1, value=100, disabled=reactivate)
    else:
        col_L.number_input(
            f"Enter new max value.", min_value=1, value=100, disabled=True)
        new_limit = None

    not_valid = True
    if new_option and st.session_state["field_changed"]:
        not_valid, msg = _validity_check(
            name=new_option, number=new_limit, existing_options=source_options)
        if msg: col_right.markdown(f":red[{msg}]")
    elif reactivate and to_reactivate:
        not_valid = False
    
    # Source states or not 
    col_left.space()
    state_is_selected = col_R.checkbox(
        "Selectable outcomes?", value=True, disabled=reactivate)
    if state_is_selected:
        new_state = f"{TERMS["state_rand"]}" 
    else:
        new_state = None 
    
    st.markdown("""***Note:** sets for calculation can be 
                defined in 'Calculate' feature.*""")
    
    # Confirm input
    if col_2.button("Confirm", on_click=_change_confirmed, disabled=not_valid, width="stretch"):
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
                    "sections": 200,
                    "positions": 5}}
        else:
            st.session_state["changed_progress"][new_option] = {
                f"{TERMS["attempt"]}": None,
                "State": None,
                "active": True,
                "sets": None}

        st.session_state["edit_options_complete"] = True


def _edit_value_settings(col_2, TERMS: dict, source_options):
    """
    Changing source limits, highlights enabling and triggers

    Args:
        col_2 (DeltaGenerator):
            Streamlit column instance

    Updates for: 
    - Options: source limits; user indicators
    """
    st.session_state["progress_is_changed"] = False
    st.space(4)

    # View settings - independent of source
    change_general = st.checkbox("Change general settings")
    if change_general:
        user_indicators = st.session_state["changed_options"]["user_indicators"]
        st.divider()
        col1, col2 = st.columns(2)
        previous_highlight = user_indicators["use_highlights"]
        use_highlights = col1.checkbox("Highlights enabled", value=previous_highlight)
        st.space("small")
        
        disabled_highlights = not use_highlights
        reverse = col2.checkbox(
            """Reverse evaluation:  \n- low is positive  \n- high is negative""",
            value=user_indicators["reverse_positive"], 
            disabled=disabled_highlights)

        col1, col2 = st.columns(2)
        col1.space()
        col2.space()
        previous_low = user_indicators["low_highlight"]
        new_low_text = f"Indication limit for low values. Current value: {previous_low}"
        new_low = col1.number_input(
            new_low_text, min_value=0, max_value=100, 
            value=previous_low, disabled=disabled_highlights)
        
        previous_high = user_indicators["high_highlight"]
        new_high_text = f"Indication limit for high values. Current value: {previous_high}"
        new_high = col2.number_input(
            new_high_text, min_value=0, max_value=100, 
            value=previous_high, disabled=disabled_highlights)
        
    # Source limit settings
    else:
        all_options = st.session_state["changed_options"]["source_limit"]
        limit_options = [x for x in source_options if all([
            x in st.session_state["active_trackers"].keys(), 
            st.session_state["changed_progress"][x][TERMS["attempt"]] is not None])]
        st.space()
        col1, col2 = st.columns(2)
        source_selection = col1.selectbox(
            "Select source to change", options=limit_options)
        if source_selection:
            current_value = all_options[source_selection]
            new_limit = col2.number_input(
                "Enter new max value.", min_value=0, value=current_value)
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
        st.session_state["edit_options_complete"] = True


def _changed():
    st.session_state["field_changed"] = True

def _change_confirmed():
    st.session_state["field_changed"] = False


def _validity_check(name: str | bool = False, number: int | bool = False, 
                    existing_options: list | None = None) -> tuple:
    """Checks if input meets requirement in format

    Args:
        name (str):
            text input
        number (int):
            number input
        existing_options (list):
            options not available for new names
    
    Returns:
        Tuple (bool, str | None):
            (bool): confirm all requirements are met
            (str | None): message for user tip
    """
    # Message values for all potential errors
    msg, msg_len, msg_sym, msg_ini, msg_val, msg_ext = [str()]*6
    # Text requirements checks: 
    # - length
    # - extra whitespaces
    # - invalid symbols
    exist_check = False
    symbol_check = False
    length_check = False
    num_check = True
    if name and existing_options:
        num_check = True
        max_length = 40
        min_length = 0
        length_check = len(name) > min_length and len(name) < max_length
        if name in existing_options:
            msg_ext = "Already exists. "
        else:
            exist_check = True

        if length_check:
            symbol_check = True
            if not name.isalnum():
                valid_symbols = st.session_state["valid_symbols"]
                for symbol in name:
                    if not symbol.isalnum() and symbol not in valid_symbols:
                        msg_sym = "Invalid characters. "
            if "  " in name:
                
                msg_sym = "Double whitespace. "
            if name[0] in (" ", ):
                msg_ini = "Invalid first character. "
        else:
            symbol_check = None
            msg_len = "Too long. "

    # Number requirement checks: min and max values
    if number:
        if not name: exist_check = True
        symbol_check = True
        length_check = True
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
    # Construct message of all errors, if any
    msg += f"{msg_ext}{msg_len}{msg_sym}{msg_ini}{msg_val}"
    if all([exist_check, length_check, symbol_check, num_check]):
        return False, None
    else:
        return True, msg


def _save_changes(col_4, DATAPATH: dict, SETTINGS: dict, TERMS: dict):
    """
    If all required fields are complete, enable save button.  
    Save button refers file for backup and sends info for writing file.

    Args:
        col_4 (DeltaGenerator):
            Streamlit column instance
    """
    from app.initialize import arciv

    progress_is_changed = st.session_state["progress_is_changed"]
    not_complete = any([not st.session_state["edit_options_complete"], 
                        progress_is_changed is None])
    if col_4.button("Save", disabled=not_complete, type="primary", width="stretch"):
        # Saving progress data
        if progress_is_changed:
            changed_progress = st.session_state["changed_progress"]
            progress_path = DATAPATH["progress"]
            progress_ref = TERMS["progress"]
            logger.info(f"Update was requrested for {progress_path}")
            error.catch_data(
                changed_progress, progress_path, progress_ref)
            if arciv.backup(
                    [101, 47, 19, 7, 3], progress_ref, join_path="data",
                    set_file=progress_path, empty_allowed=True):
                arciv.writer(
                    changed_progress, object_type=progress_ref, 
                    set_file=progress_path, join_path="data")
        # Saving options data
        if st.session_state["options_are_edited"]:
            options_path = SETTINGS["Options"]
            changed_options = st.session_state["changed_options"]
            logger.info(f"Update was requrested for {options_path}")
            error.catch_data(
                changed_options, 
                options_path, "options")
            if arciv.backup(
                    [7, 5, 3, 1], "options", join_path="settings", 
                    set_file=options_path, empty_allowed=False): 
                arciv.writer(
                    changed_options, 
                    set_file=options_path, join_path="settings")
        st.session_state["processed_edits"] = True
        st.rerun()