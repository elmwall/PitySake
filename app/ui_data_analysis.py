import streamlit as st
import statistics 

from .data_access import Holder

from settings.config import TERMS


def small_stats(data_options, component_key):
    hold = Holder()
    with st.container(key=f"{component_key}_head", height="content"):
        st.markdown("##### *Character statistics*", text_alignment="left")
    with st.container(border=True, key=f"{component_key}_main", height="stretch"):
        st.markdown("")
        object_database = hold.load_main_database()

        attempt_list = list()
        att_date = dict()
        success_rate = {
            "Win": 0,
            "Loss": 0,
            "Rate": 0
        }
        lowest = 100
        highest = 0

        counts = {
            TERMS["origin"]: {},
            TERMS["attribute"]: {},
            TERMS["utility"]: {}
        }
        for x, y in counts.items():
            for z in data_options[TERMS["main"]][x]:
                # print(x, y, z)
                counts[x][f"{z}"] = 0

        for main_data in object_database.values():
            for cat, rec in counts.items():
                rec[main_data[cat]] += 1
            for date, ev_data in main_data[TERMS["event"]].items():
                att = ev_data[TERMS["attempt"]]
                if att: 
                    attempt_list.append(att)
                    att_date[f"{date}"] = att
                    # n += 1
                    if att < lowest: lowest = att
                    if att > highest: highest = att
                state = ev_data[TERMS["state"]]
                if state:
                    if state == TERMS["state_win"]: success_rate["Win"] += 1
                    elif state == TERMS["state_loss"]: success_rate["Loss"] += 1
        tot = success_rate["Win"] + success_rate["Loss"]
        if tot > 0:
            ratio = 100 * success_rate["Win"] / tot
            success_rate["Rate"] = str("%.f" % ratio)

        attempt_list.sort()
        att_date = dict(sorted(att_date.items(), key=lambda item:str(item[0])))
        last10 = list(att_date.values())[:10]
        last10.reverse()

        top = dict()
        table_coll = dict()
        for x, y in counts.items():
            top[x] = {"0": [0]}
            table_coll[x] = f"{x}:  \n"
            for a, b in y.items():
                table_coll[x] += f"{b} {a}  \n"
                for i, j in top[x].items():
                    # print("j", j)
                    if b == int(i): 
                        j.append(a)
                        top[x] = {str(b): j}
                    if b > int(i): 
                        top[x] = {str(b): [a]}

        att_median = statistics.median(attempt_list)
        att_mean = statistics.mean(attempt_list)
        att_mode = statistics.mode(attempt_list)
        datelist = list(att_date.keys())
        last = att_date[datelist[len(datelist)-1]]
        last10_med = statistics.median(last10)
        last10_mean = statistics.mean(last10)

        if last < att_median: 
            green_vis, red_vis = "green", "transparent"
        elif last > att_median: 
            green_vis, red_vis = "transparent", "red"
        else:
            green_vis, red_vis = "transparent", "transparent"
        col_1, col_m, col_2 = st.columns([12, 1, 17])
        with col_1:
            col_left, col_mid, col_right = st.columns([1, 9, 7])
            with col_mid:
                with st.container(border=False, width="stretch", height="content", horizontal_alignment="center", vertical_alignment="center"):
                    st.html("<div style='font-size: 50px; margin: -1rem 0; padding: 0; line-height: 1; text-align: center; color: REF;'>⏶</div>".replace("REF", red_vis))
                with st.container(border=True, width="stretch", height="content", horizontal_alignment="center", vertical_alignment="center"):
                    html_output = "<div style='font-size: 50px; margin: 0; padding: 0; line-height: 1; text-align: center;'>REF</div>"
                    result_output = f"{last}"
                    st.html(html_output.replace("REF", result_output))
                with st.container(border=False, width="stretch", height="content", horizontal_alignment="center", vertical_alignment="center"):
                    st.html("<div style='font-size: 50px; margin: -1.5rem 0 ; padding: 0; line-height: 1; text-align: center; color: REF;'>⏷</div>".replace("REF", green_vis))
            with col_right:
                with st.container(border=False, width="stretch", height="stretch", horizontal_alignment="center", vertical_alignment="center"):
                    label_last = f"Last {TERMS["event"]}"
                    st.html("<div style='font-size: 22px; margin: 1.0rem 0 0 -0.5rem; padding: 0; line-height: 1; text-align: left;'>REF</div>".replace("REF", label_last))
            st.space("medium")
        with col_1:
            col_left, col_mid, col_right = st.columns([1, 9, 7])
            with col_mid:
                with st.container(border=True, width="stretch", height="content", horizontal_alignment="center", vertical_alignment="center"):
                    html_output = "<div style='font-size: 50px; height: 50px; margin: 0; padding: 0; line-height: 1; text-align: center;'>REF</div>"
                    result_output = f"{success_rate["Rate"]}"
                    st.html(html_output.replace("REF", result_output))
            with col_right:
                with st.container(border=False, width="stretch", height="stretch", horizontal_alignment="center", vertical_alignment="center"):
                    label_last = f"%"
                    st.html("<div style='font-size: 30px; margin: 0rem 0 0 -0.5rem; padding: 0; line-height: 1; text-align: left;'>REF</div>".replace("REF", label_last))
                    st.html("<div style='font-size: 20px; margin: 0rem 0 0 -0.5rem; padding: 0; line-height: 0; text-align: left;'>REF</div>".replace("REF", "win rate"))
            print("test1")
            last10_mean_col = "red" if att_mean < last10_mean else "green"
            last10_med_col = "red" if att_median < last10_med else "green"

        with col_2:
            st.markdown(" ")
            col_3, col_4, col_5 = st.columns([5, 11, 10])
            st.markdown(" ")
            col_3.markdown(f"""
                {"%.1f" % att_mean}  
                {"%.0f" % att_median}  
                {att_mode}  
                {lowest}-{highest}    
            """)
            col_4.markdown(f"""
                Average  
                Half below  
                Most occuring  
                Lowest-Highest  
            """)
            col_5.markdown(f"""
10 last: :{last10_mean_col}[{"%.1f" % last10_mean}]
10 last: :{last10_med_col}[{"%.0f" % last10_med}]
""")
            
            def count_occurrence(category):
                space = ""
                num, entries = [str()]*2
                
                for x, y in top[category].items():
                    num = x
                    for z in y:
                        if len(y) > 4:
                            entries += f"{space}{z[:2]}"
                            space = "/"
                        elif len(y) > 1:
                            entries += f"{space}{z[:3]}"
                            space = "/"
                        else:
                            entries = z

                return num, entries
            num_origin, entries_origin = count_occurrence(TERMS["origin"])
            num_attribute, entries_attribute = count_occurrence(TERMS["attribute"])
            num_utility, entries_utility = count_occurrence(TERMS["utility"])
            # st.markdown(f"{TERMS["origin"]}s: {num} in {entries}")

            st.markdown("*Most collected character types:*")
            col_3, col_4, col_5 = st.columns([4, 1, 10])
            # st.space("large")
            col_3.markdown(f"""
                {TERMS["origin"]}s  
                {TERMS["attribute"]}s  
                {TERMS["utility"]}s
            """)
            col_4.markdown(f"""
                {num_origin}  
                {num_attribute}  
                {num_utility}
            """)
            col_5.markdown(f"""
                {entries_origin}  
                {entries_attribute}  
                {entries_utility}
            """)

