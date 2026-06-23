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
import statistics 

import pandas as pd
import streamlit as st

from .file_manager import Archivist


DATAPATH = st.session_state["DATAPATH"]
DIRECTORIES = st.session_state["DIRECTORIES"]
SETTINGS = st.session_state["SETTINGS"]
TERMS = st.session_state["TERMS"]
logger = logging.getLogger(__name__)
arciv = Archivist(DIRECTORIES, DATAPATH, "nofile")


def data_loader(datafile, join_path):
    database = arciv.reader(datafile, join_path)
    if database:
        return arciv.reader(datafile, join_path)
    else:
        return {}


@st.cache_data
def load_main_database() -> dict:
    "Loads main database via file_manager, and caches data"
    datafile = DATAPATH[TERMS["main"]]
    return data_loader(datafile, join_path="data")


@st.cache_data
def load_secondary_database() -> dict:
    "Loads secondary database via file_manager, and caches data"
    datafile = DATAPATH[TERMS["secondary"]]
    return data_loader(datafile, join_path="data")


@st.cache_data
def load_progress_data() -> dict:
    "Loads progress data via file_manager, and caches it"
    datafile = DATAPATH["progress"]
    return data_loader(datafile, join_path="data")


@st.cache_data
def load_options() -> dict:
    "Loads project-unique data options, and caches data"
    options_file = SETTINGS["Options"]
    return data_loader(options_file, join_path="settings")


# For best syncronization after editing theme, 
# these settings are best kept in session state
def load_themes() -> dict:
    "Loads theme settings, and stores in session state"
    options_file = SETTINGS["Themes"]
    return data_loader(options_file, join_path="settings")


@st.cache_data
def process_main_db(database):
    "Cache processed database for main type object."
    return _process_collection_db(database, "main")

@st.cache_data
def process_secondary_db(database):
    "Cache processed database for secondary type object."
    return _process_collection_db(database, "secondary")

def _process_collection_db(database: dict, datatype: str):
    """
    Database processing for data view featrues
    - manages processing for data depending on datatype
    - main for table view and timeline, secondary object for table view

    Args:
        database (dict):
            main or secondary database
        datatype (str):
            defines "main" or "secondary" object type

    Returns:
        processed database (dict):
            counts (dict): couts of labels for main type objects  
            attempt_list (list): collected values for analysis  
            last_event (list): last recorded  
            success_fail (list): counts of positive (index 0) and negative (index 1)  
            table_data (list): rows for history table  
            overview_data (list): rows for overview table  
            graph_data (dict): data for timeline  
            attempt_title: term for attempt (value) for view  
    """
    data_options = load_options()
    graph_data = {
        "name": [],
        "date": [],
        "attempt": [],
        "attempt_made": [],
        "state": [],
        "highlight": [],
        "type": []
    }

    # For analysis of values
    attempt_value_list = list()
    # To count labels of main divided into categories
    counts = dict()
    # To record last attempt [date, attempt value]
    last_event = [0, 0]
    # To record [successful, failed] attempts
    success_fail = [0, 0]
    # Recording no of an object collected
    object_count = dict()
    # Data for pandas/st.dataframe
    rows_for_history = list()
    rows_for_overview = list()
    attempt_title = TERMS["attempt"]
    if TERMS["unit"]: 
        attempt_title = f"{TERMS["unit"]} {attempt_title}" 

    if not len(data_options) > 0:
        return {
            "counts": counts,
            "attempt_list": attempt_value_list,
            "last_event": last_event,
            "success_fail": success_fail, 
            "table_data": rows_for_history,
            "overview_data": rows_for_overview,
            "graph_data": graph_data,
            "attempt_title": attempt_title,
            "valid": False}

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
        
        attempt_per_object = list()  
        # Collect event data
        for event_id, event_data in info[TERMS["event"]].items(): 
            # Collect date and index
            date, index = event_id.split("-")
            # For main type object, dataview should show collection count 
            formatted_date = datetime.datetime.strptime("20" + date, "%Y%m%d").strftime("%Y-%m-%d")
            if datatype == "main":
                if name in object_count:
                    object_count[name] += 1
                else:
                    object_count[name] = data_options["value_limits"]["collection_start_count"]
                object_collection = f"{object_count[name]}"
            else:
                object_collection = ""

            # Collect attempt
            attempt_value = event_data[TERMS["attempt"]]
            attempt_per_object.append(attempt_value)
            state = event_data[TERMS["state"]]
            if attempt_value:
                # Collect all attempt results in a list
                attempt_value_list.append(attempt_value)
                # Check date to identify latest value
                if int(date) > last_event[0]:
                    last_event = [int(date), attempt_value]

            # Collect state
            if state == TERMS["state_win"]:
                success_fail = [success_fail[0] + 1, success_fail[1]]
                state_value = True
            elif state == TERMS["state_loss"]: 
                success_fail = [success_fail[0], success_fail[1] + 1]
                state_value = False
            else:
                state_value = None

            # Collect values for graph data
            graph_data["date"].append(formatted_date)
            graph_data["name"].append(name)
            graph_data["state"].append(state_value)
            graph_data["type"].append(datatype)
            # Adapt attempt and highlight values depending on data present
            source = event_data[TERMS["source"]]
            print(data_options)
            if attempt_value is not None:
                graph_data["attempt"].append(attempt_value)
                graph_data["attempt_made"].append(True)

                high_threshold = data_options["user_indicators"]["high_highlight"] / 100
                low_threshold = data_options["user_indicators"]["low_highlight"] / 100
                limit = data_options["source_limit"][source]
                relative = attempt_value / limit
                if relative > high_threshold:
                    graph_data["highlight"].append(True)
                elif relative < low_threshold:
                    graph_data["highlight"].append(False)
                else:
                    graph_data["highlight"].append(None)
            else:
                graph_data["attempt"].append(0)
                graph_data["attempt_made"].append(False)
                graph_data["highlight"].append(None)

            # Create list of row sets for pandas for tables
            if datatype == "main": 
                utility = info[TERMS["utility"]]
                attribute = info[TERMS["attribute"]]
                origin = info[TERMS["origin"]]

                rows_for_history.append({
                    "Date": date, 
                    "#": object_collection, 
                    "Name": name,
                    attempt_title: attempt_value, 
                    TERMS["source"]: source,
                    TERMS["origin"]: origin, 
                    TERMS["attribute"]: attribute, 
                    TERMS["utility"]: utility, 
                    TERMS["state"]: state, 
                    "Index": index})
            else:
                utility = info[TERMS["utility"]]

                rows_for_history.append({
                    "Date": date, 
                    " ": object_collection, 
                    "Name": name,
                    attempt_title: attempt_value, 
                    TERMS["source"]: source,
                    TERMS["utility"]: utility, 
                    TERMS["state"]: state, 
                    "Index": index})
        if not any(attempt_per_object):
            mean_attempt = None
        else:
            if None in attempt_per_object:
                attempt_per_object.remove(None)
            mean_attempt = "%.1f" % statistics.mean(attempt_per_object)
        if datatype == "main": 
            rows_for_overview.append({
                "Name": name,
                "Total": len(info[TERMS["event"]]) - 1,
                "Mean": mean_attempt,
                TERMS["origin"]: info[TERMS["origin"]],
                TERMS["attribute"]: info[TERMS["attribute"]],
                TERMS["utility"]: info[TERMS["utility"]]
            })
        else: 
            rows_for_overview.append({
                "Name": name,
                "Total": len(info[TERMS["event"]]) - 1,
                "Mean": mean_attempt,
                TERMS["utility"]: info[TERMS["utility"]]
            })

    if len(database) == 0: 
        if datatype == "main": 
            rows_for_history = [{
                    "Date": None, 
                    "#": None, 
                    "Name": None,
                    attempt_title: None, 
                    TERMS["source"]: None,
                    TERMS["origin"]: None, 
                    TERMS["attribute"]: None, 
                    TERMS["utility"]: None, 
                    TERMS["state"]: None, 
                    "Index": None}]
            rows_for_overview = [{
                "Name": None,
                "Total": None,
                "Mean": None,
                TERMS["origin"]: None,
                TERMS["attribute"]: None,
                TERMS["utility"]: None}]
        else:
            rows_for_history = [{
                    "Date": None, 
                    " ": None, 
                    "Name": None,
                    attempt_title: None, 
                    TERMS["source"]: None,
                    TERMS["utility"]: None, 
                    TERMS["state"]: None, 
                    "Index": None}]
            rows_for_overview = [{
                "Name": None,
                "Total": None,
                "Mean": None,
                TERMS["utility"]: None
            }]
            
    return {
        "counts": counts,
        "attempt_list": attempt_value_list,
        "last_event": last_event,
        "success_fail": success_fail, 
        "table_data": rows_for_history,
        "overview_data": rows_for_overview,
        "graph_data": graph_data,
        "attempt_title": attempt_title,
        "valid": True}


@st.cache_data
def history_dataframe(rows: list, object_type: str):
    """
    Database processing for table view (main or secondary) 
    for view of object history

    Args:
        rows (list):
            list of dictionaries for pandas table view rows
        object_type (str):
            defines "main" or "secondary" object type

    Returns:
        processed pandas dataframe rows:
            date, consecutive count, name, progress, source, labels, state
    """
    
    dataframe = pd.DataFrame(rows)
    # Use index for sorting, then discard 
    processed_dataframe = (
        dataframe.sort_values(["Date", "Index"], ascending=False)
        .drop(columns=["Index"]))

    # Collection value disregarded for secondary type
    if object_type == "secondary": 
        processed_dataframe = (processed_dataframe.drop(columns=[" "]))

    return processed_dataframe


@st.cache_data
def overview_dataframe(rows: list):
    """
    Database processing for table view (main or secondary) 
    for view of object catalog

    Args:
        rows (list):
            list of dictionaries for pandas table view rows

    Returns:
        processed pandas dataframe rows:
            name, total count, mean progress, labels
    """
    
    dataframe = pd.DataFrame(rows)
    # Use index for sorting, then discard
    processed_dataframe = (
        dataframe.sort_values(["Name"], ascending=True))

    return processed_dataframe
                    