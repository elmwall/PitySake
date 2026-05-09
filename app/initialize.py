import datetime

import streamlit as st

from app.file_manager import Archivist
import app.data_access as hold
from settings.config import TERMS, DIRECTORIES, DATAPATH


PRINT_SPACER = 80

INIT_STATE = {
    # Main
    # "cleared_cache": False,
    "pending_backup": False,
    "pending_save": False,
    # "rerun": 0,
    "state_key": "init",
    "vertical_view": False,
    # Calculate progress
    "curr_page": 1, 
    "curr_row": 0, 
    "prev_page": 1, 
    "prev_row": 2,
    "message": "",
    "calculation": None,
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


def initialize():
    if "cleared_cache" not in st.session_state: st.session_state["cleared_cache"] = False
    if "rerun" not in st.session_state: st.session_state["rerun"] = 0

    arciv = Archivist(DIRECTORIES, DATAPATH, "nofile")
    fetch_database()
    data_options = hold.load_options()
    attempts = hold.load_progress_data()
    themes = hold.load_themes()
    state_import = {
        "reg_attempt": attempts[f"{TERMS["main"]} {TERMS["temp"]}"][TERMS["attempt"]],
        "reg_state": data_options["state_alternatives"][0],
        "set_theme": themes["active"],
        "set_theme_temp": themes["active"]
    }
    
    for key, state in INIT_STATE.items():
        if key not in st.session_state:
            if state == "state_import":
                st.session_state[key] = state_import[key]
            else:
                st.session_state[key] = state
        elif st.session_state[key] is None:
            try:
                if state == "state_import":
                    st.session_state[key] = state_import[key]
                else:
                    st.session_state[key] = state
            except Exception as e:
                print(f"{f"initialize.initialize: initializing {key}":{PRINT_SPACER}} Failed")

    for key in themes[st.session_state["set_theme"]].keys():
        if key not in st.session_state:
            st.session_state[key] = themes[st.session_state["set_theme"]][key]
    
    if st.session_state["pending_backup"]: arciv.pending_backup()

    for x, y in INIT_STATE.items():
        print(f"{x:25} {y}")


def fetch_database():
    msg = "First attempt" if st.session_state["rerun"] == 0 else "Retrying"
    print(f"{f"initialize.fetch_database: fetching":{PRINT_SPACER}} {msg}")
    try:
        n = 1
        done = True
        for database in [
            hold.load_options(),
            hold.load_themes(),
            hold.load_main_database(),
            hold.load_utility_database(),
            hold.load_progress_data()
        ]:
            print(f"{f"initialize.fetch_database: database {n}":{PRINT_SPACER}} Attempting...")
            if not database:
                done = False
                print(f"{f" ":{PRINT_SPACER}} Failed")
                raise ValueError("Database not ready")
            else:
                print(f"{f" ":{PRINT_SPACER}} Success")
            n += 1
        if done: 
            print("main", hold.load_main_database().keys())
            print("util", hold.load_utility_database().keys())
            print("prog", hold.load_progress_data().keys())
            print("opt", hold.load_options().keys())
            print("theme", hold.load_themes().keys())
            st.session_state["cleared_cache"] = False
            st.session_state["rerun"] = 0
            print(f"{f" ":{PRINT_SPACER}} Done")
    except Exception:
        if st.session_state["rerun"] < 5:
            print(f"{f"initialize.fetch_database: database {n}":{PRINT_SPACER}} Not fetched, retrying.")
            st.session_state["rerun"] += 1
            st.rerun()
        else:
            print(f"{f"initialize.fetch_database: database {n}":{PRINT_SPACER}} Not fetched, quitting.")
            st.error("")


def refresh():
    hold.load_options.clear(),
    hold.load_themes.clear(),
    hold.load_main_database.clear(),
    hold.load_utility_database.clear(),
    hold.load_progress_data.clear()
    for key in st.session_state.keys():
        del st.session_state[key]
    st.session_state["processed_edits"] = False
    st.session_state["cleared_cache"] = True
    st.rerun()
