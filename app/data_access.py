import datetime
import pandas as pd
from dataclasses import dataclass

import streamlit as st

from .file_manager import Archivist
# import app.config_hub as hub
# from settings.config import TERMS, DIRECTORIES, DATAPATH, SETTINGS
# from app.configg import DIRECTORIES, SETTINGS, DATAPATH
from app.config_hub import TERMS, DIRECTORIES, SETTINGS, DATAPATH


arciv = Archivist(DIRECTORIES, DATAPATH, "nofile")


# @dataclass
# class AppContext:
#     project_root: str
#     config: dict


@st.cache_data
def load_main_database():
    """
    Loads and caches main database with three labels (region, origin, attempt) and event data.
    Event data has date, attempts and source
    """
    datafile = DATAPATH[TERMS["main"]]
    return arciv.reader(datafile, join_path="data")

@st.cache_data
def load_secondary_database():
    """
    Loads and caches secondary database with one labels (type) and event data
    Event data has date, attempts and source
    """
    datafile = DATAPATH[TERMS["secondary"]]
    return arciv.reader(datafile, join_path="data")

@st.cache_data
def load_progress_data():
    """
    Loads and caches logged attempt/progress data for efforts in different sources
    """
    datafile = DATAPATH["progress"]
    return arciv.reader(datafile, join_path="data")

@st.cache_data
def load_options():
    """
    Loads and caches data option needed for registering and analyzing data
    """
    options_file = SETTINGS["Options"]
    
    return arciv.reader(other_file=options_file, join_path="settings")

@st.cache_data
def load_themes():
    """
    Loads and caches style settings
    """
    options_file = SETTINGS["Themes"]
    return arciv.reader(other_file=options_file, join_path="settings")


@st.cache_data
def process_collection_db(database, datatype):
    """
    Perform and cache calculations and data collection and process them for easy accessibility
    Processes databases organized by Object name | Details, including Event date | Event details
    Generate data for table and graph features
    """
    data_options = load_options()
    graph_data = {
        "name": [],
        "date": [],
        "attempt": [],
        "state": []
    }
    
    attempt_value_list = list()     # For analysis of values
    counts = dict()                 # To count Category - Label - How many
    last_event = [0, 0]             # To record last attempt [date, attempt value]
    success_fail = [0, 0]            # To record [successful, failed] attempts
    object_count = dict()           # Recording main object type collected
    rows_for_table = list()         # Data for pandas/st.dataframe

    # For counting object labels - Define dictionary with category keys and data keys 
    if datatype == "main": 
        for category, options in data_options[TERMS["main"]].items():
            counts[category] = dict()
            for x in options:
                counts[category][x] = 0
    state_value, date, object_collection, name, attempt_value, source, state, index = [None]*8
    for name, info in database.items():
        # Initiate non-values

        # Only count labels for main type object
        if datatype == "main": 
            for category, options in counts.items():
                object_option = info[category]
                counts[category][object_option] += 1
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
    print(len(graph_data["attempt"]), len(graph_data["state"]))

    return {
        "counts": counts,
        "attempt_list": attempt_value_list,
        "last_event": last_event,
        "success_fail": success_fail, 
        "table_data": rows_for_table,
        "graph_data": graph_data
    }


@st.cache_data
def data_to_dataframe(rows, object_type):
    """
    Process data with basic formatting for Pandas dataframe
    """
    dataframe = pd.DataFrame(rows)
    processed_dataframe = (
        dataframe.sort_values(["Date", "Index"], ascending=False)
        .drop(columns=["Index", f"{TERMS["state"]}"])
    )
    if object_type == "secondary": processed_dataframe = (processed_dataframe.drop(columns=[" "]))
    processed_dataframe[TERMS["attempt"]] = pd.to_numeric(
        processed_dataframe[TERMS["attempt"]], errors="coerce"
    ).astype("Int64")

    return processed_dataframe


                    