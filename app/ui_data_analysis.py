import streamlit as st
import statistics 

def small_stats(component_key, height, key_reg_obj, key_list_reg, arciv, negotiator, DIRECTORIES, DATAPATH, data_options, TERMS, attempts):
    with st.container(key=f"{component_key}_head", height="content"):
        st.markdown("##### *Character statistics*", text_alignment="left")
    with st.container(border=True, key=f"{component_key}_main", height="stretch"):
        st.markdown("")

        data_reference = TERMS["Character"]
        datafile = DATAPATH[data_reference]
        object_database = arciv.reader(datafile, join_path="data")

        attempt_list = list()
        att_date = dict()
        success_rate = {
            "Win": 0,
            "Loss": 0,
            "Rate": 0
        }
        n = 0
        lowest = 100
        highest = 0
        # count_tool, count_attribute, count_origin = [dict()]*3
        # for x in data_options[TERMS["Character"]][TERMS["Tool"]]:
        #     count_tool[x] = 0
        # for x in data_options[TERMS["Character"]][TERMS["Attribute"]]:
        #     count_attribute[x] = 0
        # for x in data_options[TERMS["Character"]][TERMS["Origin"]]:
        #     count_origin[x] = 0
        
        counts = {
            TERMS["Origin"]: {},
            TERMS["Attribute"]: {},
            TERMS["Tool"]: {}
        }
        for x, y in counts.items():
            for z in data_options[TERMS["Character"]][x]:
                # print(x, y, z)
                counts[x][f"{z}"] = 0



        for ch_data in object_database.values():
            for cat, rec in counts.items():
                rec[ch_data[cat]] += 1
            for date, ev_data in ch_data[TERMS["Event"]].items():
                att = ev_data[TERMS["Attempt"]]
                if att: 
                    attempt_list.append(att)
                    att_date[f"{date}"] = att
                    # n += 1
                    if att < lowest: lowest = att
                    if att > highest: highest = att
                state = ev_data[TERMS["State"]]
                if state:
                    if state == TERMS["StateWin"]: success_rate["Win"] += 1
                    elif state == TERMS["StateLoss"]: success_rate["Loss"] += 1
        tot = success_rate["Win"] + success_rate["Loss"]
        if tot > 0:
            ratio = 100 * success_rate["Win"] / tot
            success_rate["Rate"] = str("%.f" % ratio)

        # print(success_rate)
            # ch_attempts = [x for x in ch_data if ]
            # attempt_list.extend()
            # for ev_data in ch_data[TERMS["Event"]].values():
            #     att = ev_data[TERMS["Attempt"]]
            #     if att: attempt_list.append(att)
        
        attempt_list.sort()
        att_date = dict(sorted(att_date.items(), key=lambda item:str(item[0])))
        last10 = list(att_date.values())[:10]
        last10.reverse()
        # print("t", att_date)
        # print("s", last10[:10])

        # catlist = list(counts.keys())
        # last = att_date[datelist[len(datelist)-1]]
        # table_coll = dict()
        # for x, y in counts.items():
        #     table_coll[x] = f"|{x}|Count|\n|-|-|\n"
        #     for a, b in y.items():
        #         table_coll[x] += f"|{a}|{b}|\n"
        # print(table_coll)

        top = dict()
        # max_att, max_ori, max_tool = [0]*3
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
                    # print(i, j)
        # print(top)

            

        # print(attempt_list)

        att_median = statistics.median(attempt_list)
        att_mean = statistics.mean(attempt_list)
        att_mode = statistics.mode(attempt_list)
        datelist = list(att_date.keys())
        last = att_date[datelist[len(datelist)-1]]
        last10_med = statistics.median(last10)
        last10_mean = statistics.mean(last10)

        # lowest = 

        # print(att_median, "%.1f" % att_mean)
        # col_1, col_2, col_3, col_4 = st.columns([0.2, 0.2, 0.2, 0.2])
        if last < att_median: 
            green_vis, red_vis = "green", "transparent"
        elif last > att_median: 
            green_vis, red_vis = "transparent", "red"
        else:
            green_vis, red_vis = "transparent", "transparent"
        # if last < att_median: sym = ":green[⏶]"
        # elif last > att_median: sym = ":red[⏷]"
        # else:
        #     sym = ""
        col_1, col_m, col_2 = st.columns([12, 1, 17])
        with col_1:
            col_left, col_mid, col_right = st.columns([1, 9, 7])
            with col_mid:
                with st.container(border=False, width="stretch", height="content", horizontal_alignment="center", vertical_alignment="center"):
                    st.html("<div style='font-size: 50px; margin: -1rem 0; padding: 0; line-height: 1; text-align: center; color: REF;'>⏶</div>".replace("REF", red_vis))
                with st.container(border=True, width="stretch", height="content", horizontal_alignment="center", vertical_alignment="center"):
                    html_output = "<div style='font-size: 50px; margin: 0; padding: 0; line-height: 1; text-align: center;'>REF</div>"
                    # st.markdown("### Stats")
                    result_output = f"{last}"
                    st.html(html_output.replace("REF", result_output))
                with st.container(border=False, width="stretch", height="content", horizontal_alignment="center", vertical_alignment="center"):
                    st.html("<div style='font-size: 50px; margin: -1.5rem 0; padding: 0; line-height: 1; text-align: center; color: REF;'>⏷</div>".replace("REF", green_vis))
            with col_right:
                with st.container(border=False, width="stretch", height="stretch", horizontal_alignment="center", vertical_alignment="center"):
                    # st.space("xsmall")
                    label_last = f"Last {TERMS["Event"]}"
                    st.html("<div style='font-size: 22px; margin: 1.0rem 0 0 -0.5rem; padding: 0; line-height: 1; text-align: left;'>REF</div>".replace("REF", label_last))
        
        with col_1:
            col_left, col_mid, col_right = st.columns([1, 9, 7])
            with col_mid:
                with st.container(border=False, width="stretch", height="content", horizontal_alignment="center", vertical_alignment="center"):
                    st.html("<div style='font-size: 50px; margin: -1rem 0; padding: 0; line-height: 1; text-align: center; color: REF;'>⏶</div>".replace("REF", red_vis))
                with st.container(border=True, width="stretch", height="content", horizontal_alignment="center", vertical_alignment="center"):
                    html_output = "<div style='font-size: 50px; height: 50px; margin: 0; padding: 0; line-height: 1; text-align: center;'>REF</div>"
                    # st.markdown("### Stats")
                    result_output = f"{success_rate["Rate"]}"
                    st.html(html_output.replace("REF", result_output))
                with st.container(border=False, width="stretch", height="content", horizontal_alignment="center", vertical_alignment="center"):
                    st.html("<div style='font-size: 50px; margin: -1.5rem 0; padding: 0; line-height: 1; text-align: center; color: REF;'>⏷</div>".replace("REF", green_vis))
            with col_right:
                with st.container(border=False, width="stretch", height="stretch", horizontal_alignment="center", vertical_alignment="center"):
                    # st.space("xsmall")
                    label_last = f"%"
                    st.html("<div style='font-size: 40px; margin: 0rem 0 0 -0.5rem; padding: 0; line-height: 1; text-align: left;'>REF</div>".replace("REF", label_last))
                    st.html("<div style='font-size: 20px; margin: 0rem 0 0 -0.5rem; padding: 0; line-height: 0; text-align: left;'>REF</div>".replace("REF", "win rate"))

            # col_3.markdown("Median")
            # col_4.markdown(f"{att_median}")
            # col_3.markdown("")
            # col_4.markdown(f"{att_median}")
            
            # st.markdown(f"""
            #     |Stat||
            #     |-|-:|
            #     |Average| {"%.1f" % att_mean}|
            #     |Median| {att_median}|
            #     |Lowest| {lowest}|
            #     |Highest| {highest}|
            #     |Last| {last}{sym}|
            # """)
        with col_2:
            # st.space("xsmall")
            st.markdown(" ")
            col_3, col_4, col_5 = st.columns([5, 11, 10])
            st.markdown(" ")
            col_3.markdown(f"""
                {"%.1f" % att_mean}  
                {att_median}  
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
10 last: {"%.1f" % last10_mean}
10 last: {"%.0f" % last10_med}
""")
            # st.markdown(table_coll[TERMS["Origin"]])
            
            def count_occurrence(category):
                space = ""
                num, entries = [str()]*2
                
                for x, y in top[TERMS[category]].items():
                    num = x
                    for z in y:
                        if len(y) > 4:
                            entries += f"{space}{z[:2]}"
                            space = "/"
                        elif len(y) > 1:
                            entries += f"{space}{z[:3]}"
                            space = "/"
                        else:
                            # print(top[TERMS[category]])
                            entries = z

                return num, entries
            
            num_origin, entries_origin = count_occurrence("Origin")
            num_attribute, entries_attribute = count_occurrence("Attribute")
            num_tool, entries_tool = count_occurrence("Tool")
            # st.markdown(f"{TERMS["Origin"]}s: {num} in {entries}")

            st.markdown("*Most collected character types:*")
            col_3, col_4, col_5 = st.columns([4, 1, 10])
            # st.space("large")
            col_3.markdown(f"""
                {TERMS["Origin"]}s  
                {TERMS["Attribute"]}s  
                {TERMS["Tool"]}s
            """)
            col_4.markdown(f"""
                {num_origin}  
                {num_attribute}  
                {num_tool}
            """)
            col_5.markdown(f"""
                {entries_origin}  
                {entries_attribute}  
                {entries_tool}
            """)
            # st.markdown(f"""
            #     {TERMS["Origin"]}s: {num_origin} from {entries_origin}  
            #     {TERMS["Attribute"]}s: {num_attribute} {entries_attribute.lower()}  
            #     {TERMS["Tool"]}s: {num_tool} {entries_tool.lower()}
            # """)
        # with col_3:
        #     st.markdown(table_coll[TERMS["Attribute"]])
        # with col_4:
        #     st.markdown(table_coll[TERMS["Tool"]])



        # if last < att_median: 
        #     st.markdown(f""":green[⏶]  
        #                 {last}""")
            # st.markdown(f"{last}")
        # elif last > att_median: 
        #     st.markdown(f"""{last}  
        #                 :red[⏷]""")
            # st.markdown(f"{last}")
            # st.markdown(":red[⏷]")
        # elif last == att_median: 
        #     st.markdown("# =")

        # print(att_date)
        # print(last)
        # p = 1 - 0.006
        # acc_p = 1 - 0.006
        # n = 1
        # p10, p20, p30, p40, p50 = [False]*5
        # print(1 - acc_p < 0.99) 
        # while 1 - acc_p < 0.99 and n < 100:
        #     k = 1 - acc_p
        #     k *= 100
        #     print(f"{n}:", "%.1f" % k)
        #     acc_p *= p 
        #     n += 1
        #     if not p10 and k > 10: 
        #         p10 = n
        #         print("here")
        #     if not p20 and k > 20: 
        #         p20 = n
        #         print("here")
        #     if not p30 and k > 30: 
        #         p30 = n
        #         print("here")
        #     if not p40 and k > 40: 
        #         p40 = n
        #         print("here")
        #     if not p50 and k > 50: 
        #         p50 = n
        #         print("here")
        # print("10", p10) 
        # print("20", p20) 
        # print("30", p30) 
        # print("40", p40) 
        # print("50", p50) 
