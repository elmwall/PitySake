import streamlit as st
import statistics 

import app.data_access as hold

from settings.config import TERMS


def small_stats(component_key, sub_keys, set_width, set_height):
    active_attempt_ref = TERMS["active_attempts"]
    attempt_ref = TERMS["attempt"]
    event_ref = TERMS["event"]
    main_ref = TERMS["main"]
    utility_ref = TERMS["utility"]
    
    if st.session_state["header_switch"]:
        with st.container(key=f"{component_key}_head", width=set_width, height="content"):
            st.markdown("##### *Statistics*", text_alignment="left")
    feat_height = "content" if set_height > 400 else "stretch"
    with st.container(border=True, key=f"{component_key}_main", width=set_width, height=feat_height):
        st.markdown("")
        object_database = hold.load_main_database()
        utility_database = hold.load_utility_database()
        progress = hold.load_progress_data()
        attempts = 0
        for x  in progress.values():
            attempts += x[attempt_ref]

        processed_main = hold.process_collection_db(object_database, "main")
        processed_utility = hold.process_collection_db(utility_database, "utility")

        counts = processed_main["counts"]

        main_success = processed_main["success_fail"]
        utility_success = processed_utility["success_fail"]
        success = main_success[0] + utility_success[0]
        success_rate = success / sum(main_success + utility_success)*100
        success_rate = "%.f" % success_rate

        attempt_list = processed_main["attempt_list"] + processed_utility["attempt_list"]
        total_val = sum(attempt_list) + attempts

        last = processed_main["last_event"][1]

        att_median = statistics.median(attempt_list)

        with st.container(width="stretch", height="stretch"):
            col_1, col_2 = st.columns([30, 30])
            with col_1:
                with st.container(border=True, key=sub_keys[4], width="stretch", height=245):
                    with st.container():
                        col_l, col_r = st.columns(2)
                        col_l.metric(
                            f"Last {event_ref.lower()}", 
                            value=last, 
                            help=f"For {main_ref.lower()}s", 
                            delta=f"{last - att_median}", 
                            delta_color="inverse", 
                            border=False, 
                            width="stretch", 
                            delta_description="vs med"
                        )
                        col_r.metric(
                            f"Median", value=att_median, 
                            help=f"From {main_ref.lower()} {event_ref.lower()}s. Median: mid-value, half above/half below.", 
                            border=False, 
                            width="stretch"
                        )
                        st.space(18)
                    with st.container():
                        col_l, col_r = st.columns(2)
                        col_l.metric(
                            "Win rate", 
                            value=f"{success_rate}%", 
                            help=f"From {main_ref.lower()} and {utility_ref.lower()} {event_ref.lower()}s", 
                            border=False, 
                            width="stretch"
                        )            
                        col_r.metric(
                            f"Total {active_attempt_ref.lower()}", 
                            value=total_val, 
                            help=f"Estimated from {event_ref.lower()}s and {attempt_ref.lower()}", 
                            border=False, 
                            width="stretch"
                        )
            with col_2:
                stat_height = "stretch" if set_height > 600 else 245
                with st.container(border=False, height=stat_height):
                    collist = st.columns(3)
                    n = 0
                    for x in counts.values():
                        for a, b in x.items():
                            collist[n].metric(f"{a}", value=b)
                        n += 1


