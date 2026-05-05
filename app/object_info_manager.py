import datetime
import streamlit as st

from .data_access import Holder
from settings.config import SETTINGS


class Secretary:
    def __init__(self, arciv, DATAPATH, TERMS, data_options, attempts, component_key, sub_keys):
        """
        Collection of all utilitys needed for accessing files and data necessary for editing object library.
        """

        self.arciv = arciv
        self.paths = DATAPATH
        self.terms = TERMS
        self.options = data_options
        self.attempts = attempts
        self.key = component_key
        self.subkeys = sub_keys
        self.hold = Holder()


    def initiate(self):
        presets = {
            "utility": None,
            "attribute": None,
            "origin": None,
            "name": None,
            "type": self.terms["main"],
            "state": self.options["state_alternatives"][0],
            "source": self.terms["temp"],
            "attempt": self.attempts[f"{self.terms["main"]} {self.terms["temp"]}"][self.terms["attempt"]],
            "date": datetime.date.today()
        }

        for x, y in presets.items():
            if x not in st.session_state:
                st.session_state[x] = y
        
        if "dialog_active" not in st.session_state.keys(): st.session_state["dialog_active"] = False
        
        return presets


    def settings(self, data_type):
        object_database = self.collect_database(data_type)
        options_utility = self.options[self.terms["main"]][self.terms["utility"]]
        options_object = object_database.keys()
        options_attribute = self.options[self.terms["main"]][self.terms["attribute"]]
        options_origin = self.options[self.terms["main"]][self.terms["origin"]]
        options_type = [self.terms["main"], self.terms["utility"]]
        options_source = self.options["source"]
        
        options_reg = dict()
        add_new, options_reg[add_new] = "Add completely new", [False, False, False]
        add_event, options_reg[add_event] = f"New {self.terms["event"].lower()} of old", [True, False, False]
        del_entry, options_reg[del_entry] = "Delete entry", [False, True, False]
        edit_entry, options_reg[edit_entry] = "Edit details", [False, False, True]
        del_event, options_reg[del_event] = f"Delete {self.terms["event"].lower()}", [True, False, False]

        return object_database, options_utility, options_object, options_attribute, options_origin, options_type, options_source, options_reg 
    

    def collect_object_info(self, object_database, reg_setting, options_reg):
        # Predefined settings collected from object details in library
        name, data_type = st.session_state["name"], st.session_state["type"]
        if name not in object_database.keys():
            pass
        elif name and not reg_setting == list(options_reg.keys())[0]:
            settings = object_database[name]
            if data_type == self.terms["main"]:
                st.session_state["utility"] = settings[self.terms["utility"]]
                st.session_state["attribute"] = settings[self.terms["attribute"]]
                st.session_state["origin"] = settings[self.terms["origin"]]
            else:
                st.session_state["utility"] = settings[self.terms["utility"]]


    def collect_database(self, set_type):
        if set_type == self.terms["main"]:
            object_database = self.hold.load_main_database()
        if set_type == self.terms["utility"]:
            object_database = self.hold.load_utility_database()
        return object_database
    

    @st.dialog(f"Editing library entry")
    def _rename(self, name, object_type, new_data, reg_setting, highlight_textstyle, highlight_html):
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


    def update_object(self, name, object_type, new_data, edit_setting, new_name):
        is_static, for_deletion, for_renaming = edit_setting
        # Rename truth-check also carries new name, define as new_name from _rename
        if for_renaming: for_renaming = new_name
        datafile = self.paths[object_type]
        backup_frequency = [101, 31, 11, 2]
        self.arciv.catch_data(new_data, datafile, object_type, name, for_deletion, for_renaming, join_path="data", need_sorting=True, is_static=is_static)
        updated_library = False
        if self.arciv.backup(backup_frequency, object_type, other_file=datafile): 
            updated_library, action_verification = self.arciv.join_data(new_data, name, for_deletion, for_renaming, other_file=datafile, join_path="data", need_sorting=True, is_static=is_static)
        if updated_library:
            self.arciv.writer(updated_library, object_type, other_file=datafile, join_path="data")
            print(f"\nLibrary updated, {action_verification}!\n")
            if object_type == self.terms["main"]:
                self.hold.load_main_database.clear()
            elif object_type == self.terms["utility"]:
                self.hold.load_utility_database.clear()
            st.rerun()


    @st.dialog("Edit options")
    def edit_options(self):
        if "edit_options_complete" not in st.session_state.keys(): st.session_state["edit_options_complete"] = False
        col_main, col_p = st.columns([1, 0.01])
        col_1, col_2, col_3, col_4, col_5 = st.columns([2, 3, 3, 3, 2])
        st.session_state["dialog_active"] = False
        for x in ["new_option", "new_state", "new_limit"]:
            if x not in st.session_state.keys(): st.session_state[x] = None
        print("chwe0")
        st.session_state["edited_options"] = list()
        with col_main:
            with st.container(border=False, height=310):
                name_edit, st.session_state["changed_progress"], selection, no_options, requirements, option_ref = self._initiate_optionedit()     
                if name_edit:
                    if st.checkbox("Remove option", value=False, key="remove_option"):
                        placeholder = "No removable options" if no_options else None
                        st.selectbox("Select option", options=st.session_state["remove_options"], key="selected_removal", on_change=self._reset_changes, disabled=no_options, placeholder=placeholder)
                        if col_2.button("Confirm", disabled=no_options, width="stretch"):
                            print(selection)
                            if selection == option_ref["edit_source"]:
                                # if "selected_removal" in st.session_state["changed_options"]["source"]:
                                st.session_state["changed_options"]["source"].remove(st.session_state["selected_removal"].capitalize())
                                st.session_state["changed_options"]["limit"].pop(st.session_state["selected_removal"].capitalize())
                                # if "selected_removal" in st.session_state["changed_progress"].keys():
                                st.session_state["changed_progress"].pop(st.session_state["selected_removal"].capitalize())
                            else:
                                # if "selected_removal" in st.session_state["changed_options"][self.terms["main"]][selection]:
                                st.session_state["changed_options"][self.terms["main"]][selection].remove(st.session_state["selected_removal"])
                            st.session_state["edit_options_complete"] = True
                            # st.session_state["remove_options"] = self._initiate_optionedit(full=False, prev_sel=selection)
                            # st.session_state["remove_options"].remove(st.session_state["selected_removal"])
                    else:
                        not_valid = True
                        if selection in [option_ref["edit_utility"], option_ref["edit_attribute"], option_ref["edit_origin"]]:
                            st.text_input("Enter name for new option. Mind spelling.", key="new_option")
                            if st.session_state["new_option"]:
                                not_valid, msg = self._validity_check(name=st.session_state["new_option"])
                                if msg: st.markdown(f":red[{msg}]")
                            if col_2.button("Confirm", disabled=not_valid, width="stretch"): 
                                st.session_state["changed_options"][self.terms["main"]][selection].append(st.session_state["new_option"].capitalize())
                                # st.session_state["remove_options"] = self._initiate_optionedit(full=False, prev_sel=selection)
                                # st.session_state["remove_options"].append(st.session_state["new_option"].capitalize())
                                st.session_state["edited_options"].append(selection)
                                st.session_state["edit_options_complete"] = True
                        elif selection == option_ref["edit_source"]:
                            st.text_input(f"Enter name for new {self.terms["source"]}. Mind spelling.", key="new_option")
                            col_left, col_right = st.columns(2)
                            new_limit = col_left.number_input(f"Enter new max value.", min_value=0)
                            state_options = [f"{self.terms["state_rand"]}", "Constant"]
                            selected_state = col_right.selectbox("Set state options", options=state_options)
                            new_state = None if selected_state == "Constant" else f"{self.terms["state_rand"]}"
                            if st.session_state["new_option"]:
                                not_valid, msg = self._validity_check(name=st.session_state["new_option"], number=new_limit)
                                if msg: st.markdown(f":red[{msg}]")
                            if col_2.button("Confirm", disabled=not_valid, width="stretch"):
                                st.session_state["changed_options"]["source"].append(st.session_state["new_option"].capitalize())
                                st.session_state["changed_options"]["limit"][st.session_state["new_option"].capitalize()] = new_limit
                                print("2", st.session_state["changed_progress"])
                                st.session_state["changed_progress"][st.session_state["new_option"].capitalize()] = {
                                    f"{self.terms["attempt"]}": 0,                                
                                    f"{self.terms["state"]}": new_state,
                                    "limit": new_limit,                             
                                }
                                print(st.session_state["changed_progress"])
                                st.session_state["edited_options"].append(selection)
                                st.session_state["edit_options_complete"] = True
                elif selection == option_ref["change_limits"]:
                    print("chwe1")
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
                        print(st.session_state["changed_options"])
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
                # st.session_state["changed_options"] = self.hold.load_options()
                # st.session_state["edited_options"] = list()
                # for x in ["new_option", "new_state", "new_limit"]:
                #     st.session_state[x] = None
                # st.session_state["edit_options_complete"] = False
            edited_str = str()

        
        print("prog1", st.session_state["changed_progress"])
        not_complete = not st.session_state["edit_options_complete"]
        if col_4.button("Save", disabled=not_complete, width="stretch"):
            changed_options = st.session_state["changed_options"]
            del st.session_state["changed_options"]
            self.hold.load_options.clear()
            if st.session_state["options_to_edit"] in [option_ref["edit_source"], option_ref["change_limits"]]:
                print("prog2", st.session_state["changed_progress"])
                changed_progress = st.session_state["changed_progress"]
                del st.session_state["changed_progress"]
                self.hold.load_progress_data.clear()
                # self.arciv.catch_data(changed_progress, self.paths["progress"], "progress")
                # if self.arciv.backup([201, 107, 47, 37, 13], self.terms["progress"], other_file=self.paths["progress"]):
                self.arciv.writer(changed_progress, object_type=self.terms["progress"], other_file=self.paths["progress"], join_path="data")
            self.arciv.catch_data(changed_options, SETTINGS["Options"], "options")
            if self.arciv.backup([7, 5, 3, 1], "options", other_file=SETTINGS["Options"]): 
                self.arciv.writer(changed_options, other_file=SETTINGS["Options"], join_path="settings")
                st.session_state["processed_edits"] = True
                for key in st.session_state.keys():
                    del st.session_state[key]
                st.rerun()

        for x in st.session_state["edited_options"]:
            edited_str += f"{x} "
        if len(edited_str) > 0: 
            st.markdown(f"Changes made in: {edited_str}")
        else:
            st.markdown("No changes")
        
        # print("\n registered")
        # print("editede", st.session_state["edited_options"])
        # try:
        #     print(new_limit)
        # except:
        #     print("no new_limit")
        # try:
        #     print(st.session_state["new_option"])
        # except:
        #     print("no new_option")
        # try:
        #     print(new_state)
        # except:
        #     print("no new_state")

        with st.container(height=150):
            st.json(st.session_state["changed_options"])
        with st.container(height=150):
            st.json(st.session_state["changed_progress"])
            # st.json(changed_progress)


    def _initiate_optionedit(self, full=True, prev_sel=None):
        if "changed_options" not in st.session_state.keys():
            st.session_state["changed_options"] = self.hold.load_options()
        if "changed_progress" not in st.session_state.keys():
            st.session_state["changed_progress"] = self.hold.load_options()
        option_ref = {
            "edit_utility": self.terms["utility"],
            "edit_attribute": self.terms["attribute"],
            "edit_origin": self.terms["origin"],
            "edit_source": self.terms["source"],
            "change_limits": f"{self.terms["attempt"]} limits"
        }
        changed_progress = self.attempts

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
                requirements = self.options[f"{self.terms["main"]}_required"][selection]
                remove_options = [x for x in self.options[self.terms["main"]][selection] if x not in requirements]
            elif selection == option_ref["edit_source"]:
                requirements = self.options["source_required"]
                remove_options = [x for x in self.options["source"] if x not in requirements]
            no_options = len(remove_options) < 1

        st.session_state["remove_options"] = remove_options

        if full:
            return name_edit, changed_progress, selection, no_options, requirements, option_ref
        else:
            remove_options


    def _reset_changes(self):
        st.session_state["changed_options"] = self.hold.load_options()
        st.session_state["changed_progress"] = self.hold.load_progress_data()
        # for x in ["new_option", "new_state", "new_limit"]:
        #     st.session_state[x] = None
        st.session_state["edit_options_complete"] = False

    def _validity_check(self, name=False, number=False):
        # msg_len, msg_sym = [str()]*2
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
            # if not len(option) < max_length: msg += "Too long. "
            # if not symbol_check: msg += "Invalid characters. "
            
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
            

        
                