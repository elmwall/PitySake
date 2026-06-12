"""
Object registration module

Renders tool and manages
- directs info from and to object_info_manager to manage databases and options
- interactive setup of options and values in widgets
- validates input before enabling save and compiles for saving
- gateway to edit project options dialog
"""

import copy
import datetime
import logging

import streamlit as st

from .object_info_manager import Secretary
import app.data_access as hold
import app.project_configuration as config


logger = logging.getLogger(__name__)
DATAPATH = st.session_state["DATAPATH"]
DIRECTORIES = st.session_state["DIRECTORIES"]
TERMS = st.session_state["TERMS"]

attempt_ref = TERMS["attempt"]
attribute_ref = TERMS["attribute"]
# common_ref = TERMS["common_source"]
event_ref = TERMS["event"]
# gift_ref = TERMS["gift"]
main_ref = TERMS["main"]
origin_ref = TERMS["origin"]
secondary_ref = TERMS["secondary"]
source_ref = TERMS["source"]
state_ref = TERMS["state"]
utility_ref = TERMS["utility"]
utility_sec_ref = TERMS["utility"]


def register_object(component_key: str, sub_keys: list, 
                    feature_size_left: int | str, highlight_html: str):
    """
    Render object registration feature

    All changes in main and secondary library.  
    - editing action: add/delete object, add/delete event, edit details
    - name: enter new / select existing
    - object event: date, source, state, progress/attempts
    - edit options: dialog for editing (limited) options above
        
    Args:
        component_key (str):
            session state key for feature
        sub_keys (list):
            session state keys for subfeatures
    
    Behavior:
    - available options adapts to type of object and action selected
    - blocks submitting invalid data
    - for event source, collects progress from corresponding tracker
    """
    logger.info("Running")
    
    _feature_style(component_key)
    attempts = copy.deepcopy(hold.load_progress_data())
    data_options = hold.load_options()
    secretary = Secretary(data_options, attempts, component_key, sub_keys)
    # Define all initial settings, options and limits
    preset_options, reg_options, preset_keys = secretary.settings()
    # Main object (standard) has all labels, secondary has one
    disable_extras = False

    # Header
    if st.session_state["header_switch"]:
        with st.container(
                key=f"{component_key}_head", 
                width=feature_size_left, height="content"):
            st.markdown("##### *Update library*",  text_alignment="left")

    # Main container
    with st.container(
            border=True, key=f"{component_key}_main", 
            width=feature_size_left, height="content"):

        # Build widgets
        col_object_info, col_save_and_event = _style_form()
        pill_group_height = "stretch"
        # Object detail column
        with col_object_info:
            # Action selector field - what to do 
            # - control name and date selection options
            reg_selection, reg_setting = _action_selector(
                sub_keys, reg_options, pill_group_height)
            
            # Name
            col_name, col_type = _style_target()
            with col_name:
                _naming_object(secretary, reg_selection)
            # Option type 
            # - controls object label options
            with col_type:
                disable_extras = _type_selection(secretary, preset_options)
            
            # Object details 
            # - options controlled by type 
            # - "secondary" object has disabled extras "attribute" and "origin"
            _select_labels(sub_keys, preset_options, disable_extras, pill_group_height)
        
        # Column: save button | event details | edit options
        with col_save_and_event:
            _save_data(secretary, preset_keys, reg_setting, reg_selection, highlight_html)
            st.space("xxsmall")

            # Event data - how and when object was collected
            # Date selector: 
            # - render proper date selector (calender or selectbox)
            # - controlled by reg action type
            checkbox_disabled = st.session_state["regset"] != "add_new"
            st.checkbox(
                "Add event", key="include_event", disabled=checkbox_disabled)
            _date_input(data_options)
            event_disabled = any([
                not st.session_state["include_event"], 
                st.session_state["regset"] not in ["add_new", "add_event"]])
            # Event details: source, state, attempts
            _event_details(preset_options, event_disabled)

            # Project configuration - change options
            with st.container(height="stretch", vertical_alignment="bottom"):
                st.button(
                    "Edit options", key="edit_options", 
                    on_click=config.edit_options, 
                    args=(attempts, data_options),
                    type="secondary", width="stretch")
            

# Style fuctions
def _feature_style(component_key: str):
    "Sets feature dimension."
    st.html("""
    <style> 
        .st-key-REF {min-width: 1000px;} 
    </style>""".replace("REF", component_key))

def _style_form() -> list:
    "Sets feature main columns."
    return st.columns([1, 0.2], vertical_alignment="top")

def _style_selector():
    "Sets label selection fields."
    return st.columns([0.1, 0.9], vertical_alignment="center")

def _style_target():
    "Sets feature name and type selection columns."
    return st.columns([5, 5], vertical_alignment="center")


# Subfeatures
def _action_selector(sub_keys: list, reg_options: dict, 
                     pill_group_height: str|int) -> tuple:
    """
    User selection for action to be performed:
    - Add completely new object
    - Add new object event
    - Delete object
    - Edit object details
    - Delete object event

    Args:
        reg_options (dict):
            registrations options available, 
            with corresponding label and settings
    
    Returns:
        Tuple (str, dict):
            identifier for selected action (str)  
            settings for selected actions (dict)
    """
    with st.container(
            border=True, key=sub_keys[0], width="stretch", 
            height=pill_group_height, vertical_alignment="center"):
        col_label, col_options = _style_selector()
        # Option label
        col_label.markdown("TO DO")
        # Action options
        # Options listed are generated via reg_options label value via lambda, 
        # while sending key to session state
        reg_selection = col_options.pills(
            "Registration setting", options=list(reg_options.keys()), 
            format_func=lambda x:reg_options[x]["label"], 
            key="regset", on_change=_update_event_choice,
            width="stretch", label_visibility="collapsed")
        if reg_selection:
            reg_setting = reg_options[reg_selection]
        
    return reg_selection, reg_setting

# _action_selector ->
def _update_event_choice():
    "Syncs control value for adding event to session state."
    if st.session_state["regset"] not in ["add_new", "add_event"]:
        st.session_state["include_event"] = False
    else:
        st.session_state["include_event"] = True


def _naming_object(secretary: Secretary, reg_selection: str):
    """
    Controls name input method and options
    
    Settings:
    - add_new, for completely new object, sets text input for new name
    - all others: changes to existing objects, 
        sets selectbox with objects from database

    Args:
        reg_selection (str):
            user selection for action, controlling input method
    """
    # For new object --> enter name
    try:
        object_viewname = st.session_state["reg_object_type"]
    except:
        object_viewname = "Object"
    if reg_selection == "add_new":
        st.text_input(
            "Name", key="reg_name", 
            placeholder=f"Enter new {object_viewname.lower()}", 
            label_visibility="collapsed")
    elif not reg_selection:
        st.text_input(
            "Name", key="reg_name", 
            placeholder="No action selected", disabled=True,
            label_visibility="collapsed")
    # For old object --> select name
    else:
        object_options = st.session_state.get("current_database", dict()).keys()
        
        if not st.session_state["current_database"]:
            disable_selection = True
            message = f"Select {object_viewname.lower()}"
        elif len(st.session_state["current_database"]) == 0:
            disable_selection = True
            message = "No objects in library"
        else:
            disable_selection = False
            message = f"Select {object_viewname.lower()}"
        st.selectbox(
            f"{object_viewname}s", 
            options=object_options,
            placeholder=message, disabled=disable_selection, key="reg_name", 
            on_change=secretary.collect_object_info, 
            args=(reg_selection,), label_visibility="collapsed")


def _type_selection(secretary: Secretary, preset_options: dict) -> bool:
    """
    Select main or secondary object type 
    and collect database deepcopy to session state.

    Returns:
        disable_extras (bool):
            control for enabling only "utility" label for secondary objects
    """
    if st.pills(
        "Object type", 
        options=preset_options["options_type"], 
        key="reg_object_type", 
        on_change=secretary.collect_database,
        label_visibility="collapsed"
    ):
        if st.session_state["reg_object_type"] == main_ref:
            st.session_state["current_database"] = copy.deepcopy(
                hold.load_main_database())
            disable_extras = False
        else:
            st.session_state["current_database"] = copy.deepcopy(
                hold.load_secondary_database())
            disable_extras = True

    return disable_extras


def _select_labels(sub_keys: list, preset_options: dict, 
                   disable_extras: bool, pill_group_height: str|int):
    """
    Pill selector fields for labels.

    Args:
        disable_extras (bool):
            disable "origin" and "attribute" labels for secondary objects, 
            while "utility" is active for both
    """
    # Utility selection
    with st.container(
            border=True, key=sub_keys[1], width="stretch", 
            height=pill_group_height, vertical_alignment="center"):
        col_label, col_options = _style_selector()
        col_label.markdown(TERMS["utility"])
        col_options.pills(
            "reg_utility", options=preset_options["options_utility"], 
            key="reg_utility", label_visibility="collapsed", width="stretch")  

    # Attribute selection
    with st.container(
            border=True, key=sub_keys[2], width="stretch", 
            height=pill_group_height, vertical_alignment="center"):

        col_label, col_options = _style_selector()
        col_label.markdown(attribute_ref)
        col_options.pills(
            "reg_attribute", options=preset_options["options_attribute"], 
            key="reg_attribute", disabled=disable_extras, 
            label_visibility="collapsed", width="stretch")

    # Origin selection
    with st.container(
            border=True, key=sub_keys[3], width="stretch", 
            height=pill_group_height, vertical_alignment="center"):
        col_label, col_options = _style_selector()
        col_label.markdown(origin_ref)
        col_options.pills(
            "reg_origin", options=preset_options["options_origin"], 
            key="reg_origin", disabled=disable_extras, 
            label_visibility="collapsed", width="stretch")


def _save_data(secretary: Secretary, preset_keys: list, 
               reg_setting: str, reg_selection: str, highlight_html: str):
    """
    Central function for validating information input and redirecting data management to Secretary.
    
    Behavior:
    1. Checks data  
    - correct setup for the edit setting
    - translate to correct format
    - adjust submit-button text for user tip
    - check valid format and combinations
    - check tasks completed
    2. Compile and save
    - Compile data structure if all data is done and render enabled button
    - Incomplete data -> disable button
    - Press enabled button -> return compiled data
    3. Save data
    - If editing or deleting object: ask for user confirmation
    - Send finished data to Secretary to write to file

    Args:
        secretary (Secretary):
            object_info_manager class
        preset_keys (list):
            session state keys for all required values
        reg_setting (str):
            settings for saving
        reg_selection (str):
            action to be performed
    """
    # 1. Check data 
    object_in_library, event_length, old_event_data = [None]*3
    event_length, old_event_data = [None]*2
    current_database = st.session_state["current_database"]
    if st.session_state["reg_name"] is not None: 
        reg_name = st.session_state["reg_name"].title()
        object_in_library = reg_name in current_database
        if reg_name.title() in current_database:
            event_length = len(current_database[reg_name][event_ref])
            old_event_data = current_database[reg_name][event_ref]

    data_is_valid, save_button_msg, is_secondary = secretary.data_validation(
        preset_keys, st.session_state["regset"], 
        object_in_library, event_length)
    task_states = secretary.checklist(data_is_valid)
    # 2. Compile object data on press of all data present, else disable button
    name, new_data = _compile_data(
        task_states, save_button_msg, is_secondary, highlight_html, old_event_data)
    object_type = st.session_state["reg_object_type"]
    # 3. Saving process. For editing data, ask for renaming in dialog box
    if new_data and object_type: 
        if st.session_state["regset"] == "edit_entry":
            secretary.rename(
                name, object_type, new_data, reg_setting, highlight_html)
        else:
            # Update (with confirmation required for deletion)
            if st.session_state["regset"] in ["del_entry", "del_event"]:
                secretary.confirm_deletion(
                    name, object_type, new_data, reg_setting, reg_selection, 
                    removal_date=st.session_state["translated_values"]["reg_date"])
            else:
                secretary.update_object(
                    name, object_type, new_data, reg_setting, new_name=None)

# _save_data ->
def _compile_data(task_states:list, save_button_msg: str, is_secondary: bool, 
                  highlight_html: str, old_event_data: dict) -> tuple:
    """
    Save button render and function
    - active when validation and completion check is all true
    - compiles object and event data to proper database format
    - sets event date with index and sorts events by date 
    - main object entry compiled as:  
        ```
        "Object Name" = {  
            "Origin term": "Origin label",  
            "Attribute term": "Attribute label",  
            "Utility term": "Utility label",  
            "Event term": {  
                "YYMMDD-index: {  
                    "Source term": "Source Name",  
                    "Attempt term": attempt_value,  
                    "State": "Selected state"  
                }  
            }  
        }
        ```

    Args:
        task_states (list):
            control for finalizing data and button activation, 
            dependent on data validation and checklist functions
        save_button_msg (str):
            user tip for complete/missing info in form
        old_event_data (dict):
            new event is added to this info

    Returns:
        Tuple (str | None, dict | None):
            name (str | None): object key in database
            new_data (dict | None): new object info
    """
    # When finished, build dictionary entry for object
    if all(task_states):
        name = st.session_state["translated_values"]["reg_name"].title()
        new_data = dict()
        new_data[name] = dict()
        if not is_secondary:
            new_data[name][origin_ref] = st.session_state[
                "translated_values"]["reg_origin"]
            new_data[name][attribute_ref] = st.session_state[
                "translated_values"]["reg_attribute"]
            new_data[name][utility_ref] = st.session_state[
                "translated_values"]["reg_utility"]
        else:
            new_data[name][utility_sec_ref] = st.session_state[
                "translated_values"]["reg_utility"]
            
        if st.session_state["include_event"]:
            new_event = {
                source_ref: st.session_state["translated_values"]["reg_source"],
                attempt_ref: st.session_state["translated_values"]["reg_attempt"],
                state_ref: st.session_state["translated_values"]["reg_state"]
            }
        st.html(highlight_html.replace("KEY_REF", "save"))

        # Save button
        data_is_collected = st.button(
            f"{save_button_msg}", 
            key="save", type="primary", width="stretch")
        
        # If save is pressed, event info is adjusted
        if data_is_collected:
            event_date = st.session_state["translated_values"]["reg_date"]
            if st.session_state["regset"] == "edit_entry":
                new_data[name][event_ref] = old_event_data
            elif st.session_state["regset"] in ["add_new", "add_event", "del_event"]:
                if st.session_state["regset"] == "add_new":
                    event_data = dict()
                else:
                    event_data = old_event_data

                if st.session_state["regset"] != "del_event": 
                    if st.session_state["include_event"]:
                        now = datetime.datetime.now()
                        hhmmss = now.strftime("%H%M%S")
                        event_data[f"{event_date}-{hhmmss}"] = new_event
                else:
                    event_data.pop(event_date)

                if len(event_data) > 0: 
                    event_data = dict(sorted(event_data.items()))
                new_data[name][event_ref] = event_data
            
            return name, new_data
        else:
            return None, None
    else:
        st.button(
            f"{save_button_msg}", key="save", 
            type="secondary", disabled=True, width="stretch")
        return None, None
    

def _date_input(data_options: dict):
    """
    Renders date selector widget depending on action.

    Modes:
    - Delete event: select previous event
    - All others: select date from calender

    Args:
        data_options (dict):
            project options
        options_dates (list):
            previous events for object
    """
    if st.session_state["regset"] == "del_event" and st.session_state["reg_name"]: 
        options_dates = st.session_state["current_database"][
            st.session_state["reg_name"]][event_ref].keys()
    else:
        options_dates = None
    # Preset earliest date defined in options file, and latest as today
    date_min = data_options["value_limits"]["date"][0]
    date_min = datetime.datetime(
        int("20"+date_min[0:2]),
        int(date_min[2:4]), 
        int(date_min[4:6]))
    date_max = datetime.date.today()
    disable_dates = False
    # Option "Delete event" sets the list options as previous event dates
    if st.session_state["regset"] == "del_event" and options_dates:
        disable_dates = False if st.session_state["reg_name"] else True
        st.selectbox(
            f"Select date", options_dates, key="reg_date", 
            help=f"Displays {event_ref.lower()} [Date]-[Time].",
            disabled=disable_dates, label_visibility="visible")
    # Standard setting, write date or select by calender
    else:
        try:
            st.session_state["reg_date"].strftime("%y%m%d")
        except:
            st.session_state["reg_date"] = datetime.date.today()
        not_ready = not st.session_state["reg_name"]
        st.date_input(
            "First received", min_value=date_min, max_value=date_max, 
            key="reg_date", disabled=not_ready, label_visibility="collapsed")    


def _event_details(preset_options, event_disabled):
    # Source selector 
    source_help_text = f"""For anything not from a {event_ref.lower()} 
        and without {attempt_ref.lower()}, select 'Reward'"""
    st.selectbox(
        f"{source_ref}", options=preset_options["options_source"], 
        index=0, key="reg_source", help=source_help_text,
        on_change=_update_source_progress, 
        args=(st.session_state["reg_object_type"],), 
        disabled=event_disabled, label_visibility="visible")
    
    # State selector
    # - controlled by source selection
    state_disabled = any([event_disabled, st.session_state["state_disabled"]])
    st.selectbox(
        "Outcome", options=preset_options["options_states"], index=0, key="reg_state", 
        placeholder="Outcome", disabled=state_disabled, 
        label_visibility="collapsed")
    
    # Attempt/progress input 
    # - limit from progress data limits
    # - suggested value from progress tracker
    # - controlled by source selection
    limit_disabled = any([event_disabled, st.session_state["limit_disabled"]])
    num_title = f"{TERMS["unit"]} {attempt_ref}" if TERMS["unit"] else attempt_ref
    st.number_input(
        num_title, min_value=0, max_value=st.session_state["selection_limit"], 
        key="reg_attempt", disabled=limit_disabled)

# _event_details -> 
def _update_source_progress(data_type: str):
    """
    Adjust progress/attempt field

    Actions:
    - For gift: set None
    - All others: collect progress value for source from progress data

    Args:
        attempts (dict):
            data from progress database
        data_type (str):
            identifier for object data type
    """
    reg_source = st.session_state["reg_source"]
    data_type = st.session_state["reg_object_type"]
    if reg_source and data_type: 
        if hold.load_options()["source_limit"][reg_source]:
            st.session_state["limit_disabled"] = False
            st.session_state["selection_limit"] = hold.load_options()["source_limit"][reg_source]
            st.session_state["reg_attempt"] = hold.load_progress_data()[reg_source][TERMS["attempt"]]
        else:
            st.session_state["limit_disabled"] = True
            st.session_state["selection_limit"] = 0
            st.session_state["reg_attempt"] = 0
        st.session_state["state_disabled"] = hold.load_options()["states"][reg_source] is False
    else:
        st.session_state["selection_limit"] = 0
        st.session_state["limit_disabled"] = True
        st.session_state["reg_attempt"] = 0
        st.session_state["state_disabled"] = True


