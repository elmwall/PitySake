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
            success_fail_tot (list): counts of positive (index 0) and negative (index 1) 
            and total (index 2)  
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
    success_fail_tot = [0, 0, 0]
    # Recording no of an object collected
    object_count = dict()
    # Data for pandas/st.dataframe
    rows_for_history = list()
    rows_for_overview = list()
    attempt_ref = TERMS["attempt"]
    if TERMS["unit"]: 
        attempt_title = f"{TERMS["unit"]} {attempt_ref}" 
    else:
        attempt_title = attempt_ref

    if not len(data_options) > 0:
        return {
            "counts": counts,
            "attempt_list": attempt_value_list,
            "last_event": last_event,
            "success_fail_tot": success_fail_tot, 
            "table_data": rows_for_history,
            "overview_data": rows_for_overview,
            "graph_data": graph_data,
            "attempt_title": attempt_title,
            "valid": False}

    utility_ref = TERMS["utility"]
    attribute_ref = TERMS["attribute"]
    origin_ref = TERMS["origin"]
    # For counting object labels - Define dictionary with category keys and data keys 
    if datatype == "main": 
        category_list = [utility_ref, attribute_ref, origin_ref]
        for category in category_list:
            counts[category] = dict()

    state_value, date, object_collection, name, attempt_value, source, state, index = [None]*8
    state_ref = TERMS["state"]
    state_win_ref = TERMS["state_win"]
    state_loss_ref = TERMS["state_loss"]
    source_ref = TERMS["source"]
    event_ref = TERMS["event"]
    high_highlight = data_options["user_indicators"]["high_highlight"]
    low_highlight = data_options["user_indicators"]["low_highlight"]
    source_limit = data_options["source_limit"]
    start_count_value = data_options["value_limits"]["collection_start_count"]
    for name, info in database.items():
        # Only count labels for main type object
        if datatype == "main": 
            for category in category_list:
                if info[category] not in counts[category]:
                    counts[category][info[category]] = 1
                else:
                    counts[category][info[category]] += 1
        
        attempt_per_object = list()  
        # Collect event data
        for event_id, event_data in info[event_ref].items(): 
            # Collect date and index
            date, index = event_id.split("-")
            # For main type object, dataview should show collection count 
            formatted_date = datetime.datetime.strptime("20" + date, "%Y%m%d").strftime("%Y-%m-%d")
            if datatype == "main":
                if name in object_count:
                    object_count[name] += 1
                else:
                    object_count[name] = start_count_value
                object_collection = f"{object_count[name]}"
            else:
                object_collection = ""

            # Collect attempt
            attempt_value = event_data[attempt_ref]
            attempt_per_object.append(attempt_value)
            state = event_data[state_ref]
            if attempt_value:
                # Collect all attempt results in a list
                attempt_value_list.append(attempt_value)
                # Check date to identify latest value
                if int(date) > last_event[0]:
                    last_event = [int(date), attempt_value]

            # Collect state
            if state == state_win_ref:
                success_fail_tot = [success_fail_tot[0] + 1, success_fail_tot[1], success_fail_tot[2] + 1]
                state_value = True
            elif state == state_loss_ref: 
                success_fail_tot = [success_fail_tot[0], success_fail_tot[1] + 1, success_fail_tot[2] + 1]
                state_value = False
            else:
                success_fail_tot = [success_fail_tot[0], success_fail_tot[1], success_fail_tot[2] + 1]
                state_value = None

            # Collect values for graph data
            graph_data["date"].append(formatted_date)
            graph_data["name"].append(name)
            graph_data["state"].append(state_value)
            graph_data["type"].append(datatype)
            # Adapt attempt and highlight values depending on data present
            source = event_data[source_ref]
            if attempt_value is not None:
                graph_data["attempt"].append(attempt_value)
                graph_data["attempt_made"].append(True)

                high_threshold = high_highlight / 100
                low_threshold = low_highlight / 100
                limit = source_limit[source]
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


            # Create list of row sets for pandas for tables - history
            if datatype == "main": 
                utility = _translate_label(info, utility_ref)
                attribute = _translate_label(info, attribute_ref)
                origin = _translate_label(info, origin_ref)

                rows_for_history.append({
                    "Date": date, 
                    "#": object_collection, 
                    "Name": name,
                    attempt_title: attempt_value, 
                    source_ref: source,
                    utility_ref: utility, 
                    attribute_ref: attribute, 
                    origin_ref: origin, 
                    state_ref: state, 
                    "Index": index})
            else:
                utility = _translate_label(info, utility_ref)

                rows_for_history.append({
                    "Date": date, 
                    " ": object_collection, 
                    "Name": name,
                    attempt_title: attempt_value, 
                    source_ref: source,
                    utility_ref: utility, 
                    state_ref: state, 
                    "Index": index})
                
        # Adapt data
        if not any(attempt_per_object):
            mean_attempt = None
        else:
            if None in attempt_per_object:
                attempt_per_object.remove(None)
            mean_attempt = "%.1f" % statistics.mean(attempt_per_object)
        total = len(info[event_ref]) - 1 + start_count_value
        if total < 0: total = None
        # Create list of row sets for pandas for tables - overview
        if datatype == "main": 
            utility = _translate_label(info, utility_ref)
            attribute = _translate_label(info, attribute_ref)
            origin = _translate_label(info, origin_ref)

            rows_for_overview.append({
                "Name": name,
                "Total": total,
                "Mean": mean_attempt,
                utility_ref: utility,
                attribute_ref: attribute,
                origin_ref: origin})
        else: 
            utility = _translate_label(info, utility_ref)

            rows_for_overview.append({
                "Name": name,
                "Total": total,
                "Mean": mean_attempt,
                utility_ref: utility})

    if datatype == "main": 
        for category in category_list:
            for option in data_options[TERMS["main"]][category]:
                if option not in counts[category]:
                    counts[category][option] = 0

    # Placeholder data for new/missing database
    if len(rows_for_history) == 0: 
        if datatype == "main": 
            rows_for_history = [{
                    "Date": None, 
                    "#": None, 
                    "Name": None,
                    attempt_title: None, 
                    source_ref: None,
                    utility_ref: None, 
                    attribute_ref: None, 
                    origin_ref: None, 
                    state_ref: None, 
                    "Index": None}]
        else:
            rows_for_history = [{
                    "Date": None, 
                    " ": None, 
                    "Name": None,
                    attempt_title: None, 
                    source_ref: None,
                    utility_ref: None, 
                    state_ref: None, 
                    "Index": None}]
    if len(rows_for_overview) == 0:
        if datatype == "main": 
            rows_for_overview = [{
                "Name": None,
                "Total": None,
                "Mean": None,
                utility_ref: None,
                attribute_ref: None,
                origin_ref: None}]
        else:
            rows_for_overview = [{
                "Name": None,
                "Total": None,
                "Mean": None,
                utility_ref: None}]

    return {
        "counts": counts,
        "attempt_list": attempt_value_list,
        "last_event": last_event,
        "success_fail_tot": success_fail_tot, 
        "table_data": rows_for_history,
        "overview_data": rows_for_overview,
        "graph_data": graph_data,
        "attempt_title": attempt_title,
        "valid": True}


def _translate_label(info, label):
    return info[label] if info[label] != "_Blank_" else ""


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
                    