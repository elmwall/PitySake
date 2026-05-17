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

    # Store config dictionaries in session state
    for dictionary, content in config.items():
        st.session_state[dictionary] = content
    for key, path in st.session_state["DIRECTORIES"].items():
        st.session_state["DIRECTORIES"][key] = os.path.join(project_name, path)

    # st.session_state["project"] = 
    st.session_state["meta"] = arch.reader(other_file="meta.json")
    # project_meta = arch.reader(other="meta.json", join_path="settings")

    # project_nomatch = last_session_meta["project"] != project_name
    # theme_nomatch = last_session_meta["theme"] != project_meta["theme"]
    # if project_nomatch or theme_nomatch:
    #     st.session_state["adjust_theme"] = True


@st.dialog("Edit options")
def edit_options(attempts: dict, options: dict):
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
    from app.initialize import arciv
    st.session_state["dialog_active"] = True
    logger.info("Edit options dialog opened")

    DATAPATH = st.session_state["DATAPATH"]
    SETTINGS = st.session_state["SETTINGS"]
    TERMS = st.session_state["TERMS"]
    # arciv = Archivist(DIRECTORIES, DATAPATH, "nofile")
    # Control values for registred edits
    st.session_state["edited_options"] = list()
    st.session_state["edit_options_complete"] = False
    progress_changed = False

    col_main, col_p = st.columns([1, 0.01])
    col_1, col_2, col_3, col_4, col_5 = st.columns([2, 3, 3, 3, 2])
    with col_main:
        with st.container(border=False, height=330):
            # User selection and configuration:
            # - collect databases and define references for editing
            # - set up session state environment and editable options for selection
            edit_named_option, selection, no_options, named_option_ref = _initiate_option_edit(TERMS)
            if edit_named_option:
                # Select to add new or remove option if available
                if st.checkbox("Remove option", value=False, key="remove_option"):
                    # If user selected to remove:
                    placeholder = "No removable options" if no_options else None
                    st.selectbox(
                        "Select option", options=st.session_state["remove_options"], 
                        key="selected_removal", on_change=_reset_changes, 
                        disabled=no_options, placeholder=placeholder)
                    
                    # Render confirm button
                    # - is disabled if no options exist that isn't in requirements
                    if col_2.button("Confirm", disabled=no_options, width="stretch"):
                        if selection == named_option_ref["edit_source"]:
                            # Removing source: remove in both options and progress databases
                            # In data_options: Registered sources
                            st.session_state["changed_options"]["source"].remove(
                                st.session_state["selected_removal"].capitalize())
                            # In data_options: Source limits
                            st.session_state["changed_options"]["limit"].pop(
                                st.session_state["selected_removal"].capitalize())
                            # In progress_data: 
                            st.session_state["changed_progress"].pop(
                                st.session_state["selected_removal"].capitalize())
                        else:
                            # Removing labels: remove from selected label's list 
                            st.session_state["changed_options"][TERMS["main"]][selection].remove(
                                st.session_state["selected_removal"])
                        st.session_state["edit_options_complete"] = True

                else:
                    # If user selected to add:
                    not_valid = True

                    # Selected: edit options of a label
                    if selection in [
                            named_option_ref["edit_utility"], 
                            named_option_ref["edit_attribute"], 
                            named_option_ref["edit_origin"]]:
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

                    # Selected: edit source
                    # Requires adding:
                    # - Name of source
                    # - Limit of progress/attempts
                    # - If fail/success states are relevant
                    elif selection == named_option_ref["edit_source"]:
                        # Source name
                        st.text_input(
                            f"Enter name for new {TERMS["source"]}. Mind spelling.", 
                            key="new_option")
                        col_left, col_right = st.columns(2)
                        # Source attempt limit
                        new_limit = col_left.number_input(
                            f"Enter new max value.", min_value=1)
                        state_options = [f"{TERMS["state"]}", "Constant"]
                        # Source states or not
                        selected_state = col_right.selectbox(
                            "Set state options", options=state_options)
                        if selected_state == "Constant":
                            new_state = None  
                        else:
                            new_state = f"{TERMS["state"]}"
                            
                        if st.session_state["new_option"]:
                            not_valid, msg = _validity_check(
                                name=st.session_state["new_option"], number=new_limit)
                            if msg: st.markdown(f":red[{msg}]")
                        
                        # Confirm input
                        if col_2.button(
                                "Confirm", disabled=not_valid, width="stretch"):
                            progress_changed = True
                            # Ajust format and add to editing database
                            new_option = st.session_state["new_option"].capitalize()
                            st.session_state["changed_options"]["source"].append(new_option)
                            st.session_state["changed_options"]["limit"][new_option] = new_limit
                            # Compile and add to editing progress data
                            st.session_state["changed_progress"][new_option] = {
                                f"{TERMS["attempt"]}": 0,
                                f"{TERMS["state"]}": new_state,
                                "limit": new_limit}
                            st.session_state["edited_options"].append(selection)
                            st.session_state["edit_options_complete"] = True

            # Selected: change limit of existing source
            elif selection == named_option_ref["change_limits"]:
                change_general = st.checkbox("Change general limits")
                if change_general:
                    new_limit_text = f"""Calculator limit. Current value: 
                        {st.session_state["changed_options"]["value_limits"]["general_limit"]}"""
                    
                    new_limit = st.number_input(
                        new_limit_text, min_value=0, 
                        value=st.session_state["changed_options"]["value_limits"]["general_limit"])
                    st.space("small")
                    col1, col2 = st.columns(2)

                    previous_low = st.session_state["changed_options"]["user_indicators"]["low_highligh"]
                    new_low_text = f"Indication limit for low values. Current value: {previous_low}"
                    new_low = col1.number_input(
                        new_low_text, min_value=0, max_value=new_limit, value=previous_low)
                    
                    previous_high = st.session_state["changed_options"]["user_indicators"]["high_highlight"]
                    new_high_text = f"Indication limit for high values. Current value: {previous_high}"
                    new_high = col2.number_input(
                        new_high_text, min_value=1, max_value=new_limit, value=previous_high)
                    
                    reverse = st.checkbox(
                        "Reverse evaluation: low is positive, high is negative",
                        value=st.session_state["changed_options"]["user_indicators"]["reverse_positive"])
                else:
                    limit_options = st.session_state["changed_options"]["limit"]
                    limit_cat = st.selectbox(
                        "Select category to change", options=limit_options.keys())
                    # Main and secondary sources each have a Temp and Mixed type source,
                    # with separate limits
                    if type(limit_options[limit_cat]) is dict:
                        limit_subcat_options = limit_options[limit_cat].keys()
                        no_sub = False
                    # Other sources are not exlusively for main or secondary
                    # and only carries limit value in data_options
                    else:
                        limit_subcat_options = None
                        no_sub = True
                    limit_subcat = st.selectbox(
                        "Select subcategory", 
                        options=limit_subcat_options, disabled=no_sub)
                    if no_sub:
                        current_value = limit_options[limit_cat]
                    else:
                        current_value = limit_options[limit_cat][limit_subcat]
                        
                    new_limit = st.number_input(
                        f"Enter new max value. Current value: {current_value}", min_value=0, value=current_value)
                    
                not_valid, msg = _validity_check(number=new_limit)

                # Confirm input
                if col_2.button("Confirm", disabled=not_valid, width="stretch"):
                    if change_general:
                        st.session_state["changed_options"]["value_limits"]["general_limit"] = new_limit
                        st.session_state["changed_options"]["user_indicators"]["reverse_positive"] = reverse
                        st.session_state["changed_options"]["user_indicators"]["high_highlight"] = new_high
                        st.session_state["changed_options"]["user_indicators"]["low_highligh"] = new_low
                    else:
                        progress_changed = True
                        if no_sub:
                            cat = limit_cat.capitalize()
                            st.session_state["changed_options"]["limit"][cat] = new_limit
                            st.session_state["changed_progress"][cat]["limit"] = new_limit
                        else:
                            cat = limit_cat.capitalize()
                            subcat = limit_subcat.capitalize()
                            st.session_state["changed_options"]["limit"][cat][subcat] = new_limit
                            st.session_state["changed_progress"][f"{cat} {subcat}"]["limit"] = new_limit
                    st.session_state["edited_options"].append(selection)
                    st.session_state["edit_options_complete"] = True
        
        # Reset button - restores changed_options and changed_progress databases
        no_changes = not st.session_state["edit_options_complete"]
        if col_3.button("Reset", disabled=no_changes, width="stretch"):
            _reset_changes()
        edited_str = str()
    
    # Save button - saves changed_options and changed_progress databases to file
    not_complete = not st.session_state["edit_options_complete"]
    if col_4.button("Save", disabled=not_complete, width="stretch"):
        if progress_changed:
            logger.info(f"Update called for {DATAPATH["progress"]}")
            arciv.writer(
                st.session_state["changed_progress"], object_type=TERMS["progress"], 
                other_file=DATAPATH["progress"], join_path="data")
        error.catch_data(
            st.session_state["changed_options"], 
            SETTINGS["Options"], "options")
        logger.info(f"Update called for {SETTINGS["Options"]}")
        if arciv.backup(
                [7, 5, 3, 1], "options", other_file=SETTINGS["Options"]): 
            arciv.writer(
                st.session_state["changed_options"], 
                other_file=SETTINGS["Options"], join_path="settings")
        st.session_state["processed_edits"] = True
        st.rerun()

    # Indication for user that changes are registered
    for x in st.session_state["edited_options"]:
        edited_str += f"{x} "
    if len(edited_str) > 0: 
        st.markdown(f"Changes made in: {edited_str}")
    else:
        st.markdown("No changes")


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
    # to avoid causing early stage initialization issues,
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
        "change_limits": f"{TERMS["attempt"]} limits"
    }

    # User selection: what to edit
    selection = st.selectbox(
        "Select option to edit", options=list(named_option_ref.values()), 
        key="options_to_edit", on_change=_reset_changes)
    
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
            requirements = options[f"{TERMS["main"]}_required"][selection]
            selection_options = options[TERMS["main"]][selection]
            remove_options = [x for x in selection_options if x not in requirements]
        # Source edits
        elif selection == named_option_ref["edit_source"]:
            requirements = options["source_required"]
            remove_options = [x for x in options["source"] if x not in requirements]
        no_options = len(remove_options) < 1
    st.session_state["remove_options"] = remove_options

    return edit_named_option, selection, no_options, named_option_ref


def _reset_changes():
    "Resets databases for editing."
    # to avoid causing early stage initialization issues,
    # data_access module function are imported here 
    from app.data_access import load_options, load_progress_data
    st.session_state["changed_options"] = copy.deepcopy(load_options())
    st.session_state["changed_progress"] = copy.deepcopy(load_progress_data())
    st.session_state["edit_options_complete"] = False


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