import os
import shutil

import json
import streamlit as st

from settings.config import TERMS


class Archivist:
    def __init__(self, DIRECTORIES, DATAPATH, file):
        """
        File and data actions for JSON and dictionary data. 
        Functions: reader, writer, backup, join_data

        file : directory of file as string
        """
        self.file = file
        self.data_directory = DIRECTORIES["DataFolder"]
        self.settings_directory = DIRECTORIES["SettingsFolder"]
        self.backup_directory = DIRECTORIES["BackupFolder"]
        self.backup_meta = DATAPATH["backup_meta"]


    def reader(self, other_file=False, join_path="none", is_json=True, allow_missing=False, allow_empty=False):
        """
        Read and return JSON file.

        join_path : set to string "data" or "settings", if *file* is located within *self.data_directory* or *self.settings_directory*.
        """
        
        read_file = self.file if not other_file else other_file

        if join_path == "data":
            read_file = os.path.join(self.data_directory, read_file)
        elif join_path == "settings":
            read_file = os.path.join(self.settings_directory, read_file)
        elif join_path != "none":
            print("Invalid value of pathway indicator 'join_path'.")

        if is_json:
            try:
                with open(read_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except FileNotFoundError:
                if allow_missing:
                    return None
                raise FileNotFoundError(f"{read_file} not found.")
            except json.JSONDecodeError:
                if allow_empty:
                    return None
                raise json.JSONDecodeError(f"{read_file} could not be decoded as JSON.")
            except Exception as e:
                print(f"\nFile at {read_file} could not be read:\n{e}")
                raise
        else:
            try:
                with open(read_file, "r", encoding="utf-8") as f:
                    return f.read()
            except FileNotFoundError:
                if allow_missing:
                    return None
            except Exception as e:
                print(f"\nFile at {read_file} could not be read:\n{e}")
                raise


    def backup(self, backup_frequency:list[int], object_type:str, other_file=False):
        """
        Automated backup in multiple files.  
        Returns: bool

        backup_frequency : list of integers largest-to-smallest; list length sets the number of backup files; integers specifies number of edits between every backup.
        object_type : sets name prefix to specify identify of backup data.
        """

        if "pending_backup" not in st.session_state.keys(): st.session_state["pending_backup"] = None
        if not other_file:
            file = self.file 
        else:
            file = os.path.join(self.data_directory, other_file)
        filename = os.path.splitext(file)[0]
        
        # Call file containing edit count info for all files
        meta_file = os.path.join(self.data_directory, self.backup_meta)
        edit_meta = self.reader(meta_file)
        if file in edit_meta.keys():
            file_edit_count = edit_meta[file]
        else:
            file_edit_count = 0 
        backup_file = False
        
        # Check backup frequencies and set backup file path if any frequency condition is met and update edit meta
        for value in backup_frequency:
            if file_edit_count > 0 and file_edit_count % value == 0:
                print(f"Performing backup for every {value} saves.")
                backup_file = os.path.join(
                    self.backup_directory, 
                    filename + f"_backup_{value}.json")
                break
        edit_meta[file] = file_edit_count + 1
        self.writer(edit_meta, other_file=meta_file)
        backup_file = os.path.join(self.backup_directory, "backuptest_nofile.json") ############ test
        file = os.path.join(self.data_directory, "nofile.json")
        data = self.reader(file, allow_missing=True, allow_empty=True)
        if data:
            file_length = len(data)
        else:
            self._catch_backup_data(data, file, backup_file, object_type)
            self.pending_backup("nodata", data, file, backup_file, object_type)
            return False

        if backup_file and os.path.exists(backup_file):
            backup_length = len(self.reader(backup_file))
        else:
            backup_length = 0

        # Compare contents of backup and current data
        if backup_length > file_length+2:
            self._catch_backup_data(data, file, backup_file, object_type)
            self.pending_backup("tooshort", data, file, backup_file, object_type)
            return False
        else:
            confirm_backup = True

        if not backup_file:
            return True
        elif confirm_backup:
            shutil.copy(file, backup_file)
            print("Data backup done.")
            return True
        

    def join_data(self, new_data:dict, name:str, object_type, for_deletion, for_editing, other_file=False, join_path="none", need_sorting=True, is_static=False):
        """
        Update library with new or edited data.  
        Returns: bool

        new_data : data to be included in file.  
        name : id of new data entry.  
        is_static : marks files that are not expected to increase in length.
        """
        read_file = self.file if not other_file else other_file

        if join_path == "data":
            read_file = os.path.join(self.data_directory, read_file)
        elif join_path == "settings":
            read_file = os.path.join(self.settings_directory, read_file)
        elif join_path != "none":
            print("Invalid value of pathway indicator 'join_path'.")

        data = self.reader(read_file)
        if type(data) is dict: 
            original_length = len(data) 
        else: 
            original_length = 0
            data = dict()
        
        if for_editing:
            edited_data = dict()
            try:
                edited_data[for_editing] = new_data[name]
                new_data = edited_data
                is_static = for_deletion = True
            except:
                raise KeyError(f"Replacing '{name}' in {read_file} could not be performed.")

        if for_deletion:
            try:
                data.pop(name)
            except KeyError:
                raise KeyError(f"Key '{name}' is absent from {read_file}. Check spelling and database content.")
            except TypeError:
                raise TypeError(f"Unable to remove {name}. Check format.")
            
            if len(data) != original_length-1 and not for_editing: 
                raise ValueError(f"Expected a data length decrease after removing {name}.")
            
            if not for_editing:
                return data, f"{name} was removed"
            else:
                name = for_editing

        # Add data to library
        if name in data.keys() and not is_static:
            data.update(new_data)
            action_verification = f"{name} was added"
        elif len(data) != original_length and is_static and not for_deletion: 
            raise ValueError(f"Data length was altered unexpectedly. Library update aborted.")
        else:
            try:
                data.update(new_data)
            except ValueError:
                raise ValueError(f"Unable to update")
            action_verification = f"{name} was added"
        if need_sorting: data = dict(sorted(data.items(), key=lambda item:str(item[0])))

        # Checking data validity depending on previous action. 
        if name not in data.keys():
            raise KeyError(f"Key '{name}' is absent from data. Check database content.")
        elif len(data) != original_length+1 and not is_static:
            raise ValueError(f"Expected data length increase. Library update aborted.")
        else:
            return data, action_verification
        

    def writer(self, data, object_type=None, other_file=False, join_path="none"):
        """
        Write JSON to file. Returns: bool
        """

        save_file = self.file if not other_file else other_file

        if join_path == "data":
            save_file = os.path.join(self.data_directory, other_file)
        elif join_path == "settings":
            save_file = os.path.join(self.settings_directory, other_file)
        elif join_path != "none":
            print(f"Invalid value of pathway switch 'join_path': {join_path}")

        try:
            with open(save_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
                return True
        except json.JSONDecodeError:
            raise json.JSONDecodeError(f"Could not decode data to save in {save_file}.")
        except Exception as e:
            raise RuntimeError(f"Error from {e} occurred while attempting to write to {save_file}. Check file health and backups.")


    @st.dialog("Automatic backup: data deviation")
    def pending_backup(self, mode, data, file, backup_file, datatype):
        file = st.session_state["pending_backup"]["file"]
        backup_file = st.session_state["pending_backup"]["backup_file"]
        data = st.session_state["pending_backup"]["data"]
        confirm_backup = False

        if mode == "nodata":
            # st.markdown("")
            st.markdown(f"""Your data file: `{file}` is empty, 
                        no backup was performed.""")
            st.markdown("**If this is not a fresh library:** please check your files!")
        elif mode == "tooshort":
            confirm_backup = True
            st.markdown("Backup file contains more objects than the data file.")
            st.markdown("**If you have not removed data entries:**: please check your files!")

        with st.expander("How to check/rescue your data"):
            filepath = os.path.realpath(file)
            backup_path = os.path.realpath(self.backup_directory)
            st.markdown(f"Your data file: `{filepath}`")
            st.markdown(f"Your backups: `{backup_path}`")
            st.markdown(f"Check the latest changed backup file (generally lower suffix), open in Notepad. If data is missing in {file}, replace the file or its content with your backup.backup_path")
            
        with st.expander("Review data"):
            with st.container(border=False, width="stretch", height=300):
                st.json(data, width="stretch")

        if self._confirm_action():
            data_details = st.session_state["pending_save"]
            if backup_file and confirm_backup:
                shutil.copy(file, backup_file)
                print("Data backup done.")

            if datatype in [TERMS["main"] or TERMS["utility"]]:
                updated_library, action_verification = self.join_data(
                data_details["new_data"], 
                data_details["name"], 
                data_details["for_deletion"], 
                data_details["for_renaming"], 
                data_details["save_file"], 
                data_details["path"], 
                data_details["need_sorting"], 
                data_details["is_static"]
            )
            elif datatype == TERMS["progress"]:
                updated_library = data_details["new_data"]
                action_verification = "progress added"
        else:
            st.rerun()

        if updated_library:
            self.writer(updated_library, other_file=data_details["save_file"], join_path=data_details["path"])
            print(f"\nLibrary updated, {action_verification}!\n")
            st.session_state["pending_backup"] = None
            st.session_state["pending_save"] = None
            st.rerun()
 



    def catch_data(self, new_data, save_file, object_type, name=None, for_deletion=False, for_renaming=False, datapath="data", need_sorting=False, is_static=False):
        st.session_state["pending_save"] = {
            "name": name,
            "new_data": new_data,
            "for_deletion": for_deletion,
            "for_renaming": for_renaming,
            "save_file": save_file,
            "path": datapath,
            "need_sorting": need_sorting,
            "is_static": is_static,
            "object_type": object_type
        }


    def _catch_backup_data(self, data, file, backup_file, object_type):
        st.session_state["pending_backup"] = {
            "data": data,
            "file": file,
            "backup_file": backup_file,
            "object_type": object_type
        }


    def _confirm_action(self):
        st.markdown("Do you wish to proceed?")
        st.space("xsmall")
        col_left, col_right = st.columns(2)
        if col_left.button("Yes", type="secondary", width="stretch"):
            return True
        if col_right.button("No", type="secondary", width="stretch"):
            return False
        
    