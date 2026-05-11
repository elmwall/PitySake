import datetime
import copy

import streamlit as st

import app.data_access as hold
# import app.config_hub as hub
# from settings.config import SETTINGS
# from app.configg import DIRECTORIES, SETTINGS, DATAPATH
from app.config_hub import SETTINGS


class Secretary:
    def __init__(self, arciv, DATAPATH, TERMS, data_options, attempts, component_key, sub_keys):
        """
        Collection of all tools needed for accessing files and data necessary for editing object library.
        """

        self.arciv = arciv
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


    def settings(self, data_type):
        if not st.session_state["reg_type"]: 
            data_type = self.main_ref
        else: 
            data_type = st.session_state["reg_type"]
            
        if data_type == self.main_ref:
            object_database = hold.load_main_database()
        if data_type == self.secondary_ref:
            object_database = hold.load_secondary_database()
        
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

        preset_keys = ["reg_utility", "reg_attribute", "reg_origin", "reg_name", "reg_object_type", "reg_state", "reg_source", "reg_attempt", "reg_date"]

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

        return object_database, options_object, selectable_options, registration_options, preset_keys
    

    def collect_object_info(self, object_database, reg_selection):
        # Predefined settings collected from object details in library
        name, data_type = st.session_state["reg_name"], st.session_state["reg_type"]
        if st.session_state["reg_name"] not in st.session_state["current_database"].keys():
            pass
        elif st.session_state["reg_name"] and not reg_selection == "add_new":
            settings = st.session_state["current_database"][st.session_state["reg_name"]]
            print(st.session_state["reg_type"], settings)
            if st.session_state["reg_type"] == self.main_ref:
                st.session_state["reg_utility"] = settings[self.utility_ref]
                st.session_state["reg_attribute"] = settings[self.attribute_ref]
                st.session_state["reg_origin"] = settings[self.origin_ref]
            else:
                st.session_state["reg_utility"] = settings[self.utility_sec_ref]
                st.session_state["reg_attribute"] = None
                st.session_state["reg_origin"] = None


    def collect_database(self):
        if st.session_state["reg_object_type"] == self.main_ref or not st.session_state["reg_object_type"]:
            st.session_state["current_database"] = copy.deepcopy(hold.load_main_database())
            st.session_state["reg_type"] = self.main_ref
            return hold.load_main_database()
        if st.session_state["reg_object_type"] == self.utility_ref:
            st.session_state["current_database"] = copy.deepcopy(hold.load_secondary_database())
            st.session_state["reg_type"] = self.secondary_ref
            return hold.load_secondary_database()
    

    @st.dialog(f"Editing library entry")
    def rename(self, name, object_type, new_data, reg_setting, highlight_html):
        active_theme = hold.load_themes()["active"]
        highlight_textstyle = hold.load_themes()[active_theme]["highlight_text"]
        st.write(f"You are editing {name}")
        new_name = name
        keep_name = st.checkbox("Keep previous name", value=True)
        name_update = st.text_input("Rename", placeholder="Enter name", disabled=keep_name, label_visibility="collapsed")
        if not name_update and not keep_name:
            not_updated, appearance, new_name = True, "secondary", None
        elif keep_name:
            st.html(highlight_html.replace("KEY_REF", "rename").replace("COLOR_REF", highlight_textstyle))
            not_updated, appearance, new_name = False, "primary", name
        else:
            st.html(highlight_html.replace("COLOR_REF", highlight_textstyle))
            not_updated, appearance, new_name = False, "primary", name_update
        if st.button("Confirm", key="rename", type=appearance, disabled=not_updated):
            self.update_object(name, object_type, new_data, reg_setting, new_name.title())
            # Reload the update the list of objects and auto-close dialog box
            st.rerun()


    def update_object(self, name, object_type, new_data, reg_setting, new_name):
        # Rename truth-check also carries new name, define as new_name from rename
        if reg_setting["for_renaming"]: reg_setting["for_renaming"] = new_name
        datafile = self.paths[object_type]
        backup_frequency = [101, 31, 11, 2]
        # Secure data in case of errors
        self.arciv.catch_data(
            new_data, 
            datafile, 
            object_type, 
            name, 
            reg_setting["for_deletion"], 
            reg_setting["for_renaming"], 
            join_path="data", 
            need_sorting=True, 
            is_static=reg_setting["is_static"],
            stage="pre_backup",
            prefix=object_type
        )
        updated_library = False
        if self.arciv.backup(backup_frequency, object_type, other_file=datafile): 
            updated_library, action_verification = self.arciv.join_data(
                new_data, 
                name, 
                reg_setting["for_deletion"], 
                reg_setting["for_renaming"], 
                other_file=datafile, 
                join_path="data", 
                need_sorting=True, 
                is_static=reg_setting["is_static"]
            )
        if updated_library:
            self.arciv.writer(
                updated_library, 
                object_type, 
                other_file=datafile, 
                join_path="data"
            )
            print(f"\nLibrary updated, {action_verification}!\n")
            if object_type == self.main_ref:
                st.session_state["processed_edits"] = True
                # hold.load_main_database.clear()
            elif object_type == self.utility_ref:
                st.session_state["processed_edits"] = True
                # hold.load_secondary_database.clear()
            st.rerun()


    @st.dialog("Edit options")
    def edit_options(self):
        st.session_state["edit_options_complete"] = False
        st.session_state["dialog_active"] = False
        col_main, col_p = st.columns([1, 0.01])
        col_1, col_2, col_3, col_4, col_5 = st.columns([2, 3, 3, 3, 2])
        st.session_state["edited_options"] = list()
        with col_main:
            with st.container(border=False, height=310):
                name_edit, selection, no_options, requirements, option_ref = self._initiate_option_edit()     
                if name_edit:
                    if st.checkbox("Remove option", value=False, key="remove_option"):
                        placeholder = "No removable options" if no_options else None
                        st.selectbox("Select option", options=st.session_state["remove_options"], key="selected_removal", on_change=self._reset_changes, disabled=no_options, placeholder=placeholder)
                        if col_2.button("Confirm", disabled=no_options, width="stretch"):
                            if selection == option_ref["edit_source"]:
                                st.session_state["changed_options"]["source"].remove(st.session_state["selected_removal"].capitalize())
                                st.session_state["changed_options"]["limit"].pop(st.session_state["selected_removal"].capitalize())
                                st.session_state["changed_progress"].pop(st.session_state["selected_removal"].capitalize())
                            else:
                                st.session_state["changed_options"][self.main_ref][selection].remove(st.session_state["selected_removal"])
                            st.session_state["edit_options_complete"] = True
                    else:
                        not_valid = True
                        if selection in [option_ref["edit_utility"], option_ref["edit_attribute"], option_ref["edit_origin"]]:
                            st.text_input("Enter name for new option. Mind spelling.", key="new_option")
                            if st.session_state["new_option"]:
                                not_valid, msg = self._validity_check(name=st.session_state["new_option"])
                                if msg: st.markdown(f":red[{msg}]")
                            if col_2.button("Confirm", disabled=not_valid, width="stretch"): 
                                st.session_state["changed_options"][self.main_ref][selection].append(st.session_state["new_option"].capitalize())
                                st.session_state["edited_options"].append(selection)
                                st.session_state["edit_options_complete"] = True
                        elif selection == option_ref["edit_source"]:
                            st.text_input(f"Enter name for new {self.source_ref}. Mind spelling.", key="new_option")
                            col_left, col_right = st.columns(2)
                            new_limit = col_left.number_input(f"Enter new max value.", min_value=1)
                            state_options = [f"{self.staterand_ref}", "Constant"]
                            selected_state = col_right.selectbox("Set state options", options=state_options)
                            new_state = None if selected_state == "Constant" else f"{self.staterand_ref}"
                            if st.session_state["new_option"]:
                                not_valid, msg = self._validity_check(name=st.session_state["new_option"], number=new_limit)
                                if msg: st.markdown(f":red[{msg}]")
                            if col_2.button("Confirm", disabled=not_valid, width="stretch"):
                                st.session_state["changed_options"]["source"].append(st.session_state["new_option"].capitalize())
                                st.session_state["changed_options"]["limit"][st.session_state["new_option"].capitalize()] = new_limit
                                st.session_state["changed_progress"][st.session_state["new_option"].capitalize()] = {
                                    f"{self.attempt_ref}": 0,                                
                                    f"{self.state_ref}": new_state,
                                    "limit": new_limit,                             
                                }
                                st.session_state["edited_options"].append(selection)
                                st.session_state["edit_options_complete"] = True
                elif selection == option_ref["change_limits"]:
                    limit_options = self.options["limit"]
                    limit_cat = st.selectbox("Select category to change", options=limit_options.keys())
                    if type(limit_options[limit_cat]) is dict:
                        limit_subcat_options = limit_options[limit_cat].keys()
                        no_sub = False
                    else:
                        limit_subcat_options = None
                        no_sub = True
                    
                    limit_subcat = st.selectbox("Select subcategory", options=limit_subcat_options, disabled=no_sub)
                    current_value = limit_options[limit_cat] if no_sub else limit_options[limit_cat][limit_subcat]
                    new_limit = st.number_input(f"Enter new max value. Current value: {current_value}", min_value=0)
                    not_valid, msg = self._validity_check(number=new_limit)
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
                self._reset_changes()
            edited_str = str()

        not_complete = not st.session_state["edit_options_complete"]
        if col_4.button("Save", disabled=not_complete, width="stretch"):
            
            if st.session_state["options_to_edit"] in [option_ref["edit_source"], option_ref["change_limits"]]:
                self.arciv.writer(st.session_state["changed_progress"], object_type=self.progress_ref, other_file=self.paths["progress"], join_path="data")
            self.arciv.catch_data(st.session_state["changed_options"], SETTINGS["Options"], "options")
            if self.arciv.backup([7, 5, 3, 1], "options", other_file=SETTINGS["Options"]): 
                self.arciv.writer(st.session_state["changed_options"], other_file=SETTINGS["Options"], join_path="settings")
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


    def _initiate_option_edit(self, full=True, prev_sel=None):
        print("11111", st.session_state["changed_options"])
        if "changed_options" not in st.session_state:
            st.session_state["changed_options"] = copy.deepcopy(hold.load_options())
        elif not st.session_state["changed_options"]:
            st.session_state["changed_options"] = copy.deepcopy(hold.load_options())
        
        if "changed_options" not in st.session_state:
            st.session_state["changed_progress"] = copy.deepcopy(hold.load_progress_data())
        elif not st.session_state["changed_progress"]:
            st.session_state["changed_progress"] = copy.deepcopy(hold.load_progress_data())
            
        option_ref = {
            "edit_utility": self.utility_ref,
            "edit_attribute": self.attribute_ref,
            "edit_origin": self.origin_ref,
            "edit_source": self.source_ref,
            "change_limits": f"{self.attempt_ref} limits"
        }
        st.session_state["changed_progress"] = self.attempts

        if full:
            selection = st.selectbox("Select option to edit", options=list(option_ref.values()), key="options_to_edit", on_change=self._reset_changes)
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
                requirements = self.options[f"{self.main_ref}_required"][selection]
                remove_options = [x for x in self.options[self.main_ref][selection] if x not in requirements]
            elif selection == option_ref["edit_source"]:
                requirements = self.options["source_required"]
                remove_options = [x for x in self.options["source"] if x not in requirements]
            no_options = len(remove_options) < 1

        st.session_state["remove_options"] = remove_options

        if full:
            return name_edit, selection, no_options, requirements, option_ref
        else:
            remove_options


    def _reset_changes(self):
        st.session_state["changed_options"] = hold.load_options()
        st.session_state["changed_progress"] = hold.load_progress_data()
        st.session_state["edit_options_complete"] = False


    def _validity_check(self, name=False, number=False):
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
            

        
                