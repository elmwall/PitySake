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
    # Constructor
    "show_theme_settings": False,
    "theme_edited": 0,
    "theme_missing": False,
    # Calculate progress
    "curr_page": 1, 
    "curr_row": 0, 
    "prev_page": 1, 
    "prev_row": 2,
    "message": "",
    "calculation": None,
    "rows": 5,
    # Database
    "current_database": "state_import",
    # Object info manager - main
    "include_event": True,
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
    "initiated": False,
    # Data viewer tables
    "main_data_select_view": "main_history",
    "secondary_data_select_view": "secondary_history"
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
    options = hold.load_options()
    progress_data = hold.load_progress_data()
    main_database = hold.load_main_database()
    # Store theme collection
    if "themes" not in st.session_state:
        st.session_state["themes"] = hold.load_themes()
    themes = st.session_state["themes"]

    # Special case: define values from external sources 
    # For source and progress values, import value for first source in list
    attempt = 0
    if len(options) > 0:
        source_options = options["source"]
        states = options["results"][0]
        source = list(options["source_limit"].keys())[0]
        limit_disabled = options["source_limit"][source_options[0]] is False
        state_disabled = options["states"][source_options[0]] is False
        limit = options["source_limit"][source_options[0]]
        if len(progress_data) > 0:
            attempt = progress_data[source_options[0]][TERMS["attempt"]]
    else:
        states, limit = [False]*2
        limit_disabled, state_disabled = [True]*2
        source = None
    if len(themes) > 0:
        active = themes["active"]
    else:
        active = None
    state_import = {
        # Database
        "current_database": copy.deepcopy(main_database),
        # Object info manager - main
        "reg_object_type": TERMS["main"],
        # Collect data from first value among items as inital option
        "reg_state": states,
        "reg_source": source,
        "limit_disabled": limit_disabled,
        "state_disabled": state_disabled,
        "reg_type": TERMS["main"],
        "reg_attempt": attempt,
        "selection_limit": limit,
        # Style
        "active_theme": active,
        "active_theme_temp": active}
    
    # Initiate all keys
    init_state = copy.deepcopy(INIT_STATE)
    for key, state in init_state.items():
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
                error.message("Could not initialize key.", "Initialize: initialize", 
                                name=key, file=None, details=None)
                logger.exception(f"\ninitialize could not initialize key: {key}")
    
    # Initialize theme setting keys
    if st.session_state["active_theme"]:
        for key in themes[st.session_state["active_theme"]].keys():
            if key not in st.session_state:
                st.session_state[key] = themes[st.session_state["active_theme"]][key]
    
    # Correct view settings dependent on last project active
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
        if len(themes) > 0: 
            _settings_correction(themes[active_theme], meta)
        else: 
            st.session_state["theme_missing"] = True
    st.session_state["vertical_view"] = meta["vertical_view"]
        
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
            logger.info(f"Fetching database {n}: {database_list[n]}")
            if not database and type(database) is not dict:
                done = False
                problematic.add(database_list[n])
                logger.warning(f"\nFailed to read database {n}: {database_list[n]}")
            else:
                logger.info(f"Collected database {n}: {database_list[n]}")
            n += 1
        # Reset control values if all fine
        if done: 
            st.session_state["cleared_cache"] = False
            st.session_state["rerun"] = 0
            st.rerun()
        else:
            logger.exception(f"\nFailed to read database(s): {problematic}")
            error.message("Failed to read database(s).", "Initialize: fetch", 
                            name=None, file=None, details=problematic)
    except Exception:
        logger.exception(f"\nFailed to collect database at stage: {database_list[n]}")
        error.message("Failed to collect database.", "Initialize: fetch", 
                        name=database_list[n], file=None, details=None)


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
    hold.process_main_db.clear()
    hold.process_secondary_db.clear()
    hold.history_dataframe.clear()
    hold.overview_dataframe.clear()

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
address = "127.0.0.1"

[browser]
gatherUsageStats = false

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
        logger.exception(f"\nError: {e} \nOccurred while attempting to write to config.toml")
    
    if theme_updated:
        meta["project"] = st.session_state["project"]
        meta["theme"] = st.session_state["active_theme"]
        arciv.writer(meta, set_file="meta.json")
        logger.info("Theme corrected")


def set_orientation():
    "Store current orientation to be maintain upon reload."
    meta = st.session_state["meta"]
    meta["vertical_view"] = st.session_state["vertical_view"]
    arciv.writer(meta, set_file="meta.json")