"""
Database collectors

Manages collection and proper storage of databases:
- main object database - cache
- secondary object database - cache
- progress data - cache
- data options - cache
- themes - sessions state
- processes database for table/graph - cache
- generates dataframe for table - cache
"""

import datetime
import logging

import pandas as pd
import streamlit as st

from .file_manager import Archivist


logger = logging.getLogger(__name__)
DATAPATH = st.session_state["DATAPATH"]
DIRECTORIES = st.session_state["DIRECTORIES"]
SETTINGS = st.session_state["SETTINGS"]
TERMS = st.session_state["TERMS"]
arciv = Archivist(DIRECTORIES, DATAPATH, "nofile")


@st.cache_data
def load_main_database() -> dict:
    """
    Loads main database via file_manager, and caches data
    
    Returns:
        (dict):
            main object database
    """
    
    datafile = DATAPATH[TERMS["main"]]
    return arciv.reader(datafile, join_path="data")


@st.cache_data
def load_secondary_database() -> dict:
    """
    Loads secondary database via file_manager, and caches data
    
    Returns:
        (dict):
            secondary object database
    """

    datafile = DATAPATH[TERMS["secondary"]]
    return arciv.reader(datafile, join_path="data")


@st.cache_data
def load_progress_data() -> dict:
    """
    Loads progress data via file_manager, and caches it
    
    Returns:
        (dict):
            progress
    """

    datafile = DATAPATH["progress"]
    return arciv.reader(datafile, join_path="data")


@st.cache_data
def load_options() -> dict:
    """
    Loads project-unique data options, and caches data
    
    Returns:
        (dict):
            data options
    """

    options_file = SETTINGS["Options"]
    
    return arciv.reader(other_file=options_file, join_path="settings")


# For best syncronization after editing theme, 
# these settings are best kept in session state
def load_themes() -> dict:
    """
    Loads theme settings, and stores in session state
    
    Returns:
        (dict):
            themes
    """

    options_file = SETTINGS["Themes"]
    return arciv.reader(other_file=options_file, join_path="settings")


@st.cache_data
def process_collection_db(database:dict, datatype:str):
    """
    Database processing for data view featrues

    Manages processing for data depending on datatype for
    - main object table view and timeline
    - secondary object table view

    Args:
        database (dict):
        datatype (str):
            defines "main" or "secondary" object type

    Returns:
        processed database (dict):
            label count, attempt values, last event value, 
            success/fail count, rows for tables, graph data
    """
    data_options = load_options()
    graph_data = {
        "name": [],
        "date": [],
        "attempt": [],
        "state": []
    }
    
    # For analysis of values
    attempt_value_list = list()
    # To count Category - Label - How many  
    counts = dict()
    # To record last attempt [date, attempt value]
    last_event = [0, 0]
    # To record [successful, failed] attempts
    success_fail = [0, 0]
    # Recording main object type collected
    object_count = dict()
    # Data for pandas/st.dataframe
    rows_for_table = list()         

    # For counting object labels - Define dictionary with category keys and data keys 
    if datatype == "main": 
        for category, options in data_options[TERMS["main"]].items():
            counts[category] = dict()
            for x in options:
                counts[category][x] = 0
    state_value, date, object_collection, name, attempt_value, source, state, index = [None]*8
    for name, info in database.items():

        # Only count labels for main type object
        if datatype == "main": 
            for category, options in counts.items():
                object_option = info[category]
                counts[category][object_option] += 1
        
        # Collect event data
        for event_id, event_data in info[TERMS["event"]].items(): 
            # Collect date and index
            date, index = event_id.split("-")
            # For main type object, date or main field in dataview should may show collection count 
            formatted_date = datetime.datetime.strptime("20" + date, "%Y%m%d").strftime("%Y-%m-%d")
            if datatype == "main":
                if name in object_count:
                    object_count[name] += 1
                else:
                    object_count[name] = 0
                object_collection = f"C{object_count[name]}"
            else:
                object_collection = ""

            # Collect attempt and state
            # For objects without attempts registered, skip both
            attempt_value = event_data[TERMS["attempt"]]
            source = event_data[TERMS["source"]]
            if attempt_value:
                # Collect all attempt results in a list
                attempt_value_list.append(attempt_value)
                # Check date to identify latest value
                if int(date) > last_event[0]:
                    last_event = [int(date), attempt_value]
                # Check event outcome and update list [success, fail] with +1 for success or fail
                state = event_data[TERMS["state"]]
                if state:
                    if state == TERMS["state_win"]:
                        success_fail = [success_fail[0] + 1, success_fail[1]]
                        state_value = True
                    elif state == TERMS["state_loss"]: 
                        success_fail = [success_fail[0], success_fail[1] + 1]
                        state_value = False
                    else:
                        state_value = None
            graph_data["date"].append(formatted_date)
            graph_data["name"].append(name)
            graph_data["state"].append(state_value)
            graph_data["attempt"].append(attempt_value)

        # Create list of row sets for pandas
        rows_for_table.append({
            "Date": date,
            " ": object_collection,
            "Name": name,
            TERMS["attempt"]: attempt_value,
            "source": source,
            TERMS["state"]: state,
            "Index": index
        })

    return {
        "counts": counts,
        "attempt_list": attempt_value_list,
        "last_event": last_event,
        "success_fail": success_fail, 
        "table_data": rows_for_table,
        "graph_data": graph_data
    }


@st.cache_data
def data_to_dataframe(rows:list, object_type:str):
    """
    Database processing for table view

    Manages data processing for:
    - main object
    - secondary object

    Args:
        rows (list):
            list of dictionaries for pandas table view rows
        object_type (str):
            defines "main" or "secondary" object type

    Returns:
        processed pandas dataframe:
            label count, attempt values, last event value, 
            success/fail count, rows for tables, graph data
    """
    
    dataframe = pd.DataFrame(rows)
    # Use index for sorting, then discard
    processed_dataframe = (
        dataframe.sort_values(["Date", "Index"], ascending=False)
        .drop(columns=["Index", f"{TERMS["state"]}"])
    )

    # Collection value disregarded for secondary type
    if object_type == "secondary": 
        processed_dataframe = (processed_dataframe.drop(columns=[" "]))

    processed_dataframe[TERMS["attempt"]] = pd.to_numeric(
        processed_dataframe[TERMS["attempt"]], 
        errors="coerce"
    ).astype("Int64")
    
    return processed_dataframe


                    