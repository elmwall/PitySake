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
from app.project_configuration import initialize_constants
# To avoid circular dependencies, arciv and constants must be defined before other processes.
# file_manager and project_configuration: only import from initialize when needed.
logger = logging.getLogger(__name__)
logger.info("Loading initialize")
project_info = initialize_constants(st.session_state["project"])
DATAPATH = project_info[0]
DIRECTORIES = project_info[1]
SETTINGS = project_info[2]
TERMS = project_info[3]
arciv = Archivist(DIRECTORIES, DATAPATH, "nofile")
import app.data_access as hold
import app.error_handler as error


# meta = st.session_state["meta"] = arciv.reader("meta.json")
# Keys requiring initial values or simply existing
INIT_STATE = {
    # Main
    # "error": False,
    "pending_backup": False,
    "pending_save": False,
    # Constructor
    "show_theme_settings": False,
    "theme_edited": 0,
    "theme_missing": False,
    # Calculate progress
    "sets": None,
    "start_section": 1, 
    "start_position": 1,
    "stop_section": 1, 
    "stop_position": 2, 
    "start_at_1": False,
    "message": "",
    "calculation": None,
    "calc_mode": False,
    "position_range": None,
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
    "date_helptext": "",
    # Object info manager - edit options
    "changed_options": None,
    "changed_progress": None,
    "edit_options_complete": True,
    "new_option": None,
    "new_state": None,
    "new_limit": None,
    "progress_is_changed": None,
    "options_are_edited": True,
    "reset_edits": False,
    "field_changed": False,
    # Style
    "active_theme": "state_import",
    "active_theme_temp": "state_import",
    "leave_theme_open": False,
    "theme_edited": 0,
    "theme_missing": False,
    # Progress tracker
    "active_trackers": "state_import",
    "value_trackers": "state_import",
    # Data viewer tables
    "main_data_select_view": "main_history",
    "secondary_data_select_view": "secondary_history",
    # General
    "initiated": False,
    "valid_symbols": (
        "-", " ", "_", "–", "—", "'", '"', "&", ".", "*", "!", "?", "%", "§", 
        "(", ")", "[", "]", "{", "}", "/", "+", "<", ">", "@", "#", "=")
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
    if "error" not in st.session_state:
        st.session_state["error"] = False
    if "meta" not in st.session_state:
        meta = st.session_state["meta"] = arciv.reader("meta.json")
    else:
        meta = st.session_state["meta"]
    st.session_state["vertical_view"] = meta["vertical_view"]

    # Cache databases and collect the needed 
    options = hold.load_options()
    progress_data = hold.load_progress_data()
    main_database = hold.load_main_database()
    # Store theme collection
    if "themes" not in st.session_state:
        themes = st.session_state["themes"] = hold.load_themes()
    else:
        themes = st.session_state["themes"]
    active_theme = themes["active"]

    # Special case: define values from external sources 
    # For source and progress values, import value for first source in list
    attempt = 0
    active_trackers = dict()
    value_trackers = dict()
    states, limit = [False]*2
    limit_disabled, state_disabled = [True]*2
    source = None
    if options and progress_data:
        source_limit = options.get("source_limit", {})
        source_options = list(source_limit.keys())
        progress_options = list(progress_data.keys())
        files_match = error.data_check(
            name_1="options", collection_1=source_options, 
            file_1=f"{DIRECTORIES["SettingsFolder"]}\\{SETTINGS["Options"]}",
            name_2="progress", collection_2=progress_options,
            file_2=f"{DIRECTORIES["DataFolder"]}\\{DATAPATH["progress"]}",
            stage="Initialize: data check")
        states = options["results"][0]
        if files_match:
            source = source_options[0]
            limit_disabled = source_limit[source_options[0]] is False
            state_disabled = options["states"][source_options[0]] is False
            limit = source_limit[source_options[0]]
            attempt = progress_data[source_options[0]][TERMS["attempt"]]
        n = 0
        for x in progress_options:
            if progress_data[x]["active"]: 
                active_trackers[x] = n
                if progress_data[x][TERMS["attempt"]] is not None:
                    value_trackers[x] = n
                n += 1

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
        "active_theme": active_theme,
        "active_theme_temp": active_theme,
        # Progress tracker
        "active_trackers": active_trackers,
        "value_trackers": value_trackers}
    
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
                error.message("Could not initialize key.", "Initialize session states", 
                                name=key, file=None, details=[
                                    f"Imported: {state == "state_import"}"])
                logger.exception(f"\ninitialize could not initialize key: {key}")
    
    # Initialize theme setting keys
    if active_theme != "placeholder":
        for key in themes[active_theme].keys():
            if key not in st.session_state:
                st.session_state[key] = themes[active_theme][key]
                st.session_state[f"{key}_temp"] = themes[active_theme][key]
    else:
        _load_placeholder_theme(active_theme)
    
    # Correct view settings dependent on last project active
    # Settings in .strealit/config.toml (currently only themes) requires this check
    logger.info(f"""
Last session project: {meta["project"]}
Current session project: {st.session_state["project"]}
Last session theme: {meta["theme"]}
Current session theme: {active_theme}""")
    # Themes are stored as Theme 1, Theme 2 etc, which themselves may differ
    # between projects, therefore check both project and set theme.
    project_nomatch = meta["project"] != st.session_state["project"]
    theme_nomatch = meta["theme"] != active_theme
    if project_nomatch or theme_nomatch:
        if themes and active_theme and not st.session_state["theme_missing"]: 
            _settings_correction(themes[active_theme], meta)
        else: 
            _settings_correction(themes[active_theme], meta, missing=True)
    else:
        _settings_correction(themes[active_theme], meta, missing=True)
        
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
    database_list = ["load_options", "load_themes", "load_progress_data",
                    "load_main_database", "load_secondary_database"]
    try:
        done = True
        problematic = set()
        # Call data_acces for all databases
        for database in [
                hold.load_options(),
                hold.load_themes(),
                hold.load_main_database(),
                hold.load_secondary_database(),
                hold.load_progress_data()]:
            logger.info(f"Fetching database {n}: {database_list[n]}")
            if not database and not isinstance(database, dict):
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
            error.message("Failed to read database(s).", "Fetching databases", 
                            name=None, file=None, details=problematic)
    except Exception:
        logger.exception(f"\nFailed to collect database at stage: {database_list[n]}")
        error.message("Failed to collect database.", "Fetching databases", 
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


def _settings_correction(active_theme_settings: dict, meta: dict, missing: bool = False):
    """
    Adjusts config file settings to match project settings.

    Args:
        active_theme_settings (dict)
            contains color codes and settings for active theme
        meta (dict)
            information about last session, for update
        missing (bool)
            regulator for missing theme settings
    """

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
    if theme_updated and not missing:
        meta["project"] = st.session_state["project"]
        meta["theme"] = st.session_state["active_theme"]
        arciv.writer(meta, set_file="meta.json")
        logger.info("Theme corrected")


def set_orientation():
    "Store current orientation to be maintain upon reload."
    meta = st.session_state["meta"]
    meta["vertical_view"] = st.session_state["vertical_view"]
    arciv.writer(meta, set_file="meta.json")


def _load_placeholder_theme(active_theme: str):
    "In case of missing theme file, these settings are used to create a functional theme."
    for key in ["background", "highlight_text"]:
        if key not in st.session_state:
            st.session_state[key] = "#000000"
            st.session_state["themes"][active_theme][key] = "#000000"
            st.session_state[f"{key}_temp"] = "#000000"
            st.session_state["themes"][active_theme][f"{key}_temp"] = "#000000"
        if "highlights" not in st.session_state: 
            _load_color("main_container", active_theme, "#333333")
            _load_color("main_gradient", active_theme, "#1D1D1D")
            _load_color("sub_container", active_theme, "#2B2B2B")
            _load_color("small_widget", active_theme, "#313131")
            _load_color("highlights", active_theme, "#ffa600")
            _load_color("positive_color", active_theme, "#00ff00")
            _load_color("negative_color", active_theme, "#ff0000")
            _load_color("neutral_color", active_theme, "#adadad")
            _load_color("input_field", active_theme, "#adadad")
            _load_color("text_color", active_theme, "#ffffff")
            _load_color("header_switch", active_theme, True)

def _load_color(key: str, active_theme: str, color: str):
    "Sync theme settings with session state."
    st.session_state[key] = st.session_state[f"{key}_temp"] = color
    st.session_state["themes"][active_theme][key] = color
