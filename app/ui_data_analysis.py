import streamlit as st
import statistics 

def small_stats(component_key, height, key_reg_obj, key_list_reg, arciv, negotiator, DIRECTORIES, DATAPATH, data_options, TERMS, attempts):
    with st.container(key=f"{component_key}_head", height=35):
        st.markdown("#### *Character statistics*", text_alignment="left")
    with st.container(border=True, key=f"{component_key}_main", height="stretch"):
        st.markdown("")

        data_reference = TERMS["Character"]
        datafile = DATAPATH[data_reference]
        object_database = arciv.reader(datafile, join_path="data")

        attempt_list = list()
        att_date = dict()
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
                    att_date[f"{date[:6]}_{n}"] = att
                    n += 1
                    if att < lowest: lowest = att
                    if att > highest: highest = att
            # ch_attempts = [x for x in ch_data if ]
            # attempt_list.extend()
            # for ev_data in ch_data[TERMS["Event"]].values():
            #     att = ev_data[TERMS["Attempt"]]
            #     if att: attempt_list.append(att)
        
        attempt_list.sort()
        att_date = dict(sorted(att_date.items(), key=lambda item:str(item[0])))

        catlist = list(counts.keys())
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
        datelist = list(att_date.keys())
        last = att_date[datelist[len(datelist)-1]]
        # lowest = 

        # print(att_median, "%.1f" % att_mean)
        # col_1, col_2, col_3, col_4 = st.columns([0.2, 0.2, 0.2, 0.2])
        col_1, col_2 = st.columns([0.4, 0.6])
        with col_1:
            # st.markdown("### Stats")
            if last < att_median: sym = ":green[⏶]"
            elif last > att_median: sym = ":red[⏷]"
            else:
                sym = ""
            st.markdown(f"""
                |Stat||
                |-|-:|
                |Average| {"%.1f" % att_mean}|
                |Median| {att_median}|
                |Lowest| {lowest}|
                |Highest| {highest}|
                |Last| {last}{sym}|
            """)
        with col_2:
            # st.markdown(table_coll[TERMS["Origin"]])
            st.markdown("### Most collected")
            num, entries = [str()]*2
            for x, y in top[TERMS["Origin"]].items():
                num = x
                for z in y:
                    entries += f"{z} "
            st.markdown(f"{TERMS["Origin"]}s: {num} in {entries}")
            num, entries = [str()]*2
            for x, y in top[TERMS["Attribute"]].items():
                num = x
                for z in y:
                    entries += f"{z} "
            st.markdown(f"{TERMS["Attribute"]}s: {num} of {entries}")
            num, entries = [str()]*2
            for x, y in top[TERMS["Tool"]].items():
                num = x
                for z in y:
                    entries += f"{z} "
            st.markdown(f"{TERMS["Tool"]}s: {num} with {entries}")

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
