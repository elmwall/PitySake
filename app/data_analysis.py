"""
Simple statistics

Builds and manages:
- overview statistics for progress data
- counts of main object data labels
"""

import logging
import statistics 

import streamlit as st

import app.data_access as hold


TERMS = st.session_state["TERMS"]
logger = logging.getLogger(__name__)
active_attempt_ref = TERMS["active_attempts"]
attempt_ref = TERMS["attempt"]
event_ref = TERMS["event"]
main_ref = TERMS["main"]
secondary_ref = TERMS["secondary"]


def small_stats(component_key: str, sub_keys: list, 
                set_width: int | str, set_height: int | str):
    """
    Render statistics feature
    - Progress overview:
        - Last event progress
        - Median progress per event
        - Sucess rate for uncertain outcomes
        - Total progress value
    - Label collection:
        - counts for objects with each label
    """
    logger.info("Running")
    
    # Feature header
    if st.session_state["header_switch"]:
        with st.container(
                key=f"{component_key}_head", 
                width=set_width, height="content"):
            st.markdown("##### *Statistics*", text_alignment="left")

    # Main container
    feat_height = "content" if set_height > 400 else "stretch"
    with st.container(
            border=True, key=f"{component_key}_main", 
            width=set_width, height=feat_height):
        st.markdown("")

        counts, total_val, last, att_median, success_rate = _analyze_data()

        # Content frame
        with st.container(width="stretch", height="stretch"):
            col_1, col_2 = st.columns([30, 30])

            # Progress overview
            # Divided into four metric views
            with col_1:
                # Top row
                with st.container(
                        border=True, key=sub_keys[4], 
                        width="stretch", height=245):
                    with st.container():
                        col_l, col_r = st.columns(2)
                        col_l.metric(
                            f"Last {event_ref.lower()}", 
                            value=last, help=f"For {main_ref.lower()}s", 
                            delta=f"{last - att_median}", delta_color="inverse", 
                            border=False, width="stretch", delta_description="vs med")
                        median_help_text = f"""From {main_ref.lower()} {event_ref.lower()}s. 
                            Median: mid-value, half above/half below."""
                        col_r.metric(
                            f"Median", value=att_median, help=median_help_text, 
                            border=False, width="stretch")
                        st.space(18)
                    # Bottom row
                    with st.container():
                        col_l, col_r = st.columns(2)
                        rate_help_text = f"""From {main_ref.lower()} 
                            and {secondary_ref.lower()} {event_ref.lower()}s"""
                        col_l.metric(
                            "Win rate", value=f"{success_rate}%", 
                            help=rate_help_text, 
                            border=False, 
                            width="stretch")            
                        col_r.metric(
                            f"Total {active_attempt_ref.lower()}", value=total_val, 
                            help=f"Estimated from {event_ref.lower()}s and {attempt_ref.lower()}", 
                            border=False, width="stretch")
            
            # Label count
            with col_2:
                stat_height = "stretch" if set_height > 600 else 245
                with st.container(border=False, height=stat_height):
                    collist = st.columns(3)
                    n = 0
                    for x in counts.values():
                        for a, b in x.items():
                            collist[n].metric(f"{a}", value=b)
                        n += 1


def _analyze_data() -> tuple:
    """
    Data processing and calculations for statistics

    Preparing databases:
    - Retrieves databases from cache
    - Sends data for processing / retrieves chached data
    
    Returns:
        Tuple (dict, int, int, int, str):
            counts (dict): counts of main object labels  
            total_val (int): total registered progress/attempts in project  
            last (int): last event progress  
            att_median (int): median progress achieved from all registered events  
            success_rate (str): for main and secondary events
    """

    # Collect databases from cache
    main_database = hold.load_main_database()
    secondary_database = hold.load_secondary_database()
    progress = hold.load_progress_data()
    # Send databases for processing, alt retrieve cached processed data
    processed_main = hold.process_collection_db(main_database, "main")
    processed_secondary = hold.process_collection_db(secondary_database, "secondary")

    # Calculate success rate
    main_success = processed_main["success_fail"]
    secondary_success = processed_secondary["success_fail"]
    success = main_success[0] + secondary_success[0]
    success_rate = success / sum(main_success + secondary_success)*100
    success_rate = "%.f" % success_rate

    # Collect progress not yet registered as event
    attempts = 0
    for x  in progress.values():
        attempts += x[attempt_ref]
    # Collect all (completed) progress values registered as events
    attempt_list = processed_main["attempt_list"] + processed_secondary["attempt_list"]
    total_val = sum(attempt_list) + attempts

    # Median progress/attempts for all registered events
    att_median = statistics.median(attempt_list)

    # Last registered event
    last = processed_main["last_event"][1]

    # Main object label count
    counts = processed_main["counts"]
    print(type(att_median))
    return counts, total_val, last, att_median, success_rate