"""
Module managing session state keys and directs cache.
"""
import os
import datetime
import copy

import streamlit as st

from app.file_manager import Archivist
import app.data_access as hold
# import app.config_hub as hub
# from settings.config import TERMS, DIRECTORIES, DATAPATH
from app.config_hub import TERMS, DIRECTORIES, SETTINGS, DATAPATH


# Keys requiring initial values or simply existing
INIT_STATE = {
    # Main
    "pending_backup": False,
    "pending_save": False,
    "state_key": "init",
    "vertical_view": False,
    # Calculate progress
    "curr_page": 1, 
    "curr_row": 0, 
    "prev_page": 1, 
    "prev_row": 2,
    "message": "",
    "calculation": None,
    # Database
    "current_database": "state_import",
    # Object info manager - main
    "dialog_active": False,
    "reg_attempt": "state_import",
    "reg_attribute": None,
    "reg_date": datetime.date.today(),
    "reg_name": None,
    "reg_object_type": TERMS["main"],
    "reg_origin": None,
    "reg_source": TERMS["temp"],
    "reg_state": "state_import",
    "reg_type": TERMS["main"],
    "reg_utility": None,
    "values": dict(),
    # Object info manager - edit options
    "changed_options": None,
    "changed_progress": None,
    "edit_options_complete": True,
    "new_option": None,
    "new_state": None,
    "new_limit": None,
    # Style
    "set_theme": "state_import",
    "set_theme_temp": "state_import",
    # Progress tracker
    "initiated": False
}
PRINT_SPACER = 80


def initialize():
    """
    Function initiating and securing correct state of keys and call for cache.
    """
    testfile = os.path.join(DIRECTORIES["SettingsFolder"], SETTINGS["Options"])
    testpath = os.path.abspath(testfile)
    print("testing init path", testpath)
    # st.stop()
    
    # Special case: immidiate need for checking previous activity and loading data
    if "cleared_cache" not in st.session_state: st.session_state["cleared_cache"] = False
    if "rerun" not in st.session_state: st.session_state["rerun"] = 0

    arciv = Archivist(DIRECTORIES, DATAPATH, "nofile")
    # Cache databases and collect the needed 
    fetch_databases()
    data_options = hold.load_options()
    attempts = hold.load_progress_data()
    themes = hold.load_themes()
    # Special case: define values from external sources 
    state_import = {
        "reg_attempt": attempts[f"{TERMS["main"]} {TERMS["temp"]}"][TERMS["attempt"]],
        "reg_state": data_options["state_alternatives"][0],
        "set_theme": themes["active"],
        "set_theme_temp": themes["active"],
        "current_database": copy.deepcopy(hold.load_main_database())
    }

    # Initiate all keys
    for key, state in INIT_STATE.items():
        if key not in st.session_state:
            if state == "state_import":
                st.session_state[key] = state_import[key]
            else:
                st.session_state[key] = state
        # In case of values lost through errors or hickups, verify the state of existing keys
        elif st.session_state[key] is None:
            try:
                if state == "state_import":
                    st.session_state[key] = state_import[key]
                else:
                    st.session_state[key] = state
            except Exception as e:
                print(f"{f"initialize.initialize: initializing {key}":{PRINT_SPACER}} Failed")
    # Initialize theme setting keys
    for key in themes[st.session_state["set_theme"]].keys():
        if key not in st.session_state:
            st.session_state[key] = themes[st.session_state["set_theme"]][key]
    # Follow up backups from prior activity
    if st.session_state["pending_backup"]: arciv.pending_backup()


def fetch_databases():
    """
    Fetch all working data for cache. 
    Tries for a set number of times in case of a file being written, then aborts.
    """
    msg = "First attempt" if st.session_state["rerun"] == 0 else "Retrying"
    print(f"{f"initialize.fetch_database: fetching":{PRINT_SPACER}} {msg}")
    try:
        n = 1
        done = True
        # Call data_acces for all databases
        for database in [
            hold.load_options(),
            hold.load_themes(),
            hold.load_main_database(),
            hold.load_secondary_database(),
            hold.load_progress_data()
        ]:
            print(f"{f"initialize.fetch_database: database {n}":{PRINT_SPACER}} Attempting...")
            if not database:
                done = False
                print(f"{f" ":{PRINT_SPACER}} Failed")
            else:
                print(f"{f" ":{PRINT_SPACER}} Success")
            n += 1
        # Reset control values if all fine
        if done: 
            st.session_state["cleared_cache"] = False
            st.session_state["rerun"] = 0
            print(f"{f" ":{PRINT_SPACER}} Done")
    except Exception:
        # Attempt to fetch againt until limit exceeded
        if st.session_state["rerun"] < 6:
            print(f"{f"initialize.fetch_database: database {n}":{PRINT_SPACER}} Not fetched, retrying.")
            st.session_state["rerun"] += 1
            st.rerun()
        else:
            print(f"{f"initialize.fetch_database: database {n}":{PRINT_SPACER}} Not fetched, quitting.")
            st.error("")


def refresh():
    """
    Clean slate: function clears all databases and removes keys.
    Sets check values for proper initialization.
    """
    hold.load_options.clear(),
    hold.load_themes.clear(),
    hold.load_main_database.clear(),
    hold.load_secondary_database.clear(),
    hold.load_progress_data.clear()

    for key in st.session_state.keys():
        del st.session_state[key]

    st.session_state["processed_edits"] = False
    st.session_state["cleared_cache"] = True
    st.rerun()
