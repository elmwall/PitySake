"""
Tools for data management during errors
- catch data before critical stages and dump as file or keep in session state
- dialog backup feature for data review and confirm/deny backup
"""

import datetime
import logging
import shutil
import os
import secrets

import streamlit as st


logger = logging.getLogger(__name__)


def message(message: str|None = None, stage: str|None = None, name: str|None = None, 
            file: str|None = None, details: list|str|None = None, id: str|None = None):
    """
    Called upon detected error or exception, 
    sends information to session state to trigger notification.

    Args:
        message (str|None):
            short error message title
        stage (str|None):
            when did the error occur
        name (str|None):
            name of object the error relates to
        file (str|None):
            file for processing related to the error
        details (list|str|None):
            additional and more detailed information 
            which accumulates in case of multiple errors
        id (str|None):
            for location of error in log file
    """
    
    if not id:
        id = f"{datetime.datetime.now().strftime("%H%M")}-{secrets.token_hex(2)}"
    logger.warning(f"""Error {id}: {message}
stage: {stage}
file: {file}
object name: {name}
details: {details}""")
    
    error = st.session_state.get("error", {})
    if error: 
        info = error.get("info_list", [])
        if isinstance(info, list) and info: 
            for x in info:
                if x not in details: details.append(x)
            
    st.session_state["error"] = {
        "message": message,
        "stage": stage,
        "name": name,
        "file": file,
        "info_list": details,
        "ID": id
    }


def notify():
    """
    User notification of error. 
    Generates a field at dedicated place in UI with details and expandable field.
    """
    error = st.session_state.get("error", None)
    info = str()
    if error:
        if error.get("stage", None): info += f"Stage: {error["stage"]}  \n"
        if error.get("name", None): info += f"Name: {error["name"]}  \n"
        if error.get("file", None): info += f"File: {error["file"]}  \n"

        col_1, col_2, col_4 = st.columns([3, 6, 1])
        # with col_1.container(border=False, width="stretch"):
        with col_2.expander(f"Details - Error ID {error["ID"]}"):
            st.markdown(info)
            if error.get("info_list", None):
                if not isinstance(error["info_list"], list): 
                    st.markdown(error["info_list"])
                else:
                    st.divider()
                    st.markdown("All detected issues:")
                    for x in error["info_list"]:
                        st.markdown(f"- {x}")
        message = error.get("message", "An unknown error occurred, check log.")
        if col_1.button(f":red[{message}]", width="stretch"):
            file = os.path.abspath(__file__)
            directory = os.path.dirname(
                os.path.dirname(file)
            )
            col_2.markdown(f"Location: {directory}", text_alignment="center")

        if col_4.button("Ok", width="stretch"): 
            st.session_state["error"] = False
            st.rerun()


def data_check(name_1: str, collection_1: list|dict, file_1: str, 
               name_2: str, collection_2: list|dict, file_2: str, stage: str|None = None):
    """
    Checks 
    - that data content returns value 
    - compares lists that they contain same values, for data stored in different files
    - triggers error notification if conditions not fulfilled

    Args:
        name_x (str):
            name of data
        collection_x (list|dict):
            data
        file_x (str): 
            name of file origin for data
        stage (str|None):
            when the check was performed
    """
    error = False
    msg = ""
    file = None
    if not collection_1:
        error = True
        msg = f"Empty {name_1} data"
        file = file_1
    elif not collection_2:
        error = True
        msg = f"Empty {name_2} data"
        file = file_2
    else:
        error, msg, file, details = _loop_collections(
           name_checked=name_2, collection_origin=collection_1, 
           collection_checked=collection_2, file_checked=file_2)
        if not error:
            error, msg, file, details = _loop_collections(
                name_checked=name_1, collection_origin=collection_2, 
                collection_checked=collection_1, file_checked=file_1)
        if error:
            details.append("Re-add missing options in *Edit options*")

    if error and not st.session_state["error"]:
        message(message=msg, stage=stage, file=file, details=details)
    return False if error else True

def _loop_collections(name_checked: str, collection_origin: list, 
                      collection_checked: list, file_checked: str):
    "Compares content of one list against another, stores missing values in list."
    error = False
    msg = ""
    file = None
    if isinstance(collection_origin, list):
        details = list()
        for x in collection_origin:
            if x not in collection_checked:
                error = True
                msg = f"Missing {name_checked} data."
                file = file_checked
                details.append(f"Missing option: {x}")
    return error, msg, file, details


@st.dialog("Automatic backup: data deviation")
def pending_backup(arciv):
    """
    Manager for data backup deviations
    - user notified of potential problems
    - review and/or rescue data
    - continue backup and saving new data

    Args:
        arciv (Archivist):
            instance of file manager class
    """
    from app.initialize import arciv, DIRECTORIES, TERMS

    logger.info("Opened dialog")
    backup_directory = DIRECTORIES["BackupFolder"]

    updated_library = False
    catch = st.session_state["pending_backup"]
    confirm_backup = False

    mode = catch.get("mode", None)
    file = catch.get("file", None)
    if not file:
        msg = "Tried and failed to catch backup data."
        details = [f"Backup interrupted for unknown file", 
                   f"Backup interruption reason: {mode}"]
        logger.error(details)
        if not "error" in st.session_state:
            notify.message(
                message=msg, stage="Project configuration", 
                file=f"settings\\config.json", details=details)
        return
            
    datatype = catch.get("datatype", "unknown")
    if not datatype:
        msg = "Catch backup was requested without valid datatype."
        details = [f"Backup interrupted but without datatype it can't be forwarded to writer", 
                   f"Backup interruption reason: {mode}"]
        logger.error(details)
        if not "error" in st.session_state:
            notify.message(
                message=msg, stage="Project configuration", 
                file=f"settings\\config.json", details=details)

    backup_file = catch.get("backup_file", "unknown")
    if not backup_file: logger.warning("Catch backup requested without backup file.")
    
    # Preventing overwriting backup data in case of error
    # Case: no data in file
    # Not backing up an empty file 
    if mode == "nodata":
        st.markdown(f"""Your data file: `{file}` is empty, 
                    no backup was performed.""")
        st.markdown("""**If this is not a fresh library:** 
                    please check your files!""")
    # Case: new data is shorter than backup
    # User must confirm
    elif mode == "tooshort":
        confirm_backup = True
        st.markdown("Backup file contains more objects than the data file.")
        st.markdown("""**If you have not removed data entries:** 
                    please check your files!""")
    else:
        confirm_backup = True
        st.markdown("An unexpected state occurred during backup.")
        st.markdown("Check your files.")

    
    # User info
    with st.expander("How to check/rescue your data"):
        filepath = os.path.realpath(file)
        backup_path = os.path.realpath(backup_directory)
        st.markdown(f"Your data file: `{filepath}`")
        st.markdown(f"Your backups: `{backup_path}`")
        st.markdown(f"""Check the latest changed backup file, open in Notepad.  
                    If data is missing in {file}, 
                    replace the file or its content with your backup.  
                    If readable, review your recent data below. 
                    """)
    # User review
    data = catch.get("data", None)
    with st.expander("Review data"):
        try:
            with st.container(border=False, width="stretch", height=300):
                st.json(data, width="stretch")
        except:
            st.markdown("Data could not be reviewed.")
            logger.exception(f"Backup data could not be reviewed for: \n{data}.")

    # User action selection
    confirm = _confirm_action()
    if confirm:
        # If verified and there is data to backup -> backup
        data_details = st.session_state["pending_save"]
        validated_details = dict()
        if backup_file and confirm_backup:
            shutil.copy(file, backup_file)

        updated_library = False
        # Continue with joining/updating data for writing
        if datatype in [TERMS["main"], TERMS["secondary"]]:
            valid = True
            for x in ["new_data", "name", "for_deletion", "for_renaming", 
                      "save_file", "path", "need_sorting", "is_static"]:
                info = data_details.get(x, "invalid")
                if info == "invalid":
                    updated_library = False
                    valid = False
                    break
                validated_details[x] = info
            # Verify data health
            if valid:
                updated_library = arciv.join_data(
                    validated_details["new_data"], 
                    validated_details["name"], 
                    validated_details["for_deletion"], 
                    validated_details["for_renaming"], 
                    validated_details["save_file"], 
                    validated_details["path"], 
                    validated_details["need_sorting"], 
                    validated_details["is_static"])
        elif datatype in [TERMS["progress"], "options"]:
            info = data_details.get("new_data", "invalid")
            if info == "invalid":
                updated_library = False
            else:
                updated_library = validated_details["new_data"]

        
        # If library properly updated:
        # - Send data for writing
        # - Reset Backup values
        # - Rerun Streamlit 
        if updated_library:
            arciv.writer(
                updated_library, 
                set_file=data_details["save_file"], 
                join_path=data_details["path"]
            )
            st.session_state["pending_backup"] = False
            st.session_state["pending_save"] = False
            st.rerun()
    # Abort if denied, reset backup
    elif confirm is False:
        st.session_state["pending_backup"] = False
        st.session_state["pending_save"] = False
        st.rerun()


def catch_data( 
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
    """
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
    logger.info(f"Caught data for {save_file}")
    dump(stage, st.session_state["pending_save"], prefix=prefix)


def catch_backup_data(mode: str, data: any, file: str, 
                       backup_file: str, object_type: str):
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
    dump("backup", st.session_state["pending_backup"], prefix="backupcatch")
    logger.info(f"Caught backup for {file}")

    return True

# pending_backup ->
def _confirm_action():
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


def dump(stage: str, details: dict, prefix: str = "data"):
    """
    Create temporary dump file before sensitive actions
    - logs info in dump file and logger

    Args:
        stage (str):
            system stage calling dump
        details (dict):
            any valuable info
        prefix (str):
            file prefix
    """
    from app.initialize import DIRECTORIES
    backup_directory = DIRECTORIES["BackupFolder"]
    content = f"{stage}\n\n"
    for x in details.keys():
        content += f"Logged {x}:\n{details[x]} \n\n"
    dumpfile = os.path.join(backup_directory, f"{prefix}_dump.txt")

    try:
        with open(dumpfile, "w", encoding="utf-8") as f:
            f.write(content)
            logger.info(f"Dump created during {stage} at {dumpfile}")
    except:
        logger.exception(f"Creating dump during {stage} at {dumpfile} failed.")