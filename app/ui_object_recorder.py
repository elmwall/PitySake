import streamlit as st
import datetime

from .file_manager import Archivist
from .object_info_manager import Secretary

from settings.config import TERMS, DIRECTORIES, DATAPATH

    

def register_object(data_options, attempts, component_key, sub_keys, feature_size_left, highlight_textstyle, highlight_html):
    _feature_style(component_key)
    arciv = Archivist(DIRECTORIES, DATAPATH, "nofile")
    secretary = Secretary(arciv, DATAPATH, TERMS, data_options, attempts, component_key, sub_keys)

    # Header
    with st.container(key=f"{component_key}_head", width=feature_size_left, height="content"):
        st.markdown("##### *Update library*",  text_alignment="left")
    # Main container
    with st.container(border=True, key=f"{component_key}_main", width=feature_size_left, height="stretch"):
        # Collect presets and initiate session states
        presets = secretary.initiate()
        for x, y in presets.items():
            if x not in st.session_state:
                st.session_state[x] = y
            elif not st.session_state[x]: 
                st.session_state[x] = y

        # Define all initial features settings, options and limits
        object_database, options_utility, options_object, options_attribute, options_origin, options_type, options_source, options_reg = secretary.settings(st.session_state["type"])
        disable_extras = False

        # Build widgets
        col_object_info, col_save_and_event = _style_form()
        pill_group_height = "stretch"
        with col_object_info:
            # Action selector field - what to do with the data
            with st.container(border=True, key=sub_keys[0], width="stretch", height=pill_group_height, vertical_alignment="center"):
                col_label, col_options = _style_selector()
                col_label.markdown("TO DO")
                reg_setting = col_options.pills("Registration setting", list(options_reg.keys()), default=list(options_reg.keys())[0], key="regset", label_visibility="collapsed")
            
            # Target selector field - name and type of object
            col_name, col_type = _style_target()
            with col_name:
                # For new object --> enter name
                if reg_setting == list(options_reg.keys())[0]:
                    st.text_input(
                        "Name", 
                        key="name", 
                        placeholder=f"Enter new {st.session_state["type"].lower()}", 
                        label_visibility="collapsed"
                    )
                # For old object --> select name
                else:
                    st.selectbox(
                        f"{st.session_state["type"]}s", 
                        options_object, index=None, 
                        placeholder=f"Select {st.session_state["type"].lower()}", 
                        key="name", 
                        on_change=secretary.collect_object_info, 
                        args=(object_database, reg_setting, options_reg), 
                        label_visibility="collapsed"
                    )
            with col_type:
                type_selected = st.pills(
                    "Object type", options_type, key="type", label_visibility="collapsed"
                )
                disable_extras = type_selected == TERMS["utility"]
            
            # Object details - "utility" utilitarian object disables extras i.e. "attribute" and "origin"
            with st.container(border=True, key=sub_keys[1], width="stretch", height=pill_group_height, vertical_alignment="center"):
                col_label, col_options = _style_selector()
                col_label.markdown(TERMS["utility"])
                col_options.pills(
                    "utility", 
                    options=options_utility, 
                    key="utility", 
                    label_visibility="collapsed", 
                    width="stretch"
                )  
            with st.container(border=True, key=sub_keys[2], width="stretch", height=pill_group_height, vertical_alignment="center"):
                col_label, col_options = _style_selector()
                col_label.markdown(TERMS["attribute"])
                col_options.pills(
                    "attribute", 
                    options_attribute, 
                    key="attribute", 
                    disabled=disable_extras, 
                    label_visibility="collapsed", 
                    width="stretch"
                )
            with st.container(border=True, key=sub_keys[3], width="stretch", height=pill_group_height, vertical_alignment="center"):
                col_label, col_options = _style_selector()
                col_label.markdown(TERMS["origin"])
                col_options.pills(
                    "origin", 
                    options_origin, 
                    key="origin", 
                    disabled=disable_extras, 
                    label_visibility="collapsed", 
                    width="stretch"
                )
        
        with col_save_and_event:
            # Save button - validate, compile and save
            # 1. Collect state values
            values = dict()
            for x in presets.keys():
                values[x] = st.session_state[x]
            if type(st.session_state["date"]) is str:
                values["date"] = st.session_state["date"]
            else:
                values["date"] = st.session_state["date"].strftime("%y%m%d")
            if st.session_state["source"] in [TERMS["common_source"], TERMS["gift"]]: values["state"] = None
            if st.session_state["source"] == TERMS["gift"]: values["attempt"] = None
            object_database = secretary.collect_database(st.session_state["type"])

            # 2. Checks for proper data setup
            object_testvalue, event_testvalue, old_event_data = [None]*3
            if st.session_state["name"]: object_testvalue = st.session_state["name"].title() in object_database.keys()
            if st.session_state["name"]: 
                if st.session_state["name"] in object_database.keys() and TERMS["event"] in object_database[st.session_state["name"]].keys():
                    event_testvalue = len(object_database[st.session_state["name"]][TERMS["event"]])
                    old_event_data = object_database[st.session_state["name"]][TERMS["event"]]
            data_is_valid, save_button_msg, is_utility = _data_validation(options_reg, values, st.session_state["regset"], object_testvalue, event_testvalue)

            # 3. Compile the data on press IF all data present, else disable button
            data_is_collected, name, new_data, new_event, event_date = _compile_data(values, data_is_valid, save_button_msg, is_utility, highlight_textstyle, highlight_html)
            if data_is_collected: 
                object_type = st.session_state["type"]
                new_data = _adjust_event_data(name, new_data, options_reg, old_event_data, new_event, event_date)

                # 4. Save the data. For editing data, ask for renaming in dialog box
                if st.session_state["regset"] == list(options_reg.keys())[3]:
                    secretary._rename(name, object_type, new_data, options_reg[reg_setting], highlight_textstyle, highlight_html)
                else:
                    if "Delete" in reg_setting:
                        _user_confirm(secretary, name, object_type, new_data, options_reg[reg_setting], reg_setting, values["date"])
                    else:
                        secretary.update_object(name, object_type, new_data, options_reg[reg_setting], None)

            # Info about how and when object was collected
            # Date collector/viewer
            options_dates = list()
            if st.session_state["regset"] == list(options_reg.keys())[4] and st.session_state["name"]: 
                options_dates = object_database[st.session_state["name"]][TERMS["event"]].keys()
            # else:
            #     options_dates = None
            _date_viewer(data_options, options_reg, options_dates)

            # source selector
            st.selectbox(
                f"{TERMS["source"]}", 
                options_source, 
                index=0, 
                key="source", 
                on_change=_update_source_state, 
                args=(attempts, st.session_state["type"]), 
                label_visibility="visible"
            )
            # state selector
            source = _translate_source(st.session_state["type"], st.session_state["source"])
            options_state = data_options["state_alternatives"]
            single_state = False
            if st.session_state["source"] in [TERMS["common_source"], TERMS["gift"]]: single_state = True
            st.selectbox(
                "Success", 
                options_state, 
                index=0, 
                key="state", 
                placeholder="Win or loose?", 
                disabled=single_state, 
                label_visibility="collapsed"
            )

            # attempt input - attempt and limit autogenerated from progress data
            if not source == TERMS["gift"]:  
                limit = attempts[source]["limit"]
                st.number_input(f"{TERMS["attempt"]}", min_value=0, max_value=limit, key="attempt")
            else:
                limit = 0
                st.number_input(f"{TERMS["attempt"]}", min_value=0, max_value=limit, key="attempt", disabled=True)

            # Change options
            st.button("Edit options", key="edit_options", on_click=secretary.edit_options, type="secondary", width="stretch")
            
                

def _feature_style(component_key):
    st.html("<style> .st-key-REF {min-width: 1000px;} </style>".replace("REF", component_key))
def _style_form():
    return st.columns([0.8, 0.2], vertical_alignment="center")
def _style_selector():
    return st.columns([0.1, 0.9], vertical_alignment="center")
def _style_target():
    return st.columns([5, 5], vertical_alignment="center")


def _date_viewer(data_options, options_reg, options_dates):
    # Preset earliest date defined in options file, and latest as today
    date_min = data_options["value_limits"]["date"][0]
    date_min = datetime.datetime(
        int("20"+date_min[0:2]),
        int(date_min[2:4]), 
        int(date_min[4:6]))
    date_max = datetime.date.today()
    disable_dates = False
    # Delete event at date sets the list of event dates as options
    if st.session_state["regset"] == list(options_reg.keys())[4]:
        disable_dates = False if st.session_state["name"] else True
        st.selectbox(
            f"Select date", 
            options_dates, 
            key="date", 
            disabled=disable_dates, 
            label_visibility="collapsed"
        )
    # Standard setting, write date or select by calender
    else:
        try:
            st.session_state["date"].strftime("%y%m%d")
        except:
            st.session_state["date"] = datetime.date.today()
        st.date_input(
            "First received", 
            min_value=date_min, 
            max_value=date_max, 
            key="date", 
            label_visibility="collapsed"
        )    


def _update_source_state(attempts, data_type):
    source = _translate_source(data_type, st.session_state["source"])
    if not source == TERMS["gift"]: 
        st.session_state["attempt"] = attempts[source][TERMS["attempt"]]
    else:
        st.session_state["attempt"] = None
# Convert source name to collect correct attempt data
def _translate_source(data_type, source):
    if source == TERMS["temp"]:
        source = f"{TERMS["main"]} {source}" if data_type == TERMS["main"] else f"{TERMS["utility"]} {source}"
    elif source == TERMS["common_source"]:
        st.session_state["state"] = None
    return source


def _data_validation(options_reg, values, reg_setting, object_testvalue, event_testvalue):
    # Checks for proper data setup
    # Adjust validity check and "save"-button message for clarity
    # "Already in library" - to avoid losing data objects shall not be added more than once
    if reg_setting == list(options_reg.keys())[0] and object_testvalue:
        data_is_valid, save_button_msg = False, "Already in library"
    # "Delete object"
    elif reg_setting == list(options_reg.keys())[2]:
        data_is_valid, save_button_msg = True, f"Delete {st.session_state["type"]}"
    # "Delete object event" - removing collection info of object at date
    elif reg_setting == list(options_reg.keys())[4]:
        save_button_msg = f"Delete {TERMS["event"]}"
        # Do not attempt if event data is empty - should only occur after previous deletion
        data_is_valid = True if event_testvalue else False
    # "Save" - use case for adding new object or editing without deletion
    else:
        data_is_valid, save_button_msg = True, "Save"
    # Main type of object or utilitarian object
    is_utility = values["type"] == TERMS["utility"]

    return data_is_valid, save_button_msg, is_utility


def _compile_data(values, data_is_valid, save_button_msg, is_utility, highlight_textstyle, highlight_html):
    # Mark tasks as finished
    name_done, utility_done, attribute_done, origin_done, state_done = [False]*5
    if data_is_valid:
        disable_extras = values["type"] == TERMS["utility"]
        if values["name"]: name_done = True
        if values["utility"]: utility_done = True
        if not disable_extras:
            if values["attribute"]: attribute_done = True
            if values["origin"]: origin_done = True
        else:
            attribute_done, origin_done = True, True
        if not values["state"]:
            if values["source"] == TERMS["common_source"] or values["source"] == TERMS["gift"]: state_done = True
        else:
            state_done = True
    # When finished, build data dictionary
    if all([name_done, utility_done, attribute_done, origin_done, state_done]):
        name = values["name"].title()
        new_data = dict()
        new_data[name] = dict()
        if not is_utility:
            new_data[name][TERMS["origin"]] = values["origin"]
            new_data[name][TERMS["attribute"]] = values["attribute"]
            new_data[name][TERMS["utility"]] = values["utility"]
        else:
            new_data[name]["Type"] = values["utility"]
        attempt_data = {
            TERMS["source"]: values["source"],
            TERMS["attempt"]: values["attempt"],
            "state": values["state"]
        }
        st.html(highlight_html.replace("KEY_REF", "save").replace("COLOR_REF", highlight_textstyle))
        data_is_collected = st.button(f"{save_button_msg}", key="save", type="primary", width="stretch")
        return data_is_collected, name, new_data, attempt_data, values["date"]
    else:
        st.button(f"{save_button_msg}", key="save", type="secondary", disabled=True, width="stretch")
        return False, None, None, None, None


def _adjust_event_data(name, new_data, options_reg, old_event_data, new_event, event_date):
    if st.session_state["regset"] == list(options_reg.keys())[3]:
        new_data[name][TERMS["event"]] = old_event_data
    elif st.session_state["regset"] in [list(options_reg.keys())[0], list(options_reg.keys())[1], list(options_reg.keys())[4]]:
        event_data = dict() if st.session_state["regset"] == list(options_reg.keys())[0] else old_event_data
        if st.session_state["regset"] != list(options_reg.keys())[4]: 
            now = datetime.datetime.now()
            hhmm = now.strftime("%H%M")
            event_data[f"{event_date}-{hhmm}"] = new_event
        else:
            event_data.pop(event_date)
        if len(event_data) > 0: 
            event_data = dict(sorted(event_data.items()))
        new_data[name][TERMS["event"]] = event_data
    
    return new_data


@st.dialog(f"Removing object data")
def _user_confirm(secretary, name, object_type, new_data, edit_settings, removal_object, removal_date):
    if removal_object == "Delete entry":
        st.markdown(f"Remove {name} from library?")
    elif removal_object == f"Delete {TERMS["event"].lower()}":
        st.markdown(f"Remove {TERMS["event"].lower()} of {name} at 20{removal_date[:2]}-{removal_date[2:4]}-{removal_date[4:6]}?")
    st.space("xsmall")
    col_left, col_right = st.columns(2)
    if col_left.button("Confirm", type="secondary", width="stretch"):
        secretary.update_object(name, object_type, new_data, edit_settings, None)
    if col_right.button("Cancel", type="secondary", width="stretch"):
        st.rerun()


