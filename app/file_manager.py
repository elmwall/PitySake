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
        self.print_spacer = 80

        if initialized:
            self.terms = st.session_state["TERMS"]

        logger.info(f"""
            file_manager.Archivist.__init__ instanced for 
            FILE: {self.file}, 
            DATA: {self.data_directory}, 
            SETTINGS: {self.settings_directory}, 
            BACKUP: {self.backup_directory}""")


    def reader(self, other_file :str = None, join_path: str | None = None, 
               is_json: bool = True, allow_missing: bool = False, 
               allow_empty: bool = False) -> dict | bool | None:
        """
        Read and return JSON or other textfile.
        - joins path if directory in argument
        - manages deviation depending on requirements

        Args:
            other_file (str):
                path/filename for non-self.file reading.
            join_path (str):
                file directory for filenames without full path
        
        Returns:
            file content (dict | None):
                typically json-derived dict
        """
    
        read_file = self.file if not other_file else other_file

        if join_path == "data":
            read_file = os.path.join(self.data_directory, read_file)
        elif join_path == "settings":
            read_file = os.path.join(self.settings_directory, read_file)
        elif join_path:
            logger.info(f"Invalid value of path indicator 'join_path' for {read_file}.")
            error.notify(f"Invalid file path for datafile.", 
                         stage="Joining", file=read_file)
            return False
        logger.info(f"Running file_manager.Archivist.reader for {read_file}")
        
        if is_json:
            try:
                with open(read_file, "r", encoding="utf-8") as f:
                    logger.info(f"Archivist.reader json: {read_file} loaded")
                    return json.load(f)
            except FileNotFoundError:
                if allow_missing:
                    logger.exception(f"No file to read: {read_file}. Exception allowed.")
                    return None
                else:
                    logger.exception(f"Failed to read file {read_file}.")
                    error.notify(f"Failed to read file.", 
                                 stage="Reading", file=read_file)
                    return False
            except json.JSONDecodeError:
                if allow_empty:
                    logger.exception(f"Empty datafile: {read_file}. Exception allowed.")
                    return None
                else:
                    logger.exception(f"File {read_file} could not be decoded as JSON.")
                    error.notify(f"File content not be interpreted.", 
                                 stage="Reading", file=read_file)
                    return False
            except Exception:
                logger.exception(f"Archivist.reader failed to read json: {read_file}.")
                error.notify(f"Failed to read file.", 
                             stage="Reading", file=read_file)
                return False
        else:
            try:
                with open(read_file, "r", encoding="utf-8") as f:
                    logger.info(f"Archivist.reader: {read_file} loaded")
                    return f.read()
            except FileNotFoundError:
                if allow_missing:
                    logger.exception(f"No file to read: {read_file}. Exception allowed.")
                    error.notify(f"No file to read.", 
                                 stage="Reading", file=read_file)
                    return None
            except Exception:
                logger.exception(f"Failed to read file {read_file}.")
                error.notify(f"Failed to read file.", 
                             stage="Reading", file=read_file)
                return False


    def backup(self, backup_frequency: list[int], 
               object_type: str, other_file: str | None = None) -> bool:
        """
        Automated backup in multiple files.
        - performes backup at listed intervals
        - checks irregularities
            - save backup info and call for user review

        Args:
            backup_frequency (list):
                any number of save intervals between backups, 
                in order [seldom, mid, often]
            other_file (str):
                path/filename for non-self.file backup

        Returns:
            (bool):
                succes check
        """

        if not other_file:
            file = self.file 
        else:
            file = os.path.join(self.data_directory, other_file)
        logger.info(f"Running file_manager.Archivist.backup for {file}")
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
        edit_meta[file] = file_edit_count + 1
        self.writer(edit_meta, other_file=meta_file)

        # Diagnostic values - uncomment to redirect backup and file
        # backup_file = os.path.join(self.backup_directory, "backuptest_nofile.json")
        # file = os.path.join(self.data_directory, "nofile.json")

        if data == "postpone":
            pass
        elif data:
            file_length = len(data)
        else:
            logger.warning(f"{file} backup stopped - new data is empty.")
            st.session_state["pending_backup"] = True
            if self._catch_backup_data(
                "nodata", 
                data, 
                file, 
                backup_file, 
                object_type
            ):
                if st.session_state["dialog_active"]: st.rerun()
                self.pending_backup()
            return False

        if backup_file and os.path.exists(backup_file):
            backup_length = len(self.reader(backup_file))
        else:
            backup_length = 0

        # Compare contents of backup and current data
        if data == "postpone":
            pass
        elif backup_length > file_length+2:
            logger.warning(f"{file} backup stopped - data too short.")
            if self._catch_backup_data(
                "tooshort", 
                data, 
                file, 
                backup_file, 
                object_type
            ):
                if st.session_state["dialog_active"]: st.rerun()
                self.pending_backup()
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
                  other_file: str | None = None, join_path: str | None = None, 
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
            other_file (str | None):
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


        read_file = self.file if not other_file else other_file

        if join_path == "data":
            read_file = os.path.join(self.data_directory, read_file)
            logger.info(f"Running file_manager.Archivist.join_data for {read_file}")
        elif join_path == "settings":
            read_file = os.path.join(self.settings_directory, read_file)
            logger.info(f"Running file_manager.Archivist.join_data for {read_file}")
        elif join_path is not None:
            logger.warning(f"""Invalid value of path indicator 
                           'join_path' for {read_file}.""")
            error.notify(f"Invalid file path for datafile.", 
                         stage="Joining", file=read_file)
            return False

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
                logger.info(f"Pre-save editing of {name} performed")
            except:
                logger.exception(f"""Replacing '{name}' in {read_file} 
                                 could not be performed.""")
                error.notify(f"Update could not be performed.", 
                             stage="Joining", name=name, file=read_file)

        if for_deletion:
            try:
                data.pop(name)
                logger.info(f"""Archivist.join_data pre-save removal 
                            of {name} performed.""")
            except KeyError:
                logger.exception(f"""Key '{name}' not removed, 
                                 already absent from {read_file}.""")
                error.notify(f"Entry could not be removed, is already absent.", 
                             stage="Joining", name=name, file=read_file)
                return False
            except TypeError:
                error.notify(f"Unable to remove.", 
                             stage="Joining", name=name, file=read_file)
                return False
            
            if len(data) != original_length-1 and not for_editing: 
                logger.exception(f"""Expected a data length decrease 
                                 after removing {name}.""")
                error.notify(f"Expected a data length decrease not detected.", 
                             stage="Joining", name=name, file=read_file)
                return False
            
            if not for_editing:
                return data, f"{name} was removed"
            else:
                name = for_editing

        # Add data to library
        # Case: editing an existing entry in a growing library
        if name in data.keys() and not is_static:
            data.update(new_data)
            action_verification = f"{name} was edited"
        # Abnormal case: a non-growing library has changed length, 
        # without a deletion registered
        elif len(data) != original_length and is_static and not for_deletion: 
            logger.exception(f"Data length altered unexpectedly. Update aborted.")
            error.notify(f"Unexpected difference in library data length.", 
                         stage="Joining", name=name, file=read_file)
            return False
        # Case: add data to a growing library
        else:
            try:
                data.update(new_data)
            except ValueError:
                error.notify(f"Unable to update.", 
                             stage="Joining", name=name, file=read_file)
                return False
            action_verification = f"{name} was added"
        if need_sorting: data = dict(sorted(data.items(), key=lambda item:str(item[0])))

        # Checking data validity depending on previous action. 
        if name not in data.keys():
            error.notify(f"Entry not added. Check database content.", 
                         stage="Joining", name=name, file=read_file)
            return False
        elif len(data) != original_length+1 and not is_static:
            error.notify(f"""Expected data length increase not detected. 
                         Library update aborted.""", 
                         stage="Joining", name=name, file=read_file)
            return False
        else:
            logger.info(f"{name} data joined to {read_file}.")
            return data, action_verification
        

    def writer(self, data: dict, object_type: str | None = None, 
               other_file: str | None = None, join_path: str | None = None):
        """
        Save file as JSON or other textfile.

        Args:
            data (dict):
                path/filename for non-self.file reading.
            object_type (str):
                identifier for datatype
            other_file (str):
                filename for non-self.file usage
            join_path (str):
                file directory for filenames without full path
        
        Returns:
            (bool):
                success verification
        """
        save_file = self.file if not other_file else other_file

        if join_path == "data":
            save_file = os.path.join(self.data_directory, other_file)
            logger.info(f"Running file_manager.Archivist.writer for {save_file}")
        elif join_path == "settings":
            save_file = os.path.join(self.settings_directory, other_file)
            logger.info(f"Running file_manager.Archivist.writer for {save_file}")
        elif join_path is not None:
            logger.warning(f"""Invalid value of pathway indicator 
                           'join_path' for {save_file}.""")
            error.notify(f"Invalid file path for datafile.", 
                         stage="Writing", file=save_file)

        try:
            with open(save_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
                return True
        except json.JSONDecodeError:
            self._dump("Archivist.writer", {
                "data": data,
                "object_type": object_type,
                "self-file": self.file,
                "other_file": other_file,
                "join_path": join_path
            })
            logger.exception(f"Could not decode data to save in {save_file}.")
            error.notify(f"Could not interpret new data for JSON.", 
                         stage="Writing", file=save_file)
            return False
        except Exception as e:
            logger.exception(f"Could not save to {save_file}.")
            error.notify(f"Could not save data.", 
                         stage="Writing", file=save_file)
            return False


    @st.dialog("Automatic backup: data deviation")
    def pending_backup(self):
        """
        Manager for data backup deviations
        - user notified of potential problems
        - review and/or rescue data
        - continue backup and saving new data
        """
        logger.info("Running file_manager.Archivist.pending_backup @st.dialog")

        st.session_state["updated_library"] = False
        catch = st.session_state["pending_backup"]
        confirm_backup = False

        # Preventing overwriting backup data in case of error
        # Case: no data in file
        # Not backing up an empty file 
        if catch["mode"] == "nodata":
            st.markdown(f"""Your data file: `{catch["file"]}` is empty, 
                        no backup was performed.""")
            st.markdown("""**If this is not a fresh library:** 
                        please check your files!""")
        # Case: new data is shorter than backup
        # User must confirm
        elif catch["mode"] == "tooshort":
            confirm_backup = True
            st.markdown("Backup file contains more objects than the data file.")
            st.markdown("""**If you have not removed data entries:**: 
                        please check your files!""")
        
        # User info
        with st.expander("How to check/rescue your data"):
            filepath = os.path.realpath(catch["file"])
            backup_path = os.path.realpath(self.backup_directory)
            st.markdown(f"Your data file: `{filepath}`")
            st.markdown(f"Your backups: `{backup_path}`")
            st.markdown(f"""Check the latest changed backup file, open in Notepad.  
                        If data is missing in {catch["file"]}, 
                        replace the file or its content with your backup.  
                        If readable, review your recent data below. 
                        """)
        # User review
        with st.expander("Review data"):
            try:
                with st.container(border=False, width="stretch", height=300):
                    st.json(catch["data"], width="stretch")
            except:
                print("Data could not be reviewed.")

        # User action selection
        confirm = self._confirm_action()
        if confirm:
            # If verified and there is data to backup -> backup
            data_details = st.session_state["pending_save"]
            if catch["backup_file"] and confirm_backup:
                shutil.copy(catch["file"], catch["backup_file"])
                print("Data backup done.")

            # Continue with joining/updating data for writing
            if catch["datatype"] in [self.terms["main"], self.terms["secondary"]]:
                st.session_state["updated_library"], action_verification = self.join_data(
                data_details["new_data"], 
                data_details["name"], 
                data_details["for_deletion"], 
                data_details["for_renaming"], 
                data_details["save_file"], 
                data_details["path"], 
                data_details["need_sorting"], 
                data_details["is_static"])
            elif catch["datatype"] == self.terms["progress"]:
                st.session_state["updated_library"] = data_details["new_data"]
                action_verification = "progress added"
            elif catch["datatype"] == "options":
                st.session_state["updated_library"] = data_details["new_data"]
                action_verification = "options edited"

            # If library properly updated:
            # - Send data for writing
            # - Reset Backup values
            # - Rerun Streamlit 
            if st.session_state["updated_library"]:
                self.writer(
                    st.session_state["updated_library"], 
                    other_file=data_details["save_file"], 
                    join_path=data_details["path"]
                )
                print(f"\nLibrary updated, {action_verification}!\n")
                st.session_state["pending_backup"] = False
                st.session_state["pending_save"] = False
                st.session_state["updated_library"] = False
                st.rerun()
        # Abort if denied, reset backup
        elif confirm is False:
            st.session_state["pending_backup"] = False
            st.session_state["pending_save"] = False
            st.rerun()

 
    def catch_data(self, 
                   new_data: any, 
                   save_file: str, 
                   object_type: str, 
                   name: str | None = None, 
                   for_deletion: bool = False, 
                   for_renaming: bool = False, 
                   join_path: str | None = "data", 
                   need_sorting: bool = False, 
                   is_static: bool = False, 
                   stage: str = "unknown_stage", 
                   prefix: str = "data"):
        """
        Pre-emptive securing data in case of errors
            - collects potential file and save settings for later pick-up
            - sends info for dump

        Args:
            data (any):
                information to be saved
            save_file (str):
                filename of save file
            object_type (str):
                identifier for datatype
            name (str | None):
                key for new data
            for_deletion (bool):
                check for data joining
            for_renaming (bool):
                check for data joining
            join_path (str):
                for path not included in save file name 
            need_sorting (bool):
                check for data joining
            is_static (bool):
                check for data joining
            stage (str):
                identifier for data securing stage
            prefix (str):
                prefix of dump-file
        """
        logger.info(f"Running file_manager.Archivist.catch_data for {save_file}")
        st.session_state["pending_save"] = {
            "name": name,
            "new_data": new_data,
            "for_deletion": for_deletion,
            "for_renaming": for_renaming,
            "save_file": save_file,
            "path": join_path,
            "need_sorting": need_sorting,
            "is_static": is_static,
            "object_type": object_type
        }
        self._dump(stage, st.session_state["pending_save"], prefix=prefix)


    def _catch_backup_data(self, mode: str, data: any, 
                           file: str, backup_file: str, object_type: str):
        """
        Collect info and data during irregularities

        Args:
            mode (str):
                mode of irregularity response
            data (str):
                collected data for backup
            file (str):
                file for backup
            backup_file (str):
                current backup file intended to be updated
            object_type (str):
                identifier och datatype
        """
        logger.info("Running file_manager.Archivist._catch_backup_data")
        st.session_state["pending_backup"] = {
            "mode": mode,
            "data": data,
            "file": file,
            "backup_file": backup_file,
            "datatype": object_type
        }
        self._dump(
            "backup", 
            st.session_state["pending_backup"], 
            prefix="backupcatch")

        return True


    def _confirm_action(self):
        """
        User Yes/No request
        Returns:
            (bool):
                True/False depending on button interaction
        """
        st.markdown("Do you wish to proceed?")
        st.space("xsmall")
        col_left, col_right = st.columns(2)
        if col_left.button("Yes", type="secondary", width="stretch"):
            return True
        if col_right.button("No", type="secondary", width="stretch"):
            return False
    

    def _dump(self, stage: str, details: dict, prefix: str = "data"):
        """
        Create temporary dump file before sensitive actions
        - logs info in dump file and logger

        Args:
            stage (str):
                system stage calling _dump
            details (dict):
                any valuable info
            prefix (str):
                file prefix
        """
        content = f"{stage}\n\n"
        for x in details.keys():
            content += f"Logged {x}:\n{details[x]} \n\n"
        dumpfile = os.path.join(self.backup_directory, f"{prefix}_dump.txt")

        try:
            with open(dumpfile, "w", encoding="utf-8") as f:
                f.write(content)
                logger.info(f"Created dump during {stage} at {dumpfile}")
                print(f"Datadump created.")
        except:
            logger.exception(f"Creating dump during {stage} at {dumpfile} failed.")
            print("Could not dump data.")


