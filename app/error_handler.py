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


def message(message=None, stage=None, name=None, 
            file=None, details=None, id=None):
    
    id = f"{datetime.datetime.now().strftime("%H%M")}-{secrets.token_hex(2)}"
    logger.warning(f"""Error {id}: {message}
stage: {stage}
file: {file}
object name: {name}
details: {details}""")

    st.session_state["error"] = {
        "message": message,
        "stage": f"Archivist: {stage}",
        "name": name,
        "file": file,
        "info_list": details,
        "ID": id
    }


def notify():
    """
    User notification of error.
    """
    error = st.session_state["error"]
    info = str()
    if error:
        if error["stage"]: info += f"Stage: {error["stage"]}:  \n"
        if error["name"]: info += f"Name: {error["name"]}  \n"
        if error["file"]: info += f"File: {error["file"]}  \n"
        if error["info_list"]:
            for x in error["info_list"]:
                info += f"- {x}  "

        col_1, col_2, col_4 = st.columns([3, 6, 1])
        # with col_1.container(border=False, width="stretch"):
        with col_2.expander(f"Details - Error ID {error["ID"]}"):
            st.markdown(info)
        if col_1.button(f":red[{error["message"]}]", width="stretch"):
            file = os.path.abspath(__file__)
            directory = os.path.dirname(
                os.path.dirname(file)
            )
            col_2.markdown(f"Location: {directory}", text_alignment="center")

        if col_4.button("Ok", width="stretch"): 
            st.session_state["error"] = False
            st.rerun()


@st.dialog("Automatic backup: data deviation")
def pending_backup(arciv):
    """
    Manager for data backup deviations
    - user notified of potential problems
    - review and/or rescue data
    - continue backup and saving new data
    """
    from app.file_manager import Archivist

    logger.info("Opened dialog")
    DATAPATH = st.session_state["DATAPATH"]
    DIRECTORIES = st.session_state["DIRECTORIES"]
    TERMS = st.session_state["TERMS"]
    backup_directory = DIRECTORIES["BackupFolder"]
    arciv = Archivist(DIRECTORIES, DATAPATH, "nofile")

    updated_library = False
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
        backup_path = os.path.realpath(backup_directory)
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
            st.markdown("Data could not be reviewed.")
            logger.exception(f"Backup data could not be reviewed for {catch["data"]}.")

    # User action selection
    confirm = _confirm_action()
    if confirm:
        # If verified and there is data to backup -> backup
        data_details = st.session_state["pending_save"]
        if catch["backup_file"] and confirm_backup:
            shutil.copy(catch["file"], catch["backup_file"])

        # Continue with joining/updating data for writing
        if catch["datatype"] in [TERMS["main"], TERMS["secondary"]]:
            updated_library = arciv.join_data(
            data_details["new_data"], 
            data_details["name"], 
            data_details["for_deletion"], 
            data_details["for_renaming"], 
            data_details["save_file"], 
            data_details["path"], 
            data_details["need_sorting"], 
            data_details["is_static"])
        elif catch["datatype"] == TERMS["progress"]:
            updated_library = data_details["new_data"]
        elif catch["datatype"] == "options":
            updated_library = data_details["new_data"]

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
    DIRECTORIES = st.session_state["DIRECTORIES"]
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