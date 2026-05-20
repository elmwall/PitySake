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
common_ref = TERMS["common_source"]
event_ref = TERMS["event"]
gift_ref = TERMS["gift"]
main_ref = TERMS["main"]
origin_ref = TERMS["origin"]
secondary_ref = TERMS["secondary"]
source_ref = TERMS["source"]
state_ref = TERMS["state"]
utility_ref = TERMS["utility"]
utility_sec_ref = TERMS["secondary_utility"]


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
            st.markdown(
                "##### *Update library*",  text_alignment="left")

    # Main container
    with st.container(
            border=True, key=f"{component_key}_main", 
            width=feature_size_left, height="stretch"):

        # Build widgets
        col_object_info, col_save_and_event = _style_form()
        pill_group_height = "stretch"
        # Object detail column
        with col_object_info:
            # Action selector field - what to do 
            # - control name and date selection options
            with st.container(
                    border=True, key=sub_keys[0], width="stretch", 
                    height=pill_group_height, vertical_alignment="center"):
                col_label, col_options = _style_selector()
                # Option label
                col_label.markdown("TO DO")
                # Action options
                reg_selection = col_options.pills(
                    "Registration setting", options=list(reg_options.keys()), 
                    format_func=lambda x:reg_options[x]["label"], 
                    key="regset", 
                    width="stretch", label_visibility="collapsed")
                if reg_selection:
                    reg_setting = reg_options[reg_selection]
            
            # Name and type
            col_name, col_type = _style_target()
            with col_name:
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
            # Option type 
            # - controls object label options
            with col_type:
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
            
            # Object details 
            # - options controlled by type 
            # - "secondary" object has disabled extras "attribute" and "origin"
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
        
        # Column: save button | event details | edit options
        with col_save_and_event:
            # 1. Checks data 
            #   - correct setup for the edit setting
            #   - translate to correct formate
            #   - adjust submit-button text for user tip
            object_in_library, event_length, old_event_data = [None]*3
            event_length, old_event_data = [None]*2
            current_database = st.session_state["current_database"]
            if st.session_state["reg_name"] is not None: 
                reg_name = st.session_state["reg_name"].title()
                object_in_library = reg_name in current_database
                if reg_name.title() in current_database:
                    event_length = len(current_database[reg_name][event_ref])
                    old_event_data = current_database[reg_name][event_ref]

            data_is_valid, save_button_msg, is_secondary = _data_validation(
                preset_keys, st.session_state["regset"], 
                object_in_library, event_length)
            # 2. Compile the object data on press IF all data present, else disable button
            name, new_data = _compile_data(
                data_is_valid, save_button_msg, is_secondary, highlight_html, old_event_data)
            object_type = st.session_state["reg_object_type"]
            if new_data and object_type: 
                # 3. Save the data. For editing data, ask for renaming in dialog box
                if st.session_state["regset"] == "edit_entry":
                    secretary.rename(
                        name, object_type, new_data, 
                        reg_setting, highlight_html)
                else:
                    # 4. Update (with confirmation required for deletion)
                    if st.session_state["regset"] in ["del_entry", "del_event"]:
                        secretary.confirm_deletion(
                            name, object_type, new_data, 
                            reg_setting, reg_selection, 
                            removal_date=st.session_state["translated_values"]["reg_date"])
                    else:
                        secretary.update_object(
                            name, object_type, new_data, 
                            reg_setting, new_name=None)
            st.space("xxsmall")

            # Event data - how and when object was collected
            # Date selector: 
            # - render proper date selector (calender or selectbox)
            # - controlled by reg action type
            if st.session_state["regset"] == "del_event" and st.session_state["reg_name"]: 
                options_dates = st.session_state["current_database"][
                    st.session_state["reg_name"]][event_ref].keys()
            else:
                options_dates = None
            _date_viewer(data_options, options_dates)
            # Source selector
            source_help_text = f"""For anything not from a {event_ref.lower()} 
                and without {attempt_ref.lower()}, select 'Reward'"""
            st.selectbox(
                f"{source_ref}", options=preset_options["options_source"], 
                index=0, key="reg_source", help=source_help_text,
                on_change=_update_source_progress, 
                args=(st.session_state["reg_object_type"],), 
                label_visibility="visible")
            # State selector
            # - controlled by source selection
            st.selectbox(
                "Outcome", options=preset_options["options_states"], index=0, key="reg_state", 
                placeholder="Outcome", disabled=st.session_state["state_disabled"], 
                label_visibility="collapsed")

            # Attempt/progress input 
            # - limit from progress data limits
            # - suggested value from progress tracker
            # - controlled by source selection
            st.number_input(
                f"{attempt_ref}", min_value=0, max_value=st.session_state["selection_limit"], key="reg_attempt", 
                disabled=st.session_state["limit_disabled"])

            # Project configuration - change options
            with st.container(height="stretch", vertical_alignment="bottom"):
                st.button(
                    "Edit options", key="edit_options", 
                    on_click=config.edit_options, 
                    args=(attempts, data_options),
                    type="secondary", width="stretch")
            

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


def _date_viewer(data_options: dict, 
                 options_dates: list | None):
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
            key="reg_date", disabled=not_ready, label_visibility="visible")    


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


def _data_validation(preset_keys: list, reg_selection: str, 
                     object_in_library: bool, event_length: int | None) -> tuple: 
    """
    Validation control controlling save-button acitvation
    - Adjusts selections to valid formats (date formats and None values)
    - Sets save button tip text

    Args:
        preset_keys (list):
            session state keys for all required values
        reg_selection (str):
            action to be performed

    Returns:
        Tuple (bool, str, bool):
            data_is_valid (bool)  
            save_button_msg (str)  
            is_secondary (bool)
    """
    # Adjust validity check and "save"-button message for clarity
    # Collect state translated_values
    for x in preset_keys:
        st.session_state["translated_values"][x] = st.session_state[x]
    if type(st.session_state["reg_date"]) is str:
        st.session_state["translated_values"]["reg_date"] = st.session_state["reg_date"]
    elif not st.session_state["translated_values"]["reg_date"]:
        pass
    else:
        adjusted_date = st.session_state["reg_date"].strftime("%y%m%d")
        st.session_state["translated_values"]["reg_date"] = adjusted_date
    if st.session_state["reg_source"] in [common_ref, gift_ref]: 
        st.session_state["translated_values"]["reg_state"] = None
    if st.session_state["reg_source"] == gift_ref: 
        st.session_state["translated_values"]["reg_attempt"] = None

    # "Already in library" 
    # - to avoid losing data, prevent adding same object more than once
    if reg_selection == "add_new" and object_in_library:
        data_is_valid, save_button_msg = False, "Already exists"
    # "Delete object"
    elif reg_selection == "del_entry":
        data_is_valid, save_button_msg = True, f"Delete object"
    # "Delete object event" 
    # - removing collection info of object at date
    elif reg_selection == "del_event":
        save_button_msg = f"Delete {event_ref.lower()}"
        # Do not attempt if event data is empty 
        # - should only occur after previous deletion
        data_is_valid = True if event_length else False
    # "Save" - use case for adding new object or editing without deletion
    else:
        data_is_valid, save_button_msg = True, "Save"
    # Main type of object or utilitarian object
    is_secondary = st.session_state[
        "translated_values"]["reg_object_type"] == secondary_ref

    return data_is_valid, save_button_msg, is_secondary


def _compile_data(data_is_valid: bool, save_button_msg: str, 
                  is_secondary: bool, highlight_html: str,
                  old_event_data: dict) -> tuple:
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
        data_is_valid (bool):
            prior checks of data validity
        save_button_msg (str):
            user tip for complete/missing info in form
        old_event_data (dict):
            new event is added to this info

    Returns:
        Tuple (str | None, dict | None):
            name (str | None): object key in database
            new_data (dict | None): new object info
    """
    name_done, utility_done, attribute_done, origin_done, state_done = [False]*5
    if data_is_valid:
        # Secondary object has attribute and origin labels disabled
        disable_extras = st.session_state[
            "translated_values"]["reg_object_type"] == secondary_ref
        
        # Completion checks
        if st.session_state["translated_values"]["reg_name"]: 
            name_done = True
        if st.session_state["translated_values"]["reg_utility"]: 
            utility_done = True
        if not disable_extras:
            if st.session_state["translated_values"]["reg_attribute"]: 
                attribute_done = True
            if st.session_state["translated_values"]["reg_origin"]: 
                origin_done = True
        else:
            attribute_done, origin_done = True, True
        if not st.session_state["translated_values"]["reg_state"]:
            reg_source = st.session_state["translated_values"]["reg_source"]
            if reg_source == common_ref or reg_source == gift_ref: 
                state_done = True
        else:
            state_done = True

    # When finished, build dictionary entry for object
    if all([name_done, utility_done, attribute_done, 
            origin_done, state_done]):
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





