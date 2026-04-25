import streamlit as st
import datetime


class Secretary:
    def __init__(self, arciv, negotiator, DATAPATH, TERMS, data_options, attempts, component_key, sub_keys):
        """
        Collection of all tools needed for accessing files and data necessary for editing object library.
        """

        self.arciv = arciv
        self.nestor = negotiator
        self.paths = DATAPATH
        self.terms = TERMS
        self.options = data_options
        self.attempts = attempts
        self.key = component_key
        self.subkeys = sub_keys
    
    def _initiate(self):
        presets = {
            "tool": None,
            "attribute": None,
            "origin": None,
            "name": None,
            "type": "Character",
            "state": self.options["State alternatives"][0],
            "source": self.terms["Temp"],
            "attempt": self.attempts[f"Character {self.terms["Temp"]}"][self.terms["Attempt"]],
            "date": datetime.date.today()
        }
        return presets

    def _settings(self, data_type):
        object_database = self._collect_database(data_type)
        options_tool = self.options[self.terms["Character"]][self.terms["Tool"]]
        options_object = object_database.keys()
        options_attribute = self.options[self.terms["Character"]][self.terms["Attribute"]]
        options_origin = self.options[self.terms["Character"]][self.terms["Origin"]]
        options_type = ["Character", self.terms["Tool"]]
        options_source = self.options["Source"]
        
        options_reg = dict()
        add_new, options_reg[add_new] = "Add completely new", [False, False, False]
        add_event, options_reg[add_event] = f"New {self.terms["Event"].lower()} of old", [True, False, False]
        del_entry, options_reg[del_entry] = "Delete entry", [False, True, False]
        edit_entry, options_reg[edit_entry] = "Edit details", [False, False, True]
        del_event, options_reg[del_event] = f"Delete {self.terms["Event"].lower()}", [True, False, False]

        return object_database, options_tool, options_object, options_attribute, options_origin, options_type, options_source, options_reg 
    
    def _collect_object_info(self, object_database, reg_setting, options_reg):
        # Predefined settings collected from object details in library
        name, data_type = st.session_state["name"], st.session_state["type"]
        if name not in object_database.keys():
            pass
        elif name and not reg_setting == list(options_reg.keys())[0]:
            settings = object_database[name]
            if data_type == "Character":
                st.session_state["tool"] = settings[self.terms["Tool"]]
                st.session_state["attribute"] = settings[self.terms["Attribute"]]
                st.session_state["origin"] = settings[self.terms["Origin"]]
            else:
                st.session_state["tool"] = settings["Type"]

    def _collect_database(self, set_type):
        if set_type == "Character":
            data_reference = self.terms["Character"]
        else:
            data_reference = set_type
        datafile = self.paths[data_reference]
        object_database = self.arciv.reader(datafile, join_path="data")
        return object_database
    
    @st.dialog(f"Editing library entry")
    def _rename(self, name, object_type, new_data, reg_setting):
        st.write(f"You are editing {name}")
        new_name = name
        keep_name = st.checkbox("Keep previous name", value=True)
        name_update = st.text_input("Rename", placeholder="Enter name", disabled=keep_name, label_visibility="collapsed")
        if not name_update and not keep_name:
            not_updated, appearance, new_name = True, "secondary", None
        elif keep_name:
            not_updated, appearance, new_name = False, "primary", name
        else:
            not_updated, appearance, new_name = False, "primary", name_update
        if st.button("Confirm", type=appearance, disabled=not_updated):
            self._update_object(name, object_type, new_data, reg_setting, new_name.title())
            # Reload the update the list of objects and auto-close dialog box
            st.rerun()

    def _update_object(self, name, object_type, new_data, edit_setting, new_name):
        is_static, for_deletion, for_renaming = edit_setting
        # Rename truth-check also carries new name, define as new_name from _rename
        if for_renaming: for_renaming = new_name
        datafile = self.paths[object_type]
        backup_frequency = [101, 31, 11, 2]
        if self.arciv.backup(self.nestor, backup_frequency, object_type[:6]+"_data"): 
            updated_library, action_verification = self.arciv.join_data(new_data, name, for_deletion, for_renaming, other_file=datafile, join_path="data", need_sorting=True, is_static=is_static)
        if updated_library:
            self.arciv.writer(updated_library, other_file=datafile, join_path="data")
            print(f"\nLibrary updated, {action_verification}!\n")
            # Reload the update the list of objects
            st.rerun()
    

def register_object(component_key, sub_keys, arciv, negotiator, DIRECTORIES, DATAPATH, data_options, TERMS, attempts):
    _feature_style(component_key)
    secretary = Secretary(arciv, negotiator, DATAPATH, TERMS, data_options, attempts, component_key, sub_keys)

    # Header
    with st.container(key=f"{component_key}_head", width=1000, height=35):
        st.markdown("#### *Update library*",  text_alignment="left")
    # Main container
    with st.container(border=True, key=f"{component_key}_main", width=1000, height="content"):
        # Collect presets and initiate session states
        presets = secretary._initiate()
        for x, y in presets.items():
            if x not in st.session_state:
                st.session_state[x] = y
            elif not st.session_state[x]: 
                st.session_state[x] = y

        # Define all initial features settings, options and limits
        object_database, options_tool, options_object, options_attribute, options_origin, options_type, options_source, options_reg = secretary._settings(st.session_state["type"])
        disable_extras = False

        # Build widgets
        col_object_info, col_save_and_event = _style_form()
        pill_group_height = 60
        with col_object_info:
            # Action selector field - what to do with the data
            with st.container(key=sub_keys[0], width="stretch", height=pill_group_height, vertical_alignment="center"):
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
                        on_change=secretary._collect_object_info, 
                        args=(TERMS, object_database, reg_setting, options_reg), 
                        label_visibility="collapsed"
                    )
            with col_type:
                type_selected = st.pills(
                    "Object type", options_type, key="type", label_visibility="collapsed"
                )
                disable_extras = type_selected == TERMS["Tool"]
            
            # Object details - "tool" utilitarian object disables extras i.e. "attribute" and "origin"
            with st.container(key=sub_keys[1], width="stretch", height=pill_group_height, vertical_alignment="center"):
                col_label, col_options = _style_selector()
                col_label.markdown(TERMS["Tool"])
                col_options.pills(
                    "Tool", 
                    options=options_tool, 
                    key="tool", 
                    label_visibility="collapsed", 
                    width="stretch"
                )  
            with st.container(key=sub_keys[2], width="stretch", height=pill_group_height, vertical_alignment="center"):
                col_label, col_options = _style_selector()
                col_label.markdown(TERMS["Attribute"])
                col_options.pills(
                    "Attribute", 
                    options_attribute, 
                    key="attribute", 
                    disabled=disable_extras, 
                    label_visibility="collapsed", 
                    width="stretch"
                )
            with st.container(key=sub_keys[3], width="stretch", height=pill_group_height, vertical_alignment="center"):
                col_label, col_options = _style_selector()
                col_label.markdown(TERMS["Origin"])
                col_options.pills(
                    "Origin", 
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
            if st.session_state["source"] == TERMS["Standard source"]: values["state"] = None
            if st.session_state["source"] == TERMS["Gift"]: values["attempt"] = None
            object_database = secretary._collect_database(st.session_state["type"])

            # 2. Checks for proper data setup
            object_testvalue, event_testvalue, old_event_data = [None]*3
            if st.session_state["name"]: object_testvalue = st.session_state["name"].title() in object_database.keys()
            if st.session_state["name"]: 
                if st.session_state["name"] in object_database.keys() and TERMS["Event"] in object_database[st.session_state["name"]].keys():
                    event_testvalue = len(object_database[st.session_state["name"]][TERMS["Event"]])
                    old_event_data = object_database[st.session_state["name"]][TERMS["Event"]]
            data_is_valid, save_button_msg, is_tool = _data_validation(TERMS, options_reg, values, st.session_state["regset"], object_testvalue, event_testvalue)

            # 3. Compile the data on press IF all data present, else disable button
            data_is_collected, name, new_data, new_event, event_date = _compile_data(TERMS, values, data_is_valid, save_button_msg, is_tool)
            if data_is_collected: 
                object_type = TERMS[f"CLI{st.session_state["type"]}"]
                new_data = _adjust_event_data(TERMS, name, new_data, options_reg, old_event_data, new_event, event_date)

                # 4. Save the data. For editing data, ask for renaming in dialog box
                if st.session_state["regset"] == list(options_reg.keys())[3]:
                    secretary._rename(name, object_type, new_data, options_reg[reg_setting])
                else:
                    secretary._update_object(arciv, negotiator, DATAPATH, name, object_type, new_data, options_reg[reg_setting], None)

            # Info about how and when object was collected
            # Date collector/viewer
            options_dates = list()
            if st.session_state["regset"] == list(options_reg.keys())[4] and st.session_state["name"]: 
                options_dates = object_database[st.session_state["name"]][TERMS["Event"]].keys()
            # else:
            #     options_dates = None
            _date_viewer(data_options, options_reg, options_dates)
            
            # Source selector
            st.selectbox(
                f"{TERMS["Source"]}", 
                options_source, 
                index=0, 
                key="source", 
                on_change=_update_source_state, 
                args=(TERMS, attempts, st.session_state["type"]), 
                label_visibility="visible"
            )

            # State selector
            source = _translate_source(TERMS, st.session_state["type"], st.session_state["source"])
            options_state = data_options["State alternatives"]
            single_state = False
            if st.session_state["source"] == TERMS["Standard source"] or st.session_state["source"] == TERMS["Gift"]: single_state = True
            st.selectbox(
                "Success", 
                options_state, 
                index=0, 
                key="state", 
                placeholder="Win or loose?", 
                disabled=single_state, 
                label_visibility="collapsed"
            )

            # Attempt input - attempt and limit autogenerated from progress data
            if not source == TERMS["Gift"]:  
                limit = attempts[source]["Limit"]
                st.number_input(f"{TERMS["Attempt"]}", min_value=0, max_value=limit, key="attempt")
            else:
                limit = 0
                st.number_input(f"{TERMS["Attempt"]}", min_value=0, max_value=limit, key="attempt", disabled=True)
                

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
    date_min = data_options["Value limits"]["Date"][0]
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


def _update_source_state(TERMS, attempts, data_type):
    source = _translate_source(TERMS, data_type, st.session_state["source"])
    if not source == TERMS["Gift"]: 
        st.session_state["attempt"] = attempts[source][TERMS["Attempt"]]
    else:
        st.session_state["attempt"] = None
# Convert source name to collect correct attempt data
def _translate_source(TERMS, data_type, source):
    if source == TERMS["Temp"]:
        source = f"Character {source}" if data_type == "Character" else f"{TERMS["Tool"]} {source}"
    elif source == TERMS["Standard source"]:
        st.session_state["state"] = None
    return source


def _data_validation(TERMS, options_reg, values, reg_setting, object_testvalue, event_testvalue):
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
        save_button_msg = f"Delete {TERMS["Event"]}"
        # Do not attempt if event data is empty - should only occur after previous deletion
        data_is_valid = True if event_testvalue else False
    # "Save" - use case for adding new object or editing without deletion
    else:
        data_is_valid, save_button_msg = True, "Save"
    # Main type of object or utilitarian object
    is_tool = values["type"] == TERMS["Tool"]

    return data_is_valid, save_button_msg, is_tool


def _compile_data(TERMS, values, data_is_valid, save_button_msg, is_tool):
    # Mark tasks as finished
    name_done, tool_done, attribute_done, origin_done, state_done = [False]*5
    if data_is_valid:
        disable_extras = values["type"] == TERMS["Tool"]
        if values["name"]: name_done = True
        if values["tool"]: tool_done = True
        if not disable_extras:
            if values["attribute"]: attribute_done = True
            if values["origin"]: origin_done = True
        else:
            attribute_done, origin_done = True, True
        if not values["state"]:
            if values["source"] == TERMS["Standard source"]: state_done = True
        else:
            state_done = True
    # When finished, build data dictionary
    if all([name_done, tool_done, attribute_done, origin_done, state_done]):
        name = values["name"].title()
        new_data = dict()
        new_data[name] = dict()
        if not is_tool:
            new_data[name][TERMS["Origin"]] = values["origin"]
            new_data[name][TERMS["Attribute"]] = values["attribute"]
            new_data[name][TERMS["Tool"]] = values["tool"]
        else:
            new_data[name]["Type"] = values["tool"]
        attempt_data = {
            TERMS["Source"]: values["source"],
            TERMS["Attempt"]: values["attempt"],
            "State": values["state"]
        }
        data_is_collected = st.button(f"{save_button_msg}", key="save", type="primary", width="stretch")
        return data_is_collected, name, new_data, attempt_data, values["date"]
    else:
        st.button(f"{save_button_msg}", key="save", type="secondary", width="stretch")
        return False, None, None, None, None


def _adjust_event_data(TERMS, name, new_data, options_reg, old_event_data, new_event, event_date):
    if st.session_state["regset"] == list(options_reg.keys())[3]:
        new_data[name][TERMS["Event"]] = old_event_data
    elif st.session_state["regset"] in [list(options_reg.keys())[0], list(options_reg.keys())[1], list(options_reg.keys())[4]]:
        event_data = dict() if st.session_state["regset"] == list(options_reg.keys())[0] else old_event_data
        if st.session_state["regset"] != list(options_reg.keys())[4]: 
            event_data[f"{event_date}-new"] = new_event
        else:
            event_data.pop(event_date)
        adjusted_data = dict()
        event_data = dict(sorted(event_data.items()))
        n = 0
        for x, y in event_data.items():
            adjusted_data[f"{x[:6]}-{n}"] = y
            n += 1
        new_data[name][TERMS["Event"]] = adjusted_data
    
    return new_data


