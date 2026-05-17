"""
Assistant functionality for object registration

Secretary (class):
- Collect database and retrieve info about object
- User input
- Direct backup and save of data to file
"""

import copy
import logging

import streamlit as st

# from .file_manager import Archivist
import app.data_access as hold
import app.error_handler as error
from app.initialize import arciv


DATAPATH = st.session_state["DATAPATH"]
DIRECTORIES = st.session_state["DIRECTORIES"]
SETTINGS = st.session_state["SETTINGS"]
TERMS = st.session_state["TERMS"]
DIAGNOSTICS = False
logger = logging.getLogger(__name__)
# arciv = Archivist(DIRECTORIES, DATAPATH, "nofile")


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
        self.utility_sec_ref = TERMS["secondary_utility"]


    def settings(self) -> tuple:
        """
        Returns options for selection 
        - collects options from database and project data options
        - defines setting values for all registration options 

        Returns:
            Tuple (dict, dict, list):
                selectable_options (dict): lists of options for all widgets
                registration_options: sets keys and bools for add/delete/edit info
                required_keys: required data for compiling
        """
        try:
            options_object = list(st.session_state["current_database"].keys())
        except:
            options_object = list(hold.load_main_database().keys())

        selectable_options = {
            "options_utility": self.options[self.main_ref][self.utility_ref],
            "options_object": options_object,
            "options_attribute": self.options[self.main_ref][self.attribute_ref],
            "options_origin": self.options[self.main_ref][self.origin_ref],
            "options_type": [self.main_ref, self.secondary_ref],
            "options_source": self.options["source"]
        }

        required_keys = [
            "reg_utility", "reg_attribute", "reg_origin", "reg_name", 
            "reg_object_type", "reg_state", "reg_source", "reg_attempt", "reg_date"]

        registration_options = {
            "add_new": {
                "label": "Add completely new",
                "is_static": False,
                "for_deletion": False,
                "for_renaming": False
            },
            "add_event": {
                "label": f"New {self.event_ref.lower()} of old",
                "is_static": True,
                "for_deletion": False,
                "for_renaming": False
            },
            "del_entry": {
                "label": "Delete entry",
                "is_static": False,
                "for_deletion": True,
                "for_renaming": False
            },
            "edit_entry": {
                "label": "Edit details",
                "is_static": False,
                "for_deletion": False,
                "for_renaming": True
            },
            "del_event": {
                "label": f"Delete {self.event_ref.lower()}",
                "is_static": True,
                "for_deletion": False,
                "for_renaming": False
            }
        }

        return selectable_options, registration_options, required_keys
    

    def collect_object_info(self, reg_selection: str):
        "Retrieves info from existing object in library to session state."
        # Predefined settings collected from object details in library
        if st.session_state["reg_name"] not in st.session_state["current_database"].keys():
            pass
        elif st.session_state["reg_name"] and not reg_selection == "add_new":
            settings = st.session_state["current_database"][st.session_state["reg_name"]]
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
        object_is_main = st.session_state["reg_object_type"] == self.main_ref
        no_selection = not st.session_state["reg_object_type"]
        if object_is_main or no_selection:
            st.session_state["current_database"] = copy.deepcopy(
                hold.load_main_database())
            st.session_state["reg_type"] = self.main_ref
            return hold.load_main_database()
        if st.session_state["reg_object_type"] == self.utility_ref:
            st.session_state["current_database"] = copy.deepcopy(
                hold.load_secondary_database())
            st.session_state["reg_type"] = self.secondary_ref
            return hold.load_secondary_database()
        

    @st.dialog(f"Removing object data")
    def confirm_deletion(self, name: str, object_type: str, 
                    new_data: dict, reg_setting: str, reg_selection: str, 
                    removal_date: str):
        """
        User confirmation dialog box.
        - Called to confirm removal of object or event            
        """
        st.session_state["dialog_active"] = True

        # Info section
        if reg_selection == "del_entry":
            st.markdown(f"Remove from library?")
            st.markdown(f"### **{name}**")
        elif reg_selection == "del_event":
            st.markdown(f"Remove from library?")
            st.markdown(f"### {TERMS["event"]} of {name}")
            st.markdown(f"""at 20{removal_date[:2]}-
                        {removal_date[2:4]}-{removal_date[4:6]}?""")
        
        # Confirm/Cancel user interaction
        st.space("xsmall")
        col_left, col_right = st.columns(2)
        if col_left.button(
                "Confirm", type="secondary", width="stretch"):
            st.session_state["reg_object_type"] = None
            self.update_object(
                name, object_type, new_data, reg_setting, None)
        if col_right.button(
                "Cancel", type="secondary", width="stretch"):
            st.rerun()
    

    @st.dialog(f"Editing library entry")
    def rename(self, name: str, object_type: str, new_data: dict, 
               reg_setting: str, highlight_html: str):
        """
        If edit object info selected, object name can be changed here.  
        Copies all previously defined options as-is.
        """
        active_theme = st.session_state["themes"]["active"]
        highlight_textstyle = st.session_state["themes"][active_theme]["highlight_text"]

        # User selection - edit name or not
        st.write(f"You are editing {name}")
        new_name = name
        keep_name = st.checkbox("Keep previous name", value=True)

        # Enter new name
        name_update = st.text_input(
            "Rename", placeholder="Enter name", 
            disabled=keep_name, label_visibility="collapsed")
        
        if not name_update and not keep_name:
            not_updated, appearance, new_name = True, "secondary", None
        elif keep_name:
            st.html(highlight_html.replace("KEY_REF", "rename")
                    .replace("COLOR_REF", highlight_textstyle))
            not_updated, appearance, new_name = False, "primary", name
        else:
            st.html(highlight_html.replace("COLOR_REF", highlight_textstyle))
            not_updated, appearance, new_name = False, "primary", name_update
        if st.button(
                "Confirm", key="rename", type=appearance, disabled=not_updated):
            self.update_object(
                name, object_type, new_data, reg_setting, new_name.title())
            # Reload the update the list of objects and auto-close dialog box
            st.rerun()


    def update_object(self, name: str, object_type: str, 
                      new_data: dict, reg_setting: str, new_name: str):
        """
        Saving registered info to file
        - Directs settings for correct editing of database
        - Sends data for backup then to file editing
        """

        # Rename truth-check also carries new name, define as new_name from rename
        if reg_setting["for_renaming"]: reg_setting["for_renaming"] = new_name
        datafile = self.paths[object_type]
        if DIAGNOSTICS: datafile = "nofile.json"
        logger.info(f"Update called for {datafile}")
        backup_frequency = [101, 31, 11, 2]
        # Secure new data in case of errors
        error.catch_data(
            new_data, datafile, object_type, name, 
            reg_setting["for_deletion"], reg_setting["for_renaming"], 
            join_path="data", need_sorting=True, is_static=reg_setting["is_static"],
            stage="pre_backup", prefix=object_type)
        updated_library = False
        # Backup old data before save
        if arciv.backup(backup_frequency, object_type, other_file=datafile): 
            updated_library = arciv.join_data(
                new_data, name, reg_setting["for_deletion"], reg_setting["for_renaming"], 
                other_file=datafile, join_path="data", 
                need_sorting=True, is_static=reg_setting["is_static"])
        # Save to file
        if DIAGNOSTICS: updated_library = False
        if updated_library:
            arciv.writer(
                updated_library, object_type, other_file=datafile, join_path="data")
            if object_type == self.main_ref:
                st.session_state["processed_edits"] = True
            elif object_type == self.utility_ref:
                st.session_state["processed_edits"] = True
            st.rerun()



            

        
                