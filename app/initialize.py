"""
Module managing session state keys and directs cache.
"""
import copy
import datetime
import logging

import streamlit as st

from app.file_manager import Archivist
import app.data_access as hold


logger = logging.getLogger(__name__)
logger.info("Loading initialize")


# Keys requiring initial values or simply existing
INIT_STATE = {
    # Main
    "pending_backup": False,
    "pending_save": False,
    # "is_initial_state_1:": True,
    # "state_key_2:": "init",
    "vertical_view": False,
    # Constructor
    "show_theme_settings": False,
    "theme_edited": 0,
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
    "reg_object_type": "state_import",
    "reg_origin": None,
    "reg_source":"state_import",
    "reg_state": "state_import",
    "reg_type": "state_import",
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
    "active_theme": "state_import",
    "active_theme_temp": "state_import",
    "leave_theme_open": False,
    "theme_edited": 0,
    # Progress tracker
    "initiated": False
    # # Loading indicators
    # "loading": "state_import"
}
PRINT_SPACER = 80


def initialize():
    """
    Function initiating and securing correct state of keys and call for cache.
    """

    logger.info("Running initialize.initialize")
    
    # directory = os.path.join(f"{file}/settings")
    # hub = ConfigHub()
    # , "config.json"
    
    DIRECTORIES = st.session_state["DIRECTORIES"]
    DATAPATH = st.session_state["DATAPATH"]
    TERMS = st.session_state["TERMS"]
    
    # Special case: immidiate need for checking previous activity and loading data
    if "cleared_cache" not in st.session_state: st.session_state["cleared_cache"] = False
    if "rerun" not in st.session_state: st.session_state["rerun"] = 0

    arciv = Archivist(DIRECTORIES, DATAPATH, "nofile")
    # Cache databases and collect the needed 
    data_options = hold.load_options()
    attempts = hold.load_progress_data()
    hold.load_main_database(),
    hold.load_secondary_database(),
    # Store theme collection
    if "themes" not in st.session_state:
        st.session_state["themes"] = hold.load_themes()
    themes = st.session_state["themes"]

    # Loading indicators
    if "loading" not in st.session_state:
        st.session_state["loading"] = {
            "reg_details": False
        }

    # Special case: define values from external sources 
    state_import = {
        # Database
        "current_database": copy.deepcopy(hold.load_main_database()),
        # Object info manager - main
        "reg_attempt": attempts[f"{TERMS["main"]} {TERMS["temp"]}"][TERMS["attempt"]],
        "reg_object_type": TERMS["main"],
        "reg_state": data_options["state_alternatives"][0],
        "reg_source": TERMS["temp"],
        "reg_type": TERMS["main"],
        # Style
        "active_theme": themes["active"],
        "active_theme_temp": themes["active"]
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
    for key in themes[st.session_state["active_theme"]].keys():
        if key not in st.session_state:
            st.session_state[key] = themes[st.session_state["active_theme"]][key]
    # Follow up backups from prior activity
    if st.session_state["pending_backup"]: arciv.pending_backup()


def fetch_databases():
    """
    Fetch all working data for cache. 
    Tries for a set number of times in case of a file being written, then aborts.
    """

    logger.info("Running initialize.fetch_databases")

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
            st.rerun()
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

    logger.info("Running initialize.refresh")

    hold.load_options.clear(),
    # hold.load_themes.clear(),
    hold.load_main_database.clear(),
    hold.load_secondary_database.clear(),
    hold.load_progress_data.clear()

    for key in st.session_state.keys():
        del st.session_state[key]

    st.session_state["processed_edits"] = False
    st.session_state["cleared_cache"] = True
    st.rerun()
