"""
Core file management module

Archivist (class):
- Reading and writing to file
- JSON file management
- Automatic backup
- Protect and rescue data source and target
"""

import json
import logging
import os
import shutil

import streamlit as st

import app.error_handler as error


logger = logging.getLogger(__name__)


class Archivist:
    def __init__(self, DIRECTORIES: dict, DATAPATH: dict, 
                 file: str | None, initialized: bool = True):
        """
        File manager

        Can be used for managing a single datafile (self.file) 
        or more broadly for reading and saving textbased datafiles.

        Tasks:
        - Read file (json/textfiles)
        - Backup in preset intervals
        - Join old data with new for saving
        - Write to file (json)
        - Detect unexpected dataformats -> protect old and new data separately

        Args:
            DIRECTORIES (dict):
                pathways for project files
            DATAPATH (dict):
                filenames for datafiles
            file (str):
                data for processing. Set None for all purpose use.
            initialized (bool):
                check for system state
        """
        self.file = file
        self.data_directory = DIRECTORIES["DataFolder"]
        self.settings_directory = DIRECTORIES["SettingsFolder"]
        self.backup_directory = DIRECTORIES["BackupFolder"]
        self.backup_meta = DATAPATH["backup_meta"]
        self.diagnostics = False

        if initialized:
            self.terms = st.session_state["TERMS"]

        logger.info(f"""
file_manager.Archivist instanced with:
FILE: {self.file}, 
DATA: {self.data_directory}, 
SETTINGS: {self.settings_directory}, 
BACKUP: {self.backup_directory}""")


    def reader(self, set_file :str = None, join_path: str | None = None, 
               is_json: bool = True, allow_missing: bool = False, 
               allow_empty: bool = False) -> dict | bool | None:
        """
        Read and return JSON or other textfile.
        - joins path if directory in argument
        - manages deviation depending on requirements

        Args:
            set_file (str):
                path/filename for non-self.file reading.
            join_path (str):
                file directory for filenames without full path
        
        Returns:
            file content (dict | None):
                typically json-derived dict
        """
        read_file, path_is_resolved = self._resolve_path(
            join_path, set_file, stage="Reading")
        if not path_is_resolved:
            return False
        logger.info(f"""
file_manager.Archivist.reader request: 
FILE: {self.file}, SET_FILE: {set_file}, JOIN_PATH: {join_path}, 
FULL_PATH: {read_file}""")
        
        if is_json:
            try:
                with open(read_file, "r", encoding="utf-8") as f:
                    logger.info(f"Archivist.reader json: {read_file} loaded")
                    return json.load(f)
            except FileNotFoundError:
                if allow_missing:
                    logger.warning(f"No file to read: {read_file}. Exception allowed.")
                    return None
                else:
                    logger.exception(f"\nFailed to read file {read_file}.")
                    error.message("Failed to read file.", "Archivist: Reading", 
                                  name=None, file=read_file, details=None)
                    return False
            except json.JSONDecodeError:
                if allow_empty:
                    logger.warning(f"Empty datafile: {read_file}. Exception allowed.")
                    return None
                else:
                    logger.exception(f"\nFile {read_file} could not be decoded as JSON.")
                    error.message("File content not be interpreted.", "Archivist: Reading", 
                                  name=None, file=read_file, details=None)
                    return False
            except Exception:
                logger.exception(f"\nArchivist.reader failed to read json: {read_file}.")
                error.message("Failed to read file.", f"Archivist: Reading", 
                              name=None, file=read_file, details=None)
                return False
        else:
            try:
                with open(read_file, "r", encoding="utf-8") as f:
                    logger.info(f"Archivist.reader: {read_file} loaded")
                    return f.read()
            except FileNotFoundError:
                if allow_missing:
                    logger.warning(f"No file to read: {read_file}. Exception allowed.")
                    error.message("No file to read.", f"Archivist: Reading", 
                                  name=None, file=read_file, details=None)
                    return None
            except Exception:
                logger.exception(f"\nFailed to read file {read_file}.")
                error.message("Failed to read file.", f"Archivist: Reading", 
                                name=None, file=read_file, details=None)
                return False


    def backup(self, backup_frequency: list[int], 
               object_type: str, set_file: str | None = None) -> bool:
        """
        Automated backup in multiple files.
        - performes backup at listed intervals
        - checks irregularities
            - save backup info and call for user review

        Args:
            backup_frequency (list):
                any number of save intervals between backups, 
                in order [seldom, mid, often]
            set_file (str):
                path/filename for non-self.file backup

        Returns:
            (bool):
                succes check
        """

        # confirm_backup = False
        if not set_file:
            file = self.file 
        else:
            file = os.path.join(self.data_directory, set_file)
            
        # Diagnostic values - uncomment to redirect backup and file
        if self.diagnostics: file = os.path.join(self.data_directory, "nofile.json")

        # Extract filename for naming backup
        filename = os.path.basename(file)
        filename = os.path.splitext(filename)[0]
        
        # Call file containing edit count info for all files
        meta_file = os.path.join(self.data_directory, self.backup_meta)
        edit_meta = self.reader(meta_file)
        if file in edit_meta.keys():
            file_edit_count = edit_meta[file]
        else:
            file_edit_count = 0 

        # Check backup and edit status 
        # - set backup file path if any edit frequency condition is met 
        # - update edit meta
        data = False
        backup_file = False
        for value in backup_frequency:
            if file_edit_count > 0 and file_edit_count % value == 0:
                backup_file = os.path.join(
                    self.backup_directory, 
                    filename + f"_backup_{value}.json")
                logger.info(f"{file} checks for {value}-edit backup.")
                data = self.reader(file, allow_missing=True, allow_empty=True)
                break
            else:
                data = "postpone"
        if backup_file:
            logger.info(f"""
file_manager.Archivist.reader request: 
FILE: {self.file}, SET_FILE: {set_file}, DATATYPE: {object_type}, 
BACKUP_PATH: {backup_file}, EDIT_COUNT: {file_edit_count} mod {value}""")
        edit_meta[file] = file_edit_count + 1
        self.writer(edit_meta, set_file=meta_file)

        if self.diagnostics: 
            backup_file = os.path.join(self.backup_directory, "backuptest_nofile.json")

        if data == "postpone":
            file_length = "not collected"
        elif data:
            file_length = len(data)
        else:
            logger.warning(f"\n{file} backup stopped - new data is empty.")
            st.session_state["pending_backup"] = True
            error.catch_backup_data(
                "nodata", data, file, backup_file, object_type)
            return False

        if backup_file and os.path.exists(backup_file):
            backup_length = len(self.reader(backup_file))
            logger.info(f"""
Backup control: 
datafile length: {file_length}, datafile location: {file}, 
backup length: {backup_length}, backup location: {backup_file}""")
        else:
            backup_length = 0

        # Compare contents of backup and current data
        if data == "postpone":
            backup_file = False
        elif backup_length > file_length+2:
            logger.warning(f"\n{file} backup stopped - data too short.")
            error.catch_backup_data(
                "tooshort", data, file, backup_file, object_type)
            return False
        else:
            confirm_backup = True

        if not backup_file:
            return True
        elif confirm_backup:
            shutil.copy(file, backup_file)
            logger.info(f"Archivist.backup of {file} in in {backup_file} done.")
            return True
        

    def join_data(self, new_data: dict, name: str, 
                  for_deletion: bool, for_editing: bool, 
                  set_file: str | None = None, join_path: str | None = None, 
                  need_sorting: bool = True, is_static: bool = False):
        """
        Update library with new or edited data.
        - depending on settings: add/remove edit entry
        - checks irregularities, aborts risky actions
        
        Args:
            new_data (dict):
                new data value for dict
            name (str):
                new data key for dict
            for_deletion (bool):
                validation controller -> datalength should shrink
            for_editing (bool):
                validation controller -> datalength should remain
            set_file (str | None):
                path/filename for non-self.file to join
            join_path (str | None):
                path for datafile if lacking in name
            need_sorting (bool):
                check triggers dict sorting
            is_static (bool):
                validation controller -> datalength should remain

        Returns:
            data (dict):
                updated data
            action_verification (str):
                message phrase for action performed
        """
        read_file, path_is_resolved = self._resolve_path(
            join_path, set_file, stage="Joining")
        if not path_is_resolved:
            return False
        logger.info(f"""
file_manager.Archivist.join_data request: 
FILE: {read_file}, ADDITION: {name}, 
SETTING: for deletion {for_deletion}, editing-only {for_editing}, 
static {is_static}           sorting {need_sorting}""")

        data = self.reader(set_file=read_file)
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
                logger.info(f"Pre-save editing of {name} performed")
            except:
                logger.exception(f"""\nReplacing '{name}' in {read_file} could not be performed.""")
                error.message(f"Updating {name} could not be performed.", 
                              "Archivist: Joining", name=name, file=read_file, details=None)

        if for_deletion:
            try:
                data.pop(name)
                logger.info(f"""Archivist.join_data pre-save removal of {name} performed.""")
            except KeyError:
                logger.exception(f"""\nKey '{name}' not removed, already absent from {read_file}.""")
                error.message(f"{name} could not be removed, is already absent.", 
                              "Archivist: Joining", name=name, file=read_file, details=None)
                return False
            except TypeError:
                error.message(
                    f"Unable to remove {name}.", "Archivist: Joining", 
                    name=name, file=read_file, details=None)
                return False
            
            if len(data) != original_length-1 and not for_editing: 
                logger.exception(f"""\nExpected a data length decrease after removing {name}.""")
                error.message(f"Expected a data length decrease in {read_file} not detected.", 
                              "Archivist: Joining", name=name, file=read_file, details=None)
                return False
            
            if not for_editing:
                logger.info(f"{name} was removed in data for saving in {read_file}")
                return data
            else:
                name = for_editing

        # Add data to library
        # Case: editing an existing entry in a growing library
        if name in data.keys() and not is_static:
            data.update(new_data)
            logger.info(f"{name} was edited for saving in {read_file}")
        # Abnormal case: a non-growing library has changed length, 
        # without a deletion registered
        elif len(data) != original_length and is_static and not for_deletion: 
            logger.exception(f"\nData length altered unexpectedly. Update aborted.")
            error.message(f"Unexpected difference in {read_file} data length, not saved.", 
                          "Archivist: Joining", name=name, file=read_file, details=None)
            return False
        # Case: add data to a growing library
        else:
            try:
                data.update(new_data)
            except ValueError:
                logger.exception(f"\nUnable to update {read_file} with {name}.")
                error.message(f"Unable to update file with {name}.", 
                              "Archivist: Joining", name=name, file=read_file, details=None)
                return False
            logger.info(f"{name} was added in data for saving in {read_file}")
        if need_sorting: data = dict(sorted(data.items(), key=lambda item:str(item[0])))

        # Checking data validity depending on previous action. 
        if name not in data.keys():
            logger.exception(f"\nFailed to add new data in {read_file} with {name}.")
            error.message("Failed to add new data.", "Archivist: Joining", 
                          name=name, file=read_file, details=None)
            return False
        elif len(data) != original_length+1 and not is_static:
            logger.exception(f"\nExpected data length increase didn't happen in {read_file} with {name}.")
            error.message("Expected data length increase didn't happen.", 
                          "Archivist: Joining", name=name, file=read_file, details=None)
            return False
        else:
            logger.info(f"{name} data joined to {read_file}.")
            return data
        

    def writer(self, data: dict, object_type: str | None = None, 
               set_file: str | None = None, join_path: str | None = None):
        """
        Save file as JSON.

        Args:
            data (dict):
                path/filename for non-self.file reading.
            object_type (str):
                identifier for datatype
            set_file (str):
                filename for non-self.file usage
            join_path (str):
                file directory for filenames without full path
        
        Returns:
            (bool):
                success verification
        """
        save_file, path_is_resolved = self._resolve_path(
            join_path, set_file, stage="Writing")
        try:
            length = len(data)
        except:
            logger.exception(f"\nSave in {save_file} with invalid format aborted.")
            error.message("Save with invalid format aborted.", "Archivist.writer", 
                          name=None, file=save_file, details=None)

        try:
            with open(save_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
                logger.info(f"""
file_manager.Archivist.writer wrote: 
FILE: {save_file}, DATATYPE: {object_type}, DATA_LENGTH: {length}""")
                return True
        except json.JSONDecodeError:
            error.dump(
                "Archivist.writer", {
                    "data": data, "object_type": object_type,
                    "self-file": self.file, "set_file": set_file, "join_path": join_path})
            logger.exception(f"\nCould not decode data to save in {save_file}.")
            error.message("Could not interpret new data for JSON.", "Archivist.writer", 
                          name=None, file=save_file, details=None)
            return False
        except Exception as e:
            logger.exception(f"\nCould not save to {save_file}.")
            error.message("Could not save data.", "Archivist.writer", 
                          name=None, file=save_file, details=None)
            return False


    def _resolve_path(self, join_path, set_file, stage):
        read_file = self.file if not set_file else set_file
        path_is_resolved = True
        if join_path == "data":
            read_file = os.path.join(self.data_directory, read_file)
        elif join_path == "settings":
            read_file = os.path.join(self.settings_directory, read_file)
        elif join_path is not None:
            path_is_resolved = False
            logger.info(f"Invalid value of path indicator 'join_path' for {read_file}.")
            error.message("Invalid file path for datafile.", f"Archivist: {stage}", 
                          name=None, file=read_file, details=None)
        
        return read_file, path_is_resolved
