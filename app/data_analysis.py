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
                        col_left, col_right = st.columns(2)
                        reverse = hold.load_options()["user_indicators"]["reverse_positive"]
                        compare_to_median = int(last - att_median)
                        sign = "+" if compare_to_median > 0 else "-"
                        delta_color = "inverse" if reverse else "normal"
                        unit = TERMS["unit"] if TERMS["unit"] else ""
                        help = f"For {main_ref.lower()}s. {sign} {compare_to_median} compared to median"
                        with col_left:
                            _adjusted_metric(
                                f"Last {event_ref.lower()}", metric_key="last_metric", 
                                metric_value=f"{last}{unit}",
                                base_limit=5, help_text=help, 
                                delta={"text": f"{compare_to_median}", "color": delta_color})
                        
                        help = f"""From {main_ref.lower()} {event_ref.lower()}s. 
                            Median: mid-value, half above/half below."""
                        with col_right:
                            _adjusted_metric(
                                "Median", metric_key="median_metric", 
                                metric_value=f"{att_median}{unit}",
                                base_limit=5, help_text=help)
                        st.space(18)

                    # Bottom row
                    with st.container():
                        col_left, col_right = st.columns(2)
                        rate_help_text = f"""From {main_ref.lower()} 
                            and {secondary_ref.lower()} {event_ref.lower()}s"""
                        col_left.metric(
                            f"{TERMS["state_win"]}", value=f"{success_rate}%", 
                            help=rate_help_text, 
                            border=False, 
                            width="stretch")
                        help=f"""All-time total sum of {attempt_ref.lower()} 
                            from {main_ref} and {secondary_ref} history and tracker"""
                        with col_right:
                            _adjusted_metric(
                                "Total", metric_key="tot_metric", 
                                metric_value=f"{total_val}{unit}",
                                base_limit=5, help_text=help)
            
            # Label count 
            with col_2:
                stat_height = "stretch" if set_height > 600 else 245
                with st.container(border=False, key="label_list", height=stat_height):
                    collist = st.columns(3)
                    n = 0
                    i = 0
                    for label_data in counts.values():
                        for label, val in label_data.items():
                            with collist[n]:
                                _adjusted_metric(
                                    f"{label}", metric_key=f"label{n}_{i}", 
                                    metric_value=val, base_limit=4, base_size=25, help_text="")
                            i += 1
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
    processed_main = hold.process_main_db(main_database)
    processed_secondary = hold.process_secondary_db(secondary_database)

    # Calculate success rate
    main_success = processed_main["success_fail"]
    secondary_success = processed_secondary["success_fail"]
    success = main_success[0] + secondary_success[0]
    if sum(main_success + secondary_success) > 0:
        success_rate = success / sum(main_success + secondary_success)*100
    else:
        success_rate = 0
    success_rate = "%.f" % success_rate

    # Collect progress not yet registered as event
    attempts = 0
    for x  in progress.values():
        attempts += x[attempt_ref]
    # Collect all (completed) progress values registered as events
    attempt_list = processed_main["attempt_list"] + processed_secondary["attempt_list"]
    total_val = sum(attempt_list) + attempts

    # Median progress/attempts for all registered events
    if len(attempt_list) > 0:
        att_median = statistics.median(attempt_list)
    else:
        att_median = 0

    # Last registered event
    last = processed_main["last_event"][1]

    # Main object label count
    counts = processed_main["counts"]
    return counts, total_val, last, att_median, success_rate


def _adjusted_metric(title: str, metric_key: str, metric_value: int, base_limit: int, 
                     help_text: str, base_size: int = 36, delta: bool = None):
    """
    Generate metric with length-dependent font size

    Behavior: decreases metric value font through CSS with a gradually decreasing value 
    until lengths beyond 13, well beyond values this app is intended for. 
    New symbols above length limit while large triggers large decrease.  
    In this way the also large numbers fits, preventing shortening as e.g. "5000...". 

    Args:
        title (str):
            label text
        metric_key (str):
            key for creating CSS class
        base_limit (int):
            threshold length of input before resizing
        helt_text (str): 
            hover text for metric widget
        base_size (int):
            sets 
    """
    
    length = len(str(metric_value))
    if length > base_limit:
        if length < 14:
            size = base_size - int(base_size * float(1 - float(base_limit / length)))
        else:
            size = 14
        st.html("""<style>
                    .st-key-KEY_REF [data-testid="stMetricValue"] {
                        font-size: SIZE_REFpx;
                    }
                </style>"""
                .replace("KEY_REF", metric_key)
                .replace("SIZE_REF", str(size)))
    else:
        st.html("""<style>
                    .st-key-KEY_REF [data-testid="stMetricValue"] {
                        font-size: SIZE_REFpx;
                    }
                </style>"""
                .replace("KEY_REF", metric_key)
                .replace("SIZE_REF", str(base_size)))
    with st.container(key=metric_key):
        if delta:
            delta_color = "grey" if int(delta["text"]) == 0 else delta["color"]
            st.metric(
                title, value=metric_value, 
                help=help_text, border=False, width="stretch",
                delta=delta["text"], delta_color=delta_color)
        else:
            st.metric(
                title, value=metric_value, 
                help=help_text, border=False, width="stretch")