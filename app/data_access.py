import streamlit as st

from .file_manager import Archivist
from settings.config import TERMS, DIRECTORIES, DATAPATH


arciv = Archivist(DIRECTORIES, DATAPATH, "nofile")

class Holder:
    def __init__(self):
        pass

    @st.cache_data
    def load_main_database(_self):
        datafile = DATAPATH["main"]
        return arciv.reader(datafile, join_path="data")

    @st.cache_data
    def load_utility_database(_self):
        datafile = DATAPATH["utility"]
        return arciv.reader(datafile, join_path="data")

    @st.cache_data
    def load_progress_data(_self):
        datafile = DATAPATH["progress"]
        return arciv.reader(datafile, join_path="data")


# @st.cache_data
# def load_library():
#     return {
#         "main": load_main_database(),
#         "utility": load_utility_database(),
#         "progress": load_progress_data()
#     }


def temp():
    return
    # data analysis
    def func():
        #
        attempt_list = list()
        att_date = dict()
        success_rate = {
            "Win": 0,
            "Loss": 0,
            "Rate": 0
        }
        #
        counts = {
            TERMS["Origin"]: {},
            TERMS["Attribute"]: {},
            TERMS["utility"]: {}
        }
        for x, y in counts.items():
            for z in data_options[TERMS["main"]][x]:
                # print(x, y, z)
                counts[x][f"{z}"] = 0

        #
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

            #
        top = dict()
        # max_att, max_ori, max_utility = [0]*3
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

        #
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
        num_utility, entries_utility = count_occurrence("utility")



    # data viewer
    def data_to_df(object_database):
        rows = []

        for name, info in object_database.items():
            collected[name] = 0
            for index, details in info[TERMS["Event"]].items():
                date, idx = index.split("-")
                if object_type == "main": 
                    viewname = f"{name} C{collected[name]}"
                else:
                    viewname = name
                attempt = details[TERMS["Attempt"]] if details[TERMS["Attempt"]] else None
                source = details[TERMS["Source"]] if details[TERMS["Source"]] else None
                state = details[TERMS["State"]] if details[TERMS["State"]] else None
                rows.append({
                    "Date": date,
                    "Name": viewname,
                    "Index": idx,
                    TERMS["Attempt"]: attempt,
                    "Source": source,
                    TERMS["State"]: state
                })
                collected[name] += 1
        df = pd.DataFrame(rows)
        df = df.sort_values(["Date", "Index"], ascending=False).drop(columns=["Index", f"{TERMS["State"]}"]).fillna("")
        df[TERMS["Attempt"]] = pd.to_numeric(df[TERMS["Attempt"]], errors="coerce").astype("Int64")

        return df



    # timeline
    def tim():
        attempt_list = list()
        att_date = dict()
        for ch_data in object_database.values():
            for date, ev_data in ch_data[TERMS["Event"]].items():
                att = ev_data[TERMS["Attempt"]]
                if att: 
                    attempt_list.append(att)
                    att_date[f"{date}"] = att
                state = ev_data[TERMS["State"]]
        
        time_dict = dict()
        time_dict["date"] = list()
        time_dict["attempt"] = list()
        time_dict["name"] = list()
        collected = dict()
        def data_to_df(object_database, object_type):
            rows = []

            for name, info in object_database.items():
                collected[name] = 0
                for index, details in info[TERMS["Event"]].items():

                    date, idx = index.split("-")
                    if object_type == "main": 
                        viewname = f"{name} C{collected[name]}"
                    else:
                        viewname = name
                    attempt = details[TERMS["Attempt"]] if details[TERMS["Attempt"]] else None
                    source = details[TERMS["Source"]] if details[TERMS["Source"]] else None
                    state = details[TERMS["State"]] if details[TERMS["State"]] else None
                    thedate = "20"+ date[0:2] + "-" + date[2:4] + "-" + date[4:6]
                    fulldata = "20" + date
                    fdate = datetime.datetime.strptime(fulldata, "%Y%m%d").strftime("%Y-%m-%d")
                    rows.append({
                        "date": date,
                        "Name": viewname,
                        "Index": idx,
                        "event": attempt,
                        "Source": source,
                        TERMS["State"]: state
                    })
                    collected[name] += 1
                time_dict["date"].append(fdate)
                time_dict["attempt"].append(attempt)
                time_dict["name"].append(name)
            df = pd.DataFrame(rows)

            return time_dict