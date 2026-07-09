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
            from app.initialize import TERMS
            self.terms = TERMS
            
        self._log_creation()


    def reader(self, set_file : str = None, join_path: str | None = None, 
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
        self._log_reading(set_file, join_path, read_file)
        
        message = "Failed to read file"
        file_advice = "Check datafile and folder. Create new data or replace with a backup."
        if is_json:
            stage = "Reading JSON file"
            try:
                with open(read_file, "r", encoding="utf-8") as f:
                    logger.info(f"Reading file:\n    Archivist.reader json: {read_file} loaded")
                    return json.load(f)
            except FileNotFoundError:
                if allow_missing:
                    logger.warning(f"Missing file:\n    No file to read: {read_file}. Exception allowed.")
                    return None
                else:
                    logger.exception(f"Missing file:\n    Failed to read file {read_file}.")
                    error.message(message, stage, name=None, file=read_file, 
                                  details=[f"File not found - {read_file}"], advice=file_advice)
                    return False
            except json.JSONDecodeError:
                if allow_empty:
                    logger.warning(f"JSON error:\n    Non-readable file: {read_file}. Exception allowed.")
                    return None
                else:
                    logger.exception(f"JSON error:\n    File {read_file} could not be decoded as JSON.")
                    error.message(message, stage, name=None, file=read_file, 
                                  details=[f"Invalid JSON format - {read_file}"])
                    return False
            except MemoryError:
                logger.exception(f"File error:\n    Warning! File too big: {read_file}.")
                error.message(message, stage, name=None, file=read_file, 
                                details=["Warning! Abnormal file size."])
            except Exception:
                logger.exception(f"File error:\n    Archivist.reader failed to read json: {read_file}.")
                error.message(message, stage, name=None, file=read_file, 
                              details=[f"Unknown error in file - {read_file}"], advice=file_advice)
                return False
        else:
            stage = "Reading file"
            try:
                with open(read_file, "r", encoding="utf-8") as f:
                    logger.info(f"Reading file:\n    Archivist.reader: {read_file} loaded")
                    return f.read()
            except FileNotFoundError:
                if allow_missing:
                    logger.warning(f"No file to read: {read_file}. Exception allowed.")
                    error.message(message, stage, name=None, file=read_file, 
                                  details=[f"File not found - {read_file}"], advice=file_advice)
                    return None
            except Exception:
                logger.exception(f"\nFailed to read file {read_file}.")
                error.message(message, stage, name=None, file=read_file, 
                              details=[f"Unknown error in file - {read_file}"], advice=file_advice)
                return False


    def backup(self, backup_frequency: list[int], object_type: str, 
               join_path: str | None = None, set_file: str | None = None, 
               empty_allowed: bool = False, len_sensitivity: int = 5) -> bool:
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
            empty_allowed (bool):
                regulates response to empty files
            len_sensitivity (int):
                regulates trigger threshold for shortened data file warning

        Returns:
            (bool):
                succes check
        """

        # confirm_backup = False
        if not set_file:
            file = self.file 
        elif join_path:
            file = self._resolve_path(join_path, set_file, stage="Backup")[0]
        else:
            file = os.path.join(self.data_directory, set_file)
            
        # Diagnostic values - uncomment to redirect backup and file
        if self.diagnostics: file = os.path.join(self.data_directory, "nofile.json")

        # Extract filename for naming backup
        filename = os.path.basename(file)
        filename = os.path.splitext(filename)[0]
        
        # Call file containing edit count info for all files
        meta_file = os.path.join(self.data_directory, self.backup_meta)
        edit_meta = self.reader(meta_file, allow_missing=True)
        if not edit_meta:
            edit_meta = dict()
            file_edit_count = 0
        elif file in edit_meta.keys():
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
        if backup_file: self._log_backup_info(set_file, object_type, backup_file, file_edit_count, value)

        edit_meta[file] = file_edit_count + 1
        self.writer(edit_meta, set_file=meta_file)

        if self.diagnostics: 
            backup_file = os.path.join(self.backup_directory, "backuptest_nofile.json")
        if data == "postpone":
            file_length = "not collected"
        elif data:
            file_length = len(data)
        elif empty_allowed:
            logger.warning(f"Empty data:\n    {file} is empty. Empty allowed but backup not performed.")
            backup_file = False
            file_length = 0
        else:
            logger.warning(f"Empty data:\n    {file} backup stopped - new data is empty.")
            st.session_state["pending_backup"] = True
            error.catch_backup_data(
                "nodata", data, file, backup_file, object_type)
            st.rerun()
            return False

        if backup_file and os.path.exists(backup_file):
            backup_length = len(self.reader(backup_file))
            self._log_backup_check(file_length, file, backup_length, backup_file)
        else:
            backup_length = 0

        # Compare contents of backup and current data
        if data == "postpone":
            backup_file = False
        elif backup_length > file_length + len_sensitivity:
            logger.warning(f"Data length warning:\n    {file} backup stopped - data too short.")
            error.catch_backup_data(
                "tooshort", data, file, backup_file, object_type)
            st.rerun()
            return False
        else:
            confirm_backup = True

        if not backup_file:
            return True
        elif confirm_backup:
            os.makedirs(self.backup_directory, exist_ok=True)
            shutil.copy(file, backup_file)
            logger.info(f"Backup done:\n    Archivist.backup of {file} in in {backup_file} done.")
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
        self._log_joining(read_file, name, for_deletion, for_editing, is_static, need_sorting)

        data = self.reader(set_file=read_file)
        if isinstance(data, dict):
            original_length = len(data) 
        else: 
            original_length = 0
            data = dict()
        
        stage = "Joining data"
        refresh_advice = "If data is not up to date, try refreshing the page."
        if for_editing:
            edited_data = dict()
            try:
                edited_data[for_editing] = new_data[name]
                new_data = edited_data
                is_static = for_deletion = True
                logger.info(f"Pre-save editing of {name}")
            except Exception:
                msg = f"Replacing '{name}' in {read_file} could not be performed."
                logger.exception(f"""Editing error:\n    {msg}""")
                error.message(f"Could not edit {name}", f"{stage}, editing", name=name, file=read_file, 
                              details=[f"{msg}, changes not saved"], advice=refresh_advice)
        
        length_message = "Data length issue"
        if for_deletion:
            try:
                data.pop(name)
                logger.info(f"""Joining performed:\n    Archivist.join_data pre-save removal of {name} done.""")
            except KeyError:
                phrase = "edited" if for_editing else "removed"
                if for_editing: delete_for_edit = " for editing"
                msg = f"Key '{name}' not {phrase}, absent from {read_file}."
                logger.exception(f"""Editing error\n    {msg}""")
                error.message(f"No {name} to remove", f"{stage}, deleting{phrase}", 
                              name=name, file=read_file, 
                              details=[f"{msg}, changes not saved"], 
                              advice=refresh_advice)
                return False
            except TypeError:
                error.message(
                    f"Unable to remove {name}.", stage, name=name, file=read_file, 
                    details=f"Unable to remove {name} - wrong type.")
                return False
            
            if len(data) != original_length-1 and not for_editing: 
                msg = f"Expected a data length decrease after removing {name}."
                logger.exception(f"Data length error:\n    {msg}")
                error.message(length_message, f"{stage}, deleting", name=name, file=read_file, 
                              details=[f"{msg}, changes not saved"],
                              advice="""Data might already be abscent, try refreshing.  \n
                              Inconsistencies with backup files might block editing.""")
                return False
            
            if not for_editing:
                logger.info(f"Data removed:\n    {name} was removed in data for saving in {read_file}")
                return data
            else:
                name = for_editing

        save_message = "Could not save data"
        # Add data to library
        # Case: editing an existing entry in a growing library
        if name in data.keys() and not is_static:
            data.update(new_data)
            logger.info(f"Data edited:\n    {name} was edited for saving in {read_file}")
        # Abnormal case: a non-growing library has changed length, 
        # without a deletion registered
        elif len(data) != original_length and is_static and not for_deletion: 
            logger.exception(f"Data length error:\n    Data length altered unexpectedly. Update aborted.")
            info = f"Unexpected difference in {read_file} data length, editing should not alter data length"
            error.message(length_message, stage, name=name, file=read_file, 
                          details=[info], advice="Wrong action occurred or data was corrupted.")
            return False
        # Case: add data to a growing library
        else:
            try:
                data.update(new_data)
            except ValueError:
                msg = f"Unable to update with {name}."
                logger.exception(msg)
                error.message(save_message, f"{stage}, updating", name=name, file=read_file, 
                              details=["Could not save data, received invalid value"],
                              advice="Wrong action occurred or data was corrupted.")
                return False
            logger.info(f"{name} was added in data for saving in {read_file}")
        if need_sorting: data = dict(sorted(data.items(), key=lambda item:str(item[0])))

        # Checking data validity depending on previous action. 
        if name not in data.keys():
            logger.exception(f"Failed to add {name}.")
            error.message(save_message, f"{stage}, updating", name=name, file=read_file, 
                          details=["Tried to add data to file data but failed, unknown error"])
            return False
        elif len(data) != original_length+1 and not is_static:
            logger.exception(f"Data length error:\n    Expected increase in {read_file} with {name}.")
            error.message(save_message, f"{stage}, verifying", name=name, file=read_file, 
                          details=["Expected data length increase didn't happen"],
                          advice="Does the entry you tried to add already exist?")
            return False
        else:
            logger.info(f"Join complete:\n    {name} data joined to {read_file}.")
            return data
        

    def writer(self, data: dict, object_type: str | None = None, 
               set_file: str | None = None, join_path: str | None = None,
               not_json: bool = False, format: str|None = None):
        """
        Save file, primarily as JSON.

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
        save_file = self._resolve_path(join_path, set_file, stage="Writing")[0]
        message = "Error while saving"
        stage = "Writing to file"
        advice = "Check that data hasn't been affected, otherwise retrieve your data from backup or dump file."

        if not_json:
            try:
                with open(save_file, "w") as f:
                    f.write(data)
                    return True
            except Exception:
                logger.exception(f"Writing error:\n    Save in {save_file} failed. Format: {format}.")


        try:
            length = len(data)
        except Exception:
            logger.exception(f"Writing error:\n    Save in {save_file} with invalid format aborted.")
            error.message(message, stage, name=None, file=save_file, 
                          details=["Data for writing file could not be read as an iterable"],
                          advice=advice)

        try:
            with open(save_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
                self._log_datasave(save_file, object_type, length)
                return True
        except json.JSONDecodeError:
            error.dump(
                "Archivist.writer", {
                    "data": data, "object_type": object_type,
                    "self-file": self.file, "set_file": set_file, "join_path": join_path})
            logger.exception(f"Writing error:\n    Could not decode data to save in {save_file}.")
            error.message(message, stage, name=None, file=save_file, 
                          details=["Could not interpret new data as JSON for writing file."], advice=advice)
            return False
        except Exception:
            logger.exception(f"Writing error:\n    Could not save to {save_file}.")
            error.message(message, stage, name=None, file=save_file, 
                          details=["Could not write to file, unknown error."], advice=advice)
            return False


    def _resolve_path(self, join_path: str|None, set_file: str|None, stage: str) -> tuple:
        """
        Joins file name with declared folder.

        Args:
            join_path (str|None):
                folder name, if any
            set_file (str|None):
                file to read, if not self.file
            stage (str):
                process indicator for log

        Returns:
            Tuple (str, bool):
                read_file (str): official file path
                path_is_resolved (bool): control value for further processes
        """
        target_file = self.file if not set_file else set_file
        path_is_resolved = True
        if join_path == "data":
            logger.info(
                f"Path resolve:\n    Path resolve requested with directory {join_path} for {target_file}.")
            os.makedirs(self.data_directory, exist_ok=True)
            target_file = os.path.join(self.data_directory, target_file)
        elif join_path == "settings":
            logger.info(
                f"Path resolve:\n    Path resolve requested with directory {join_path} for {target_file}.")
            target_file = os.path.join(self.settings_directory, target_file)
        elif join_path is not None:
            path_is_resolved = False
            logger.info(
                f"Path error:\n    Invalid value of path indicator 'join_path' for {target_file}.")
            error.message("Invalid datafile path.", stage, name=None, file=target_file, details=["File paths are indicated as either 'data' or 'settings"])
        elif not join_path:
            logger.info(
                f"Path resolve note:\n    Path resolve requested without directory for {target_file}.")
            path_is_resolved = True
        
        return target_file, path_is_resolved


    def _log_creation(self):
        logger.info(f"""Archivist created: 
    file_manager.Archivist instanced with:
    FILE: {self.file}, 
    DATA: {self.data_directory}, 
    SETTINGS: {self.settings_directory}, 
    BACKUP: {self.backup_directory}""")
        
    def _log_reading(self, set_file, join_path, read_file):
        logger.info(f"""Reading task registered: 
    file_manager.Archivist.reader request: 
    FILE: {self.file}, 
    SET_FILE: {set_file}, 
    JOIN_PATH: {join_path}, 
    FULL_PATH: {read_file}""")
        
    def _log_backup_info(self, set_file, object_type, backup_file, file_edit_count, value):
        logger.info(f"""Backup task registered: 
    file_manager.Archivist.reader request: 
    FILE: {self.file}, 
    SET_FILE: {set_file}, 
    DATATYPE: {object_type}, 
    BACKUP_PATH: {backup_file}, 
    EDIT_COUNT: {file_edit_count} mod {value}""")
        
    def _log_backup_check(self, file_length, file, backup_length, backup_file):
        logger.info(f"""Backup data check: 
    Backup control: 
    datafile length: {file_length}, 
    datafile location: {file}, 
    backup length: {backup_length}, 
    backup location: {backup_file}""")
        
    def _log_joining(self, read_file, name, for_deletion, for_editing, is_static, need_sorting):
        logger.info(f"""Joining task registered: 
    file_manager.Archivist.join_data request: 
    FILE: {read_file}, ADDITION: {name}, 
    SETTING: 
        for deletion {for_deletion}, 
        for_editing {for_editing}, 
        static {is_static}           
        sorting {need_sorting}""")
        
    def _log_datasave(self, save_file, object_type, length):
        logger.info(f"""
    file_manager.Archivist.writer wrote: 
    FILE: {save_file}, 
    DATATYPE: {object_type}, 
    DATA_LENGTH: {length}""")