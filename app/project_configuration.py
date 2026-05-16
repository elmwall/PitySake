"""
Connector to project data

Manages:
- retrieves project settings
- setup config values in Streamlit session state
"""

import copy
import logging

import streamlit as st

from app.file_manager import Archivist
import app.data_access as hold


DATAPATH = st.session_state["DATAPATH"]
DIRECTORIES = st.session_state["DIRECTORIES"]
SETTINGS = st.session_state["SETTINGS"]
TERMS = st.session_state["TERMS"]

arciv = Archivist(DIRECTORIES, DATAPATH, "nofile")
attempt_ref = TERMS["attempt"]
attribute_ref = TERMS["attribute"]
event_ref = TERMS["event"]
main_ref = TERMS["main"]
origin_ref = TERMS["origin"]
progress_ref = TERMS["progress"]
secondary_ref = TERMS["secondary"]
source_ref = TERMS["source"]
state_ref = TERMS["state"]
staterand_ref = TERMS["state_rand"]
utility_ref = TERMS["utility"]
utility_sec_ref = TERMS["secondary_utility"]
logger = logging.getLogger(__name__)


def initialize_constants(project_name: str):
    """
    Collect and initialize project settings
    - collects settings dictionaries via file_manager Archivist
    - initializes configuration values in session state
    """

    logger.info("Running config_hub.initialize_constants")

    # Use case for Archivist for unique single path-file:
    # - setup None-values for irrelevant references
    # - join_path with project_name/settings and project-unique config.json
    arch = Archivist(
        DIRECTORIES={
            "DataFolder": None,
            "SettingsFolder": f"{project_name}/settings",
            "BackupFolder": None},
        DATAPATH={"backup_meta": None},
        file="config.json",
        initialized=False)
    config = arch.reader(join_path="settings")

    # Store config dictionaries in session state
    for dictionary, content in config.items():
        st.session_state[dictionary] = content


@st.dialog("Edit options")
def edit_options(attempts, options):
    logger.info("Running object_info_manager.Secretary.edit_options @st.dialog")

    st.session_state["edit_options_complete"] = False
    st.session_state["dialog_active"] = False
    col_main, col_p = st.columns([1, 0.01])
    col_1, col_2, col_3, col_4, col_5 = st.columns([2, 3, 3, 3, 2])
    st.session_state["edited_options"] = list()
    with col_main:
        with st.container(border=False, height=310):
            name_edit, selection, no_options, option_ref = _initiate_option_edit(attempts, options)     
            if name_edit:
                if st.checkbox("Remove option", value=False, key="remove_option"):
                    placeholder = "No removable options" if no_options else None
                    st.selectbox(
                        "Select option", options=st.session_state["remove_options"], 
                        key="selected_removal", on_change=_reset_changes, 
                        disabled=no_options, placeholder=placeholder)
                    if col_2.button("Confirm", disabled=no_options, width="stretch"):
                        if selection == option_ref["edit_source"]:
                            st.session_state["changed_options"]["source"].remove(
                                st.session_state["selected_removal"].capitalize())
                            st.session_state["changed_options"]["limit"].pop(
                                st.session_state["selected_removal"].capitalize())
                            st.session_state["changed_progress"].pop(
                                st.session_state["selected_removal"].capitalize())
                        else:
                            st.session_state["changed_options"][main_ref][selection].remove(
                                st.session_state["selected_removal"])
                        st.session_state["edit_options_complete"] = True
                else:
                    not_valid = True
                    if selection in [option_ref["edit_utility"], option_ref["edit_attribute"], option_ref["edit_origin"]]:
                        st.text_input(
                            "Enter name for new option. Mind spelling.", key="new_option")
                        if st.session_state["new_option"]:
                            not_valid, msg = _validity_check(
                                name=st.session_state["new_option"])
                            if msg: st.markdown(f":red[{msg}]")
                        if col_2.button(
                                "Confirm", disabled=not_valid, width="stretch"): 
                            st.session_state["changed_options"][main_ref][selection].append(
                                st.session_state["new_option"].capitalize())
                            st.session_state["edited_options"].append(selection)
                            st.session_state["edit_options_complete"] = True
                    elif selection == option_ref["edit_source"]:
                        st.text_input(
                            f"Enter name for new {source_ref}. Mind spelling.", 
                            key="new_option")
                        col_left, col_right = st.columns(2)
                        new_limit = col_left.number_input(
                            f"Enter new max value.", min_value=1)
                        state_options = [f"{staterand_ref}", "Constant"]
                        selected_state = col_right.selectbox("Set state options", options=state_options)
                        if selected_state == "Constant":
                            new_state = None  
                        else:
                            new_state = f"{staterand_ref}"
                        if st.session_state["new_option"]:
                            not_valid, msg = _validity_check(
                                name=st.session_state["new_option"], number=new_limit)
                            if msg: st.markdown(f":red[{msg}]")
                        if col_2.button(
                                "Confirm", disabled=not_valid, width="stretch"):
                            st.session_state["changed_options"]["source"].append(
                                st.session_state["new_option"].capitalize())
                            st.session_state["changed_options"]["limit"][st.session_state["new_option"].capitalize()] = new_limit
                            st.session_state["changed_progress"][st.session_state["new_option"].capitalize()] = {
                                f"{attempt_ref}": 0,                                
                                f"{state_ref}": new_state,
                                "limit": new_limit,                             
                            }
                            st.session_state["edited_options"].append(selection)
                            st.session_state["edit_options_complete"] = True
            elif selection == option_ref["change_limits"]:
                limit_options = options["limit"]
                limit_cat = st.selectbox(
                    "Select category to change", options=limit_options.keys())
                if type(limit_options[limit_cat]) is dict:
                    limit_subcat_options = limit_options[limit_cat].keys()
                    no_sub = False
                else:
                    limit_subcat_options = None
                    no_sub = True
                
                limit_subcat = st.selectbox(
                    "Select subcategory", 
                    options=limit_subcat_options, disabled=no_sub)
                current_value = limit_options[limit_cat] if no_sub else limit_options[limit_cat][limit_subcat]
                new_limit = st.number_input(
                    f"Enter new max value. Current value: {current_value}", min_value=0)
                not_valid, msg = _validity_check(number=new_limit)
                if col_2.button("Confirm", disabled=not_valid, width="stretch"):
                    if no_sub:
                        st.session_state["changed_options"]["limit"][limit_cat.capitalize()] = new_limit
                        st.session_state["changed_progress"][limit_cat.capitalize()]["limit"] = new_limit
                    else:
                        st.session_state["changed_options"]["limit"][limit_cat.capitalize()][limit_subcat] = new_limit
                        st.session_state["changed_progress"][f"{limit_cat.capitalize()} {limit_subcat.capitalize()}"]["limit"] = new_limit
                    st.session_state["edited_options"].append(selection)
                    st.session_state["edit_options_complete"] = True
                
        no_changes = False
        if col_3.button("Reset", disabled=no_changes, width="stretch"):
            _reset_changes()
        edited_str = str()

    not_complete = not st.session_state["edit_options_complete"]
    if col_4.button("Save", disabled=not_complete, width="stretch"):
        progress_edits = [option_ref["edit_source"], option_ref["change_limits"]]
        if st.session_state["options_to_edit"] in progress_edits:
            arciv.writer(
                st.session_state["changed_progress"], object_type=progress_ref, 
                other_file=DATAPATH["progress"], join_path="data")
        arciv.catch_data(
            st.session_state["changed_options"], 
            SETTINGS["Options"], "options")
        if arciv.backup(
                [7, 5, 3, 1], "options", other_file=SETTINGS["Options"]): 
            arciv.writer(
                st.session_state["changed_options"], 
                other_file=SETTINGS["Options"], join_path="settings")
        st.session_state["processed_edits"] = True
        st.rerun()

    for x in st.session_state["edited_options"]:
        edited_str += f"{x} "
    if len(edited_str) > 0: 
        st.markdown(f"Changes made in: {edited_str}")
    else:
        st.markdown("No changes")

    with st.container(height=150):
        st.json(st.session_state["changed_options"])
    with st.container(height=150):
        st.json(st.session_state["changed_progress"])


def _initiate_option_edit(attempts, options, full=True, prev_sel=None):
    logger.info("Running object_info_manager.Secretary._initiate_option_edit")

    if "changed_options" not in st.session_state:
        st.session_state["changed_options"] = copy.deepcopy(
            hold.load_options())
    elif not st.session_state["changed_options"]:
        st.session_state["changed_options"] = copy.deepcopy(
            hold.load_options())
    
    if "changed_options" not in st.session_state:
        st.session_state["changed_progress"] = copy.deepcopy(
            hold.load_progress_data())
    elif not st.session_state["changed_progress"]:
        st.session_state["changed_progress"] = copy.deepcopy(
            hold.load_progress_data())
        
    option_ref = {
        "edit_utility": utility_ref,
        "edit_attribute": attribute_ref,
        "edit_origin": origin_ref,
        "edit_source": source_ref,
        "change_limits": f"{attempt_ref} limits"
    }
    st.session_state["changed_progress"] = attempts

    if full:
        selection = st.selectbox(
            "Select option to edit", options=list(option_ref.values()), 
            key="options_to_edit", on_change=_reset_changes)
    else:
        selection = prev_sel
    name_edit = False
    remove_options, no_options, requirements = [None]*3
    name_options = list(option_ref.values())
    name_options.remove(option_ref["change_limits"])
    object_options = name_options.copy()
    object_options.remove(option_ref["edit_source"])
    if selection in name_options: 
        name_edit = True

        if selection in object_options:
            requirements = options[f"{main_ref}_required"][selection]
            selection_options = options[main_ref][selection]
            remove_options = [x for x in selection_options if x not in requirements]
        elif selection == option_ref["edit_source"]:
            requirements = options["source_required"]
            remove_options = [x for x in options["source"] if x not in requirements]
        no_options = len(remove_options) < 1

    st.session_state["remove_options"] = remove_options

    if full:
        return name_edit, selection, no_options, option_ref
    else:
        remove_options


def _reset_changes():
    st.session_state["changed_options"] = hold.load_options()
    st.session_state["changed_progress"] = hold.load_progress_data()
    st.session_state["edit_options_complete"] = False


def _validity_check(name=False, number=False):
    msg, msg_len, msg_sym, msg_ini, msg_val = [str()]*5
    
    if name:
        max_length = 40
        min_length = 0
        msg_len = "Too long. "
        length_check = len(name) > min_length and len(name) < max_length

        if length_check:
            symbol_check = True
            if not name.isalnum():
                for symbol in name:
                    if not symbol.isalnum() and symbol not in ("-", " "):
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
                msg_val = "Too-high. "
    else:
        num_check = True

    msg += f"{msg_len}{msg_sym}{msg_ini}{msg_val}"
    if all([length_check, symbol_check, num_check]):
        return False, None
    else:
        return True, msg