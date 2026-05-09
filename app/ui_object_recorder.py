import streamlit as st
import datetime

from .file_manager import Archivist
from .object_info_manager import Secretary
import app.data_access as hold

from settings.config import TERMS, DIRECTORIES, DATAPATH


attempt_ref = TERMS["attempt"]
attribute_ref = TERMS["attribute"]
common_ref = TERMS["common_source"]
event_ref = TERMS["event"]
gift_ref = TERMS["gift"]
origin_ref = TERMS["origin"]
source_ref = TERMS["source"]
state_ref = TERMS["state"]
utility_ref = TERMS["utility"]


def register_object(component_key, sub_keys, feature_size_left, highlight_html):
    _feature_style(component_key)
    attempts = hold.load_progress_data()
    data_options = hold.load_options()
    arciv = Archivist(DIRECTORIES, DATAPATH, "nofile")
    secretary = Secretary(arciv, DATAPATH, TERMS, data_options, attempts, component_key, sub_keys)

    # Header
    if st.session_state["header_switch"]:
        with st.container(
            key=f"{component_key}_head", 
            width=feature_size_left, 
            height="content"
        ):
            st.markdown(
                "##### *Update library*",  
                text_alignment="left"
            )
    # Main container
    with st.container(border=True, key=f"{component_key}_main", width=feature_size_left, height="stretch"):
        # Define all initial settings, options and limits
        object_database, selectable_options, registration_options, preset_keys = secretary.settings(st.session_state["reg_object_type"])
        disable_extras = False
        # Build widgets
        col_object_info, col_save_and_event = _style_form()
        pill_group_height = "stretch"
        with col_object_info:
            # Action selector field - what to do with the data
            with st.container(border=True, key=sub_keys[0], width="stretch", height=pill_group_height, vertical_alignment="center"):
                col_label, col_options = _style_selector()
                col_label.markdown("TO DO")
                reg_selection = col_options.pills(
                    "Registration setting", 
                    options=list(registration_options.keys()), 
                    default=list(registration_options.keys())[0], 
                    format_func=lambda x:registration_options[x]["label"], 
                    key="regset", 
                    width="stretch", 
                    label_visibility="collapsed"
                )
                reg_setting = registration_options[reg_selection]
            # Target selector field - name and type of object
            col_name, col_type = _style_target()
            with col_name:
                # For new object --> enter name
                try:
                    label = st.session_state["reg_object_type"]
                except:
                    label = "Object"
                if reg_selection == "add_new":
                    st.text_input(
                        "Name", 
                        key="reg_name", 
                        placeholder=f"Enter new {label.lower()}", 
                        label_visibility="collapsed"
                    )
                # For old object --> select name
                else:
                    st.selectbox(
                        f"{label}s", 
                        options=selectable_options["options_object"],
                        placeholder=f"Select {label.lower()}", 
                        key="reg_name", 
                        on_change=secretary.collect_object_info, 
                        args=(object_database, reg_selection), 
                        label_visibility="collapsed"
                    )
            with col_type:
                type_selected = st.pills(
                    "Object type", options=selectable_options["options_type"], key="reg_object_type", label_visibility="collapsed"
                )
                disable_extras = type_selected ==utility_ref
            
            # Object details - "utility" utilitarian object disables extras i.e. "attribute" and "origin"
            with st.container(border=True, key=sub_keys[1], width="stretch", height=pill_group_height, vertical_alignment="center"):
                col_label, col_options = _style_selector()
                col_label.markdown(TERMS["utility"])
                col_options.pills(
                    "reg_utility", 
                    options=selectable_options["options_utility"], 
                    key="reg_utility", 
                    label_visibility="collapsed", 
                    width="stretch"
                )  
            with st.container(border=True, key=sub_keys[2], width="stretch", height=pill_group_height, vertical_alignment="center"):
                col_label, col_options = _style_selector()
                col_label.markdown(attribute_ref)
                col_options.pills(
                    "reg_attribute", 
                    options=selectable_options["options_attribute"], 
                    key="reg_attribute", 
                    disabled=disable_extras, 
                    label_visibility="collapsed", 
                    width="stretch"
                )
            with st.container(border=True, key=sub_keys[3], width="stretch", height=pill_group_height, vertical_alignment="center"):
                col_label, col_options = _style_selector()
                col_label.markdown(origin_ref)
                col_options.pills(
                    "reg_origin", 
                    options=selectable_options["options_origin"], 
                    key="reg_origin", 
                    disabled=disable_extras, 
                    label_visibility="collapsed", 
                    width="stretch"
                )
        
        with col_save_and_event:
            # Save button - validate, compile and save
            # 1. Collect state values
            values = dict()
            for x in preset_keys:
                values[x] = st.session_state[x]
            if type(st.session_state["reg_date"]) is str:
                values["reg_date"] = st.session_state["reg_date"]
            elif not values["reg_date"]:
                pass
            else:
                values["reg_date"] = st.session_state["reg_date"].strftime("%y%m%d")
            if st.session_state["reg_source"] in [common_ref, gift_ref]: values["reg_state"] = None
            if st.session_state["reg_source"] == gift_ref: values["reg_attempt"] = None
            object_database = secretary.collect_database(st.session_state["reg_object_type"])

            # 2. Checks for proper data setup
            object_testvalue, event_testvalue, old_event_data = [None]*3
            if st.session_state["reg_name"]: 
                object_testvalue = st.session_state["reg_name"].title() in object_database.keys()
                if st.session_state["reg_name"] in object_database.keys() and event_ref in object_database[st.session_state["reg_name"]].keys():
                    event_testvalue = len(object_database[st.session_state["reg_name"]][event_ref])
                    old_event_data = object_database[st.session_state["reg_name"]][event_ref]
            data_is_valid, save_button_msg, is_utility = _data_validation(
                values, 
                st.session_state["regset"], 
                object_testvalue, 
                event_testvalue
            )

            # 3. Compile the data on press IF all data present, else disable button
            data_is_collected, name, new_data, new_event, event_date = _compile_data(
                values, 
                data_is_valid, 
                save_button_msg, 
                is_utility, 
                highlight_html
            )
            if data_is_collected and st.session_state["reg_object_type"]: 
                object_type = st.session_state["reg_object_type"]
                new_data = _adjust_event_data(
                    name, 
                    new_data,
                    old_event_data, 
                    new_event, 
                    event_date
                )

                # 4. Save the data. For editing data, ask for renaming in dialog box
                if st.session_state["regset"] == "edit_entry":
                    secretary._rename(
                        name, 
                        object_type, 
                        new_data, 
                        reg_setting, 
                        highlight_html
                    )
                else:
                    # Confirmation required for deletion
                    if st.session_state["regset"] in ["del_entry", "del_event"]:
                        _user_confirm(
                            secretary, 
                            name, 
                            object_type, 
                            new_data, 
                            reg_setting, 
                            reg_selection, 
                            removal_date=values["reg_date"]
                        )
                    else:
                        secretary.update_object(
                            name, 
                            object_type, 
                            new_data, 
                            reg_setting, 
                            new_name=None
                        )

            # Info about how and when object was collected
            # Date collector/viewer
            st.space("xxsmall")
            options_dates = list()
            if st.session_state["regset"] == "del_event" and st.session_state["reg_name"]: 
                options_dates = object_database[st.session_state["reg_name"]][event_ref].keys()
            _date_viewer(data_options, options_dates)

            # Source selector
            st.selectbox(
                f"{source_ref}", 
                options=selectable_options["options_source"], 
                index=0, 
                key="reg_source", 
                help=f"For anything not from a {event_ref.lower()} and without {attempt_ref.lower()}, select 'Reward'",
                on_change=_update_source_state, 
                args=(attempts, st.session_state["reg_object_type"]), 
                label_visibility="visible"
            )
            # State selector
            source = _translate_source(
                st.session_state["reg_object_type"], 
                st.session_state["reg_source"]
            )
            options_state = data_options["state_alternatives"]
            single_state = False
            if st.session_state["reg_source"] in [common_ref, gift_ref]: 
                single_state = True
            st.selectbox(
                "Success", 
                options_state, 
                index=0, 
                key="reg_state", 
                placeholder="Win or loose?", 
                disabled=single_state, 
                label_visibility="collapsed"
            )

            # attempt input - attempt and limit autogenerated from progress data
            if not source == gift_ref:  
                limit = attempts[source]["limit"]
                st.number_input(f"{attempt_ref}", min_value=0, max_value=limit, key="reg_attempt")
            else:
                limit = 0
                st.number_input(f"{attempt_ref}", min_value=0, max_value=limit, key="reg_attempt", disabled=True)

            # Change options
            with st.container(height="stretch", vertical_alignment="bottom"):
                st.button("Edit options", key="edit_options", on_click=secretary.edit_options, type="secondary", width="stretch")
            


def _feature_style(component_key):
    st.html("<style> .st-key-REF {min-width: 1000px;} </style>".replace("REF", component_key))
def _style_form():
    return st.columns([1, 0.2], vertical_alignment="top")
def _style_selector():
    return st.columns([0.1, 0.9], vertical_alignment="center")
def _style_target():
    return st.columns([5, 5], vertical_alignment="center")


def _date_viewer(data_options, options_dates):
    # Preset earliest date defined in options file, and latest as today
    date_min = data_options["value_limits"]["date"][0]
    date_min = datetime.datetime(
        int("20"+date_min[0:2]),
        int(date_min[2:4]), 
        int(date_min[4:6]))
    date_max = datetime.date.today()
    disable_dates = False
    # Option "Delete event" sets the list options as previous event dates
    if st.session_state["regset"] == "del_event":
        disable_dates = False if st.session_state["reg_name"] else True
        st.selectbox(
            f"Select date", 
            options_dates, 
            key="reg_date", 
            help=f"Displays {event_ref.lower()} [Date]-[Time].",
            disabled=disable_dates, 
            label_visibility="visible"
        )
    # Standard setting, write date or select by calender
    else:
        try:
            st.session_state["reg_date"].strftime("%y%m%d")
        except:
            st.session_state["reg_date"] = datetime.date.today()
        not_ready = not st.session_state["reg_name"]
        st.date_input(
            "First received", 
            min_value=date_min, 
            max_value=date_max, 
            key="reg_date", 
            disabled=not_ready,
            label_visibility="visible"
        )    


def _update_source_state(attempts, data_type):
    source = _translate_source(data_type, st.session_state["reg_source"])
    if not source == gift_ref: 
        st.session_state["reg_attempt"] = attempts[source][attempt_ref]
    else:
        st.session_state["reg_attempt"] = None


# Convert source name to collect correct attempt data
def _translate_source(data_type, source):
    if source == TERMS["temp"]:
        source = f"{TERMS["main"]} {source}" if data_type == TERMS["main"] else f"{TERMS["utility"]} {source}"
    elif source == common_ref:
        st.session_state["reg_state"] = None
    elif not data_type:
        source = TERMS["temp"]
    return source


def _data_validation(values, reg_selection, object_testvalue, event_testvalue):
    # Checks for proper data setup
    # Adjust validity check and "save"-button message for clarity
    # "Already in library" - to avoid losing data objects shall not be added more than once
    if reg_selection == "add_new" and object_testvalue:
        data_is_valid, save_button_msg = False, "Already exists"
    # "Delete object"
    elif reg_selection == "del_entry":
        data_is_valid, save_button_msg = True, f"Delete object"
    # "Delete object event" - removing collection info of object at date
    elif reg_selection == "del_event":
        save_button_msg = f"Delete {event_ref.lower()}"
        # Do not attempt if event data is empty - should only occur after previous deletion
        data_is_valid = True if event_testvalue else False
    # "Save" - use case for adding new object or editing without deletion
    else:
        data_is_valid, save_button_msg = True, "Save"
    # Main type of object or utilitarian object
    is_utility = values["reg_object_type"] == utility_ref

    return data_is_valid, save_button_msg, is_utility


def _compile_data(values, data_is_valid, save_button_msg, is_utility, highlight_html):
    # Mark tasks as finished
    name_done, utility_done, attribute_done, origin_done, state_done = [False]*5
    if data_is_valid:
        disable_extras = values["reg_object_type"] == utility_ref
        if values["reg_name"]: name_done = True
        if values["reg_utility"]: utility_done = True
        if not disable_extras:
            if values["reg_attribute"]: attribute_done = True
            if values["reg_origin"]: origin_done = True
        else:
            attribute_done, origin_done = True, True
        if not values["reg_state"]:
            if values["reg_source"] == common_ref or values["reg_source"] == gift_ref: state_done = True
        else:
            state_done = True
    # When finished, build data dictionary
    if all([name_done, utility_done, attribute_done, origin_done, state_done]):
        name = values["reg_name"].title()
        new_data = dict()
        new_data[name] = dict()
        if not is_utility:
            new_data[name][origin_ref] = values["reg_origin"]
            new_data[name][attribute_ref] = values["reg_attribute"]
            new_data[name][TERMS["utility"]] = values["reg_utility"]
        else:
            new_data[name]["Type"] = values["reg_utility"]
        attempt_data = {
            source_ref: values["reg_source"],
            attempt_ref: values["reg_attempt"],
            state_ref: values["reg_state"]
        }
        st.html(highlight_html.replace("KEY_REF", "save"))
        data_is_collected = st.button(f"{save_button_msg}", key="save", type="primary", width="stretch")
        return data_is_collected, name, new_data, attempt_data, values["reg_date"]
    else:
        st.button(f"{save_button_msg}", key="save", type="secondary", disabled=True, width="stretch")
        return False, None, None, None, None


def _adjust_event_data(name, new_data, old_event_data, new_event, event_date):    
    if st.session_state["regset"] == "edit_entry":
        new_data[name][event_ref] = old_event_data
    elif st.session_state["regset"] in ["add_new", "add_event", "del_event"]:
        event_data = dict() if st.session_state["regset"] == "add_new" else old_event_data
        if st.session_state["regset"] != "del_event": 
            now = datetime.datetime.now()
            hhmmss = now.strftime("%H%M%S")
            event_data[f"{event_date}-{hhmmss}"] = new_event
        else:
            event_data.pop(event_date)
        if len(event_data) > 0: 
            event_data = dict(sorted(event_data.items()))
        new_data[name][event_ref] = event_data
    
    return new_data


@st.dialog(f"Removing object data")
def _user_confirm(secretary, name, object_type, new_data, edit_settings, removal_object, removal_date):
    st.session_state["dialog_active"] = True
    if removal_object == "Delete entry":
        st.markdown(f"Remove {name} from library?")
    elif removal_object == f"Delete {event_ref.lower()}":
        st.markdown(f"Remove {event_ref.lower()} of {name} at 20{removal_date[:2]}-{removal_date[2:4]}-{removal_date[4:6]}?")
    st.space("xsmall")
    col_left, col_right = st.columns(2)
    if col_left.button("Confirm", type="secondary", width="stretch"):
        st.session_state["reg_object_type"] = None
        secretary.update_object(name, object_type, new_data, edit_settings, None)
    if col_right.button("Cancel", type="secondary", width="stretch"):
        st.rerun()


