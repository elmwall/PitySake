"""
Assistant functionality for object registration

Secretary (class):
- Collect database and retrieve info about object 
- User input
- Direct backup and save of data to file
"""

import copy
import datetime
import logging

import streamlit as st

from app.initialize import arciv, DATAPATH, TERMS
import app.data_access as hold
import app.error_handler as error


DIAGNOSTICS = False
logger = logging.getLogger(__name__)


class Secretary:
    def __init__(self, data_options: dict, attempts: dict, 
                 component_key: str, sub_keys: list):
        """
        Tools needed for accessing files and data necessary for editing object library.
        """
        logger.info("Initiating Secretary")

        self.paths = DATAPATH
        self.options = data_options
        self.attempts = attempts
        self.key = component_key
        self.subkeys = sub_keys

        self.attempt_ref = TERMS["attempt"]
        self.attribute_ref = TERMS["attribute"]
        self.event_ref = TERMS["event"]
        self.main_ref = TERMS["main"]
        self.origin_ref = TERMS["origin"]
        self.progress_ref = TERMS["progress"]
        self.secondary_ref = TERMS["secondary"]
        self.source_ref = TERMS["source"]
        self.state_ref = TERMS["state"]
        self.staterand_ref = TERMS["state_rand"]
        self.utility_ref = TERMS["utility"]
        self.utility_sec_ref = TERMS["utility"]


    def settings(self) -> tuple:
        """
        Returns options for selection 
        - collects options from database and project data options
        - defines setting values for all registration options 

        Returns:
            Tuple (dict, dict, list):
                selectable_options (dict): lists of options for all widgets
                registration_options (dict): sets keys and bools for add/delete/edit info
                required_keys (list): required data for compiling
        """ 
        try:
            options_object = list(st.session_state["current_database"].keys())
        except:
            options_object = list(hold.load_main_database().keys())

        if self.options:
            preset_options = {
                "options_utility": self.options[self.main_ref][self.utility_ref],
                "options_object": options_object,
                "options_attribute": self.options[self.main_ref][self.attribute_ref],
                "options_origin": self.options[self.main_ref][self.origin_ref],
                "options_type": [self.main_ref, self.secondary_ref],
                "options_source": list(st.session_state["active_trackers"].keys()),
                "options_states": self.options["results"]}
        else:
            preset_options = {
                "options_utility": None,
                "options_object": None,
                "options_attribute": None,
                "options_origin": None,
                "options_type": None,
                "options_source": None,
                "options_states": None}

        required_keys = [
            "reg_utility", "reg_attribute", "reg_origin", "reg_name", 
            "reg_object_type", "reg_state", "reg_source", "reg_attempt", "reg_date"]

        registration_options = {
            "add_new": {
                "reg_key": f"Add new",
                "is_static": False,
                "for_deletion": False,
                "for_renaming": False
            },
            "add_event": {
                "reg_key": "New event",
                "is_static": True,
                "for_deletion": False,
                "for_renaming": False
            },
            "del_entry": {
                "reg_key": "Delete/Convert",
                "is_static": False,
                "for_deletion": True,
                "for_renaming": False
            },
            "edit_entry": {
                "reg_key": "Edit info",
                "is_static": True,
                "for_deletion": False,
                "for_renaming": True
            },
            "del_event": {
                "reg_key": f"Edit event",
                "is_static": True,
                "for_deletion": False,
                "for_renaming": False
            }
        }

        return preset_options, registration_options, required_keys
    

    def collect_object_info(self, reg_selected: str):
        "Retrieves info from existing object in library to session state."
        # Predefined settings collected from object details in library
        reg_name = st.session_state["reg_name"]
        current_database = st.session_state["current_database"]
        if reg_name not in current_database:
            pass
        elif reg_name and not reg_selected == "add_new":
            settings = current_database[reg_name]
            if st.session_state["reg_type"] == self.main_ref:
                st.session_state["reg_utility"] = settings[self.utility_ref]
                st.session_state["reg_attribute"] = settings[self.attribute_ref]
                st.session_state["reg_origin"] = settings[self.origin_ref]
            else:
                st.session_state["reg_utility"] = settings[self.utility_sec_ref]
                st.session_state["reg_attribute"] = None
                st.session_state["reg_origin"] = None


    def collect_database(self):
        "Retrieves database self-contained deepcopy of databases to session state."
        reg_object_type = st.session_state["reg_object_type"]
        object_is_main = reg_object_type == self.main_ref
        no_selection = not reg_object_type
        if object_is_main or no_selection:
            st.session_state["current_database"] = copy.deepcopy(
                hold.load_main_database())
            st.session_state["reg_type"] = self.main_ref
            return hold.load_main_database()
        if reg_object_type == self.secondary_ref:
            st.session_state["current_database"] = copy.deepcopy(
                hold.load_secondary_database())
            st.session_state["reg_type"] = self.secondary_ref
            return hold.load_secondary_database()


    def data_validation(self, preset_keys: list, reg_selected: str, 
                        object_in_library: bool, event_length: int | None) -> tuple: 
        """
        Validation control before save-button acitvation
        - Adjusts selections to valid formats (date formats and None values)
        - Checks whether action is compatible with database and input states
        - Sets save button tip text

        Args:
            preset_keys (list):
                session state keys for all required values
            reg_selected (str):
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
            st.session_state["translated_values"][x] = st.session_state.get(x, None)

        # Remove leading/trailing whitespaces from name
        reg_name = st.session_state["reg_name"]
        name_invalid = False
        if reg_name: 
            st.session_state["translated_values"]["reg_name"] = reg_name.strip()
            name_invalid = self.symbol_validation(reg_name.strip())

        reg_date = st.session_state["reg_date"]
        if isinstance(reg_date, str):
            st.session_state["translated_values"]["reg_date"] = reg_date
        elif not st.session_state["translated_values"]["reg_date"]:
            pass
        else:
            adjusted_date = reg_date.strftime("%y%m%d")
            st.session_state["translated_values"]["reg_date"] = adjusted_date

        reg_source = st.session_state["reg_source"]
        if self.options and reg_source:
            # If value or state disabled, set None
            if not self.options["states"][reg_source]: 
                st.session_state["translated_values"]["reg_state"] = None
            if not self.options["source_limit"][reg_source]: 
                st.session_state["translated_values"]["reg_attempt"] = None
        else:
            st.session_state["translated_values"]["reg_state"] = None
            st.session_state["translated_values"]["reg_attempt"] = None
        
        # "Already in library" 
        # - to avoid losing data, prevent adding same object more than once
        if reg_selected == "add_new" and object_in_library:
            data_is_valid, save_button_msg = False, "Already exists"
        elif name_invalid:
            data_is_valid, save_button_msg = False, name_invalid
        # "Delete/convert object"
        elif reg_selected == "del_entry":
            if st.session_state["convert_type"]:
                if st.session_state["convert_already_exists"]:
                    data_is_valid, save_button_msg = False, f"Already exists"
                else:
                    data_is_valid, save_button_msg = True, f"Convert object"
            else:
                data_is_valid, save_button_msg = True, f"Delete object"
        # "Delete object event" 
        # - removing collection info of object at date
        elif reg_selected == "del_event":
            save_button_msg = f"Edit {self.event_ref}"
            # Do not attempt if event data is empty 
            # - should only occur after previous deletion
            data_is_valid = True if event_length else False
        # "Save" to existing: adding events, or editing info without deletion
        else:
            data_is_valid, save_button_msg = True, "Save"
        # Main type of object or utilitarian object
        is_secondary = st.session_state["translated_values"]["reg_object_type"] == self.secondary_ref
        return data_is_valid, save_button_msg, is_secondary


    def checklist(self, data_is_valid: bool) -> list:
        """
        Checks whether all data which must be included in a save is complete.
        - name: object name,
        - labels: utility, attribute, origin 
            (exceptions for attribute/origin for secondary)
        - event: date, source, state, attempt 
            (exceptions depending on settings and choice)

        Args:
            data_is_valid (bool):
                prior check of data format and validity

        Returns:
            (list):
                bools for all data checks
        """
        tasklist = ["name_done", "utility_done", "attribute_done", 
                    "origin_done", "source_done", "state_done", "attempt_done"]
        data_checks = dict()
        translated_values = st.session_state["translated_values"]
        for x in tasklist:
            data_checks[x] = False
        if data_is_valid:
            # Secondary object has attribute and origin labels disabled
            disable_extras = translated_values.get("reg_object_type", None) == self.secondary_ref
            include_event = st.session_state["include_event"]
            # Completion checks
            # Name
            if translated_values.get("reg_name", None): 
                data_checks["name_done"] = True
            
            # Labels: all for main, only utility for secondary
            if translated_values.get("reg_utility", None): 
                data_checks["utility_done"] = True
            if not disable_extras:
                if translated_values.get("reg_attribute", None): 
                    data_checks["attribute_done"] = True
                if translated_values.get("reg_origin", None): 
                    data_checks["origin_done"] = True
            else:
                data_checks["attribute_done"], data_checks["origin_done"] = True, True
            # Override labels as completed if irrelevant registration setting
            if st.session_state["reg_selected"] in ["del_entry", "add_event", "del_event"]: 
                for x in ["utility_done", "attribute_done", "origin_done"]:
                    data_checks[x] = True
            
            # Source
            reg_source = translated_values.get("reg_source", None)
            reg_state = translated_values.get("reg_state", None)
            if not reg_source:
                if not include_event: 
                    data_checks["source_done"] = True
            else:
                data_checks["source_done"] = True
            
            if include_event:
                data_checks["state_done"] = False
                data_checks["attempt_done"] = False
            else:
                data_checks["state_done"] = True
                data_checks["attempt_done"] = True
            # State and limit can be excluded if states or values, respectively, are disabled for source
            # of if include event is not enabled by user
            if self.options and reg_source:
                # State
                if not reg_state:
                    if any([not self.options["states"][reg_source], 
                            not include_event]): 
                        data_checks["state_done"] = True
                else:
                    data_checks["state_done"] = True
            
                # Limit
                if translated_values["reg_attempt"] is None:
                    if any([not self.options["source_limit"][reg_source],
                            not include_event]): 
                        data_checks["attempt_done"] = True
                else:
                    data_checks["attempt_done"] = True

        return list(data_checks.values())
    

    def symbol_validation(self, word: str, strict: bool = False) -> str|bool:
        """
        Validation of format of input text

        Args:
            word (str):
                value collected from text input field
            strict (bool):
                True for sensitive values (file names)

        Returns:
            (tuple):
                msg (str|bool):
                    tool tip message and regulator for save button
        """
        msg = False
        if word:
            if not strict:
                valid_symbols = (
                    "-", " ", "_", "–", "—", "'", '"', "&", ".", "*", "!", "?", "%", "§",
                    "(", ")", "[", "]", "{", "}", "/", "+", "<", ">", "@", "#", "=")
                invalid_first = (" ")
            else:
                valid_symbols = ("-", " ")
                invalid_first = ("-", " ")
            max_length = 40
            min_length = 0
            length_check = len(word) > min_length and len(word) < max_length

            if length_check:
                if "  " in word:
                    msg = "2× space in name"
                if word[0] in invalid_first:
                    msg = "Invalid first character"
                if not word.isalnum():
                    for symbol in word:
                        if not symbol.isalnum() and symbol not in valid_symbols:
                            msg = "Invalid name"
            else:
                msg = "Too long. "
        return msg


    @st.dialog(f"Editing object data")
    def confirm_deletion(self, name: str, object_type: str, new_data: dict, event_date: str|None, 
                         reg_setting: dict, reg_selected: str, removal_date: str):
        """
        User confirmation dialog box applied in the following cases:  
        - Confirm removal of object  
        - Confirm conversion of object type  
            - Informs user of consequences: loss of labels / added blanks  
            - Adjusts data accordingly  
            - Calls for addition update to other database type, then removal update in original database  
        - Confirm removal or changing info of an event  
            - Removes old event data and/or adds new data and calls for update
        """
        st.session_state["dialog_active"] = True
        new_date = None
        edited_data = copy.deepcopy(new_data)
        for_conversion = st.session_state["convert_type"]

        # Info section
        # Delete/convert object
        if reg_selected == "del_entry":
            msg = "Remove from library?" if not for_conversion else "Convert object?"
            st.markdown(msg)
            st.markdown(f"### **{name}**")
            if for_conversion:
                st.space()
                if object_type == self.main_ref:
                    # if name in hold.load_secondary_database():
                    st.warning(f"""
                    #### Move from {self.main_ref} to {self.secondary_ref} database:

                    This will discard the labels for {self.attribute_ref} and {self.origin_ref}.""")
                elif object_type == self.secondary_ref:
                    # if name in hold.load_main_database():
                    st.warning(f"""
                    #### Move from {self.secondary_ref} to {self.main_ref} database:

                    This will add blank labels for {self.attribute_ref} and {self.origin_ref}, which can be changed manually via *Update library: Edit info*.""")
        # Delete event
        elif reg_selected == "del_event" and st.session_state["delete_event"]:
            msg = "Remove from library?"
            st.markdown(msg)
            st.markdown(f"### {TERMS["event"]} of {name}")
            st.markdown(f"""at 20{removal_date[:2]}-
                        {removal_date[2:4]}-{removal_date[4:6]}, 
                        ID: {removal_date[7:13]}""")
        # Change event info
        elif reg_selected == "del_event"and not st.session_state["delete_event"]:
            msg = "Change event information?"
            st.markdown(msg)
            st.markdown(f"### {TERMS["event"]} of {name}")
            st.markdown(f"""at 20{removal_date[:2]}-
                        {removal_date[2:4]}-{removal_date[4:6]}, 
                        ID: {removal_date[7:13]}""")
            st.space()
            st.markdown("New information:")
            col_margin, col_indent, col_tab = st.columns([1, 5, 10])
            for x, y in new_data[name]["event"][event_date].items():
                col_indent.markdown(x)
                col_tab.markdown(y)
            st.space()
            col_margin, col_indent, col_tab = st.columns([1, 5, 10])
            change_date = col_indent.checkbox("Change date?", value=False)
            # Event date change 
            # - collect date info
            # - removing and adding with new date ID
            if change_date: 
                date_min = None
                data_options = hold.load_options()
                if len(data_options) > 0: date_min = data_options["value_limits"]["date"][0]
                if date_min:
                    date_min = datetime.datetime(
                        int("20"+date_min[0:2]),
                        int(date_min[2:4]), 
                        int(date_min[4:6]))
                date_max = datetime.date.today()
                new_date = col_tab.date_input(
                    "New date", min_value=date_min, max_value=date_max, label_visibility="collapsed")
                now = datetime.datetime.now()
                hhmmss = now.strftime("%H%M%S")
                edited_event = f"{new_date.strftime("%y%m%d")}-{hhmmss}"
                event_data = new_data[name]["event"][event_date]
                edited_data[name]["event"].pop(event_date)
                edited_data[name]["event"][edited_event] = event_data
                edited_data[name]["event"] = dict(sorted(edited_data[name]["event"].items()))
            else:
                col_tab.date_input("New date", disabled=True, label_visibility="collapsed")
        
        # Confirm/Cancel user interaction
        st.space()
        col_left, col_right = st.columns(2)
        if col_left.button(
                "Confirm", type="secondary", width="stretch"):
            st.session_state["reg_object_type"] = None
            conversion_state = False
            if for_conversion:
                # Adjust label data, then add to other database
                # Ajust processed data sync settings (conversion_state) after update
                conversion_settings = self.settings()[1]["add_new"]
                if object_type == self.main_ref:
                    edited_data[name].pop(self.attribute_ref)
                    edited_data[name].pop(self.origin_ref)
                    new_type = self.secondary_ref
                elif object_type == self.secondary_ref:
                    edited_data[name].update(
                        {self.attribute_ref: "_Blank_", self.origin_ref: "_Blank_"})
                    new_type = self.main_ref
                self.update_object(
                    name, new_type, edited_data, conversion_settings, None, conversion=True)
                conversion_state = "Done"
            # Remove from original database
            self.update_object(
                name, object_type, edited_data, reg_setting, None, conversion=conversion_state)
        if col_right.button(
                "Cancel", type="secondary", width="stretch"):
            st.rerun()
    

    @st.dialog(f"Editing library entry")
    def rename(self, name: str, object_type: str, new_data: dict, 
               reg_setting: dict, current_database: dict, highlight_html: str):
        """
        If edit object info selected, object name can be changed here.  
        Copies all previously defined options as-is.
        """
        # User selection - edit name or not
        st.write(f"You are editing {name}")
        new_name = name
        keep_name = st.checkbox("Keep previous name", value=True)

        # Enter new name
        name_update = st.text_input(
            "Rename", placeholder="Enter name", 
            disabled=keep_name, label_visibility="collapsed")
        
        # Checks and user indication depending on whether to keep name
        # or if name should be replaced and new name is entered
        disable = not any([name_update and not keep_name, keep_name])
        new_name = name if keep_name else name_update
        name_invalid = self.symbol_validation(new_name.strip())
        object_in_library = new_name.strip() in current_database
        msg = "Confirm"
        if name_invalid:
            disable = True
            msg = name_invalid
        elif object_in_library and not keep_name:
            disable = True
            msg = "Already exists"

        st.space()
        if disable:
            st.button(msg, type="secondary" , disabled=True)
        else: 
            st.html(highlight_html.replace("KEY_REF", "rename"))
            if st.button(
                    msg, key="rename", type="primary", disabled=False):
                self.update_object(
                    name, object_type, new_data, reg_setting, new_name.strip())
                # Reload the update the list of objects and auto-close dialog box
                st.rerun()


    def update_object(self, name: str, object_type: str, new_data: dict, 
                      reg_setting: dict, new_name: str|None, conversion: bool = False):
        """
        Saving registered info to file
        - Directs settings for correct editing of database
        - Sends data for backup then to file editing
        - Set states for processed data - calls cache re-sync of changed data only
        """

        # Rename truth-check also carries new name, define as new_name from rename
        if reg_setting["for_renaming"]: 
            for_renaming = new_name
        else:
            for_renaming = reg_setting["for_renaming"]
        for_deletion = reg_setting["for_deletion"]
        is_static = reg_setting["is_static"]
        datafile = self.paths[object_type]
        if DIAGNOSTICS: datafile = "nofile.json"
        logger.info(f"Update called for {datafile}")
        backup_frequency = [101, 31, 11, 2]
        # Secure new data in case of errors
        error.catch_data(
            new_data, datafile, object_type, name, 
            for_deletion, for_renaming, 
            join_path="data", need_sorting=True, is_static=is_static,
            stage="pre_backup", prefix=object_type)
        updated_library = False
        # Backup old data before save
        if arciv.backup(backup_frequency, object_type, set_file=datafile, empty_allowed=True): 
            updated_library = arciv.join_data(
                new_data, name, for_deletion, for_renaming, 
                set_file=datafile, join_path="data", 
                need_sorting=True, is_static=is_static)
        edits_successful = False
        if updated_library: 
            edits_successful = True
        elif isinstance(updated_library, dict) and for_deletion:
            edits_successful = True
        else:
            st.rerun()
        # Save to file
        if DIAGNOSTICS: updated_library = False
        if edits_successful:
            arciv.writer(
                updated_library, object_type, set_file=datafile, join_path="data")
            if conversion:
                is_done = conversion == "Done"
                st.session_state["processed_edits"] = {
                    "clear_options": False,
                    "clear_main": is_done,
                    "clear_secondary": is_done,
                    "clear_progress": False}
                if is_done: st.rerun()
            elif object_type == self.main_ref:
                st.session_state["processed_edits"] = {
                    "clear_options": False,
                    "clear_main": True,
                    "clear_secondary": False,
                    "clear_progress": False}
                st.rerun()
            elif object_type == self.secondary_ref:
                st.session_state["processed_edits"] = {
                    "clear_options": False,
                    "clear_main": False,
                    "clear_secondary": True,
                    "clear_progress": False}
                st.rerun()