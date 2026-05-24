"""
App initialization

Manages:
- Ordered system startup session state initialization
- Directs database and settings cache
- System resets
"""

import copy
import datetime
import logging

import streamlit as st

from app.file_manager import Archivist
import app.data_access as hold
import app.error_handler as error


logger = logging.getLogger(__name__)
logger.info("Loading initialize")
DIRECTORIES = st.session_state["DIRECTORIES"]
DATAPATH = st.session_state["DATAPATH"]
TERMS = st.session_state["TERMS"]
arciv = Archivist(DIRECTORIES, DATAPATH, "nofile")

# Keys requiring initial values or simply existing
INIT_STATE = {
    # Main
    "error": False,
    "pending_backup": False,
    "pending_save": False,
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
    "rows": 5,
    # "page_range": range(10+1),
    # Database
    "current_database": "state_import",
    # Object info manager - main
    "dialog_active": False,
    "limit": 0,
    "regset": "add_new",
    "reg_attempt": "state_import",
    "reg_attribute": None,
    "reg_date": datetime.date.today(),
    "reg_name": None,
    "reg_object_type": "state_import",
    "reg_origin": None,
    "reg_source": "state_import",
    "reg_state": "state_import",
    "reg_type": "state_import",
    "reg_utility": None,
    "translated_values": dict(),
    "selection_limit": "state_import",
    "limit_disabled": "state_import",
    "state_disabled": "state_import",
    # Object info manager - edit options
    "changed_options": None,
    "changed_progress": None,
    "edited_options": list(),
    "edit_options_complete": True,
    "new_option": None,
    "new_state": None,
    "new_limit": None,
    "progress_changed": None,
    # Style
    "active_theme": "state_import",
    "active_theme_temp": "state_import",
    "leave_theme_open": False,
    "theme_edited": 0,
    # Progress tracker
    "initiated": False
}


def initialize():
    """
    Initiating and securing correct state of data at startup
    - initialize session state: list of essential keys
    - initialize session states requiring external info
    - loads data for cache
    - checks meta for last session settings needing correction
    """

    logger.info("Running")
    
    # Special case: immidiate need for checking previous activity and loading data
    if "cleared_cache" not in st.session_state: 
        st.session_state["cleared_cache"] = False
    if "rerun" not in st.session_state: 
        st.session_state["rerun"] = 0

    # Cache databases and collect the needed 
    hold.load_options()
    hold.load_progress_data()
    hold.load_main_database()
    hold.load_secondary_database()
    # Store theme collection
    if "themes" not in st.session_state:
        st.session_state["themes"] = hold.load_themes()
    themes = st.session_state["themes"]

    # Special case: define values from external sources 
    state_import = {
        # Database
        "current_database": copy.deepcopy(hold.load_main_database()),
        # Object info manager - main
        "reg_object_type": TERMS["main"],
        "reg_state": hold.load_options()["results"][0],
        "reg_source": list(hold.load_options()["source_limit"].keys())[0],
        "limit_disabled": hold.load_options()["source_limit"][TERMS["main_source"]] is False,
        "state_disabled": hold.load_options()["states"][TERMS["main_source"]] is False,
        "reg_type": TERMS["main"],
        "reg_attempt": hold.load_progress_data()[TERMS["main_source"]][TERMS["attempt"]],
        "selection_limit": hold.load_options()["source_limit"][TERMS["main_source"]],
        # Style
        "active_theme": themes["active"],
        "active_theme_temp": themes["active"]}

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
                elif state is not None:
                    st.session_state[key] = state
            except Exception as e:
                st.session_state["error"] = {
                    "message": "Could not initialize key.",
                    "stage": "Initialize, initialize",
                    "name": "name",
                    "file": None,
                    "info_list": None
                }
                logger.warning(f"initialize could not initialize key: {key}")
    
    # Initialize theme setting keys
    for key in themes[st.session_state["active_theme"]].keys():
        if key not in st.session_state:
            st.session_state[key] = themes[st.session_state["active_theme"]][key]
    
    # Correct settings dependent on last project active
    # Settings in .strealit/config.toml (currently only themes) requires this check
    meta = st.session_state["meta"]
    active_theme = st.session_state["active_theme"]
    logger.info(f"""
        Last session project: {meta["project"]}
        Current session project: {st.session_state["project"]}
        Last session theme: {meta["theme"]}
        Current session theme: {st.session_state["active_theme"]}""")
    # Themes are stored as Theme 1, Theme 2 etc, which themselves may differ
    # between projects, therefore check both project and set theme.
    project_nomatch = meta["project"] != st.session_state["project"]
    theme_nomatch = meta["theme"] != st.session_state["active_theme"]
    if project_nomatch or theme_nomatch:
        _settings_correction(themes[active_theme], meta)
        
    # Follow up backups from prior activity
    if st.session_state["pending_backup"]: error.pending_backup(arciv)
    

def fetch_databases():
    """
    Initiate all working data
    - loads for cache: object and progress databases, options
    - loads for session state: theme
    - tries for a set number of times, then aborts
    """

    logger.info("Fetching")
    n = 0
    database_list = ["load_options", "load_themes", 
                    "load_main_database", "load_secondary_database", 
                    "load_progress_data"]
    try:
        done = True
        problematic = set()
        # Call data_acces for all databases
        for database in [
            hold.load_options(),
            hold.load_themes(),
            hold.load_main_database(),
            hold.load_secondary_database(),
            hold.load_progress_data()
        ]:
            logger.info("Fetching databases: {n}")
            if not database:
                done = False
                problematic.add(database_list[n])
                logger.warning(f"Failed to read database {n}: {database_list[n]}")
            else:
                logger.info(f"Collected database {n}: {database_list[n]}")
            n += 1
        # Reset control values if all fine
        if done: 
            st.session_state["cleared_cache"] = False
            st.session_state["rerun"] = 0
            st.rerun()
        else:
            logger.info(f"Failed to read database(s): {database_list}")
            st.session_state["error"] = {
                "message": "Failed to read database(s).",
                "stage": "Initialize, fetch",
                "name": None,
                "file": None,
                "info_list": database_list
            }
    except Exception:
        logger.exception(f"Failed to collect database at stage: {database_list[n]}")
        st.session_state["error"] = {
            "message": "Failed to collect database.",
            "stage": "Initialize, fetch",
            "name": {database_list[n]},
            "file": None,
            "info_list": None
        }


def refresh():
    """
    Perform clean slate
    - clears all databases and removes keys
    - sets check values for proper initialization
    """
    logger.info("Refresh requested")

    hold.load_options.clear(),
    hold.load_main_database.clear(),
    hold.load_secondary_database.clear(),
    hold.load_progress_data.clear()

    for key in st.session_state.keys():
        del st.session_state[key]

    st.session_state["processed_edits"] = False
    st.session_state["cleared_cache"] = True
    st.rerun()


def _settings_correction(active_theme_settings, meta):
    "Adjusts config file settings to match project settings."
    config = f"""
[server]
runOnSave = true

[theme]
backgroundColor = '{active_theme_settings["background"]}'
secondaryBackgroundColor = '{active_theme_settings["input_field"]}'
primaryColor = '{active_theme_settings["highlights"]}'
textColor = '{active_theme_settings["text_color"]}'
font = 'sans serif'
"""
    
    theme_updated = False
    # Write new toml
    try:
        with open(".streamlit/config.toml", "w") as f:
            f.write(config.strip())
            theme_updated = True
    except Exception as e:
        logger.exception(f"Error from {e} occurred while attempting to write to config.toml")
    
    if theme_updated:
        meta["project"] = st.session_state["project"]
        meta["theme"] = st.session_state["active_theme"]
        arciv.writer(meta, other_file="meta.json")
        logger.info("Theme corrected")