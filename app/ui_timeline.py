import streamlit as st
import os
import pandas as pd
import plotly.express as px
import altair as alt
import datetime
from streamlit_timeline import st_timeline

def timeline(component_key, feature_size_left, arciv, negotiator, DATAPATH, TERMS, attempts): 
    st.space("large")
    with st.container(key=f"{component_key}_head", width=feature_size_left, height="content"):
        st.markdown(f"##### *Timeline*", text_alignment="left")
    with st.container(border=True, key=f"{component_key}_main", width="stretch", height="stretch"):
        def collect_data(reference):
            # for x in ["Character", "Tool"]
            data_reference = TERMS[reference]
            datafile = DATAPATH[data_reference]
            # files = [DATAPATH["CharReport"], DATAPATH["ToolReport"]]

            object_database = arciv.reader(datafile, join_path="data")

            return object_database
        
        object_database = collect_data("Character")
        attempt_list = list()
        att_date = dict()
        for ch_data in object_database.values():
            for date, ev_data in ch_data[TERMS["Event"]].items():
                att = ev_data[TERMS["Attempt"]]
                if att: 
                    attempt_list.append(att)
                    att_date[f"{date}"] = att
                state = ev_data[TERMS["State"]]
        # print(att_date)

        time_dict = list()
        collected = dict()
        # print(object_type, 3)
        def data_to_df(object_database, object_type):
            rows = []

            for name, info in object_database.items():
                collected[name] = 0
                # attempts = dict()
                # pulls = info.get("Pull", {})
                for index, details in info[TERMS["Event"]].items():
                    date, idx = index.split("-")
                    if object_type == "Character": 
                        viewname = f"{name} C{collected[name]}"
                    else:
                        viewname = name
                    # attempt, source, state = ["-"]*3
                    attempt = details[TERMS["Attempt"]] if details[TERMS["Attempt"]] else None
                    source = details[TERMS["Source"]] if details[TERMS["Source"]] else None
                    state = details[TERMS["State"]] if details[TERMS["State"]] else None
                    # date = datetime.datetime(
                    #     int("20"+date[0:2]),
                    #     int(date[2:4]), 
                    #     int(date[4:6]))
                    # date = "20240202"
                    # print("here")
                    # print("20"+date, date)
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
                time_dict.append({"id": f"{name}", "content":  f"{name}", "start": f"{fdate}", "title": f"{attempt}"})
                # print(date)
            df = pd.DataFrame(rows)

            # df["Date"] = pd.to_datetime(df["Date"], format="%y%m%d")
            # df = df.sort_values(["Date", "Index"], ascending=False).drop(columns=["Index", f"{TERMS["State"]}"]).fillna("")
            # df[TERMS["Attempt"]] = pd.to_numeric(df[TERMS["Attempt"]], errors="coerce").astype("Int64")
            
            # df_display = df.copy()
            # df.style.set_properties(subset=[TERMS["Attempt"]], **{"text-align": "right"})
            return time_dict
        


        data = data_to_df(object_database, "Character")
        # print(df)



        st.set_page_config(layout="wide")
        # print(data)
        # items = [
        #     {"id": 1, "content": "2022-10-20", "start": "2022-10-20"},
        #     {"id": 2, "content": "2022-10-09", "start": "2022-10-09"},
        #     {"id": 3, "content": "2022-10-18", "start": "2022-10-18"},
        #     {"id": 4, "content": "2022-10-16", "start": "2022-10-16"},
        #     {"id": 5, "content": "2022-10-25", "start": "2022-10-25"},
        #     {"id": 6, "content": "2022-10-27", "start": "2022-10-27"},
        # ]

        timeline = st_timeline(data, groups=[], options={}, height="300px")
        st.subheader("Selected item")
        st.write(timeline)
        # data = pd.DataFrame({
        #     'date': ['2023-01-01', '2023-03-01', '2023-06-01', '2023-09-01'],
        #     'event': ['Start', 'Milestone A', 'Milestone B', 'End'],
        #     'y_pos': [0, 0, 0, 0] # All dots on the same y-position
        # })

        # # 2. Create the Altair Chart
        # chart = alt.Chart(data).mark_line(
        #     point=True, # Adds dots to the line
        #     color='blue'
        # ).encode(
        #     x='date', # T for Time
        #     y=alt.Y('y_pos', axis=None), # Hide the Y-axis
        #     tooltip=['date', 'event'] # Optional: Show info on hover
        # ).properties(
        #     height=100 # Keep the height small to make it look like a timeline
        # )

        # # 3. Display in Streamlit
        # st.title("Simple Timeline")
        # st.altair_chart(chart)

        # fig = px.line(df, x="Date", y=TERMS["Attempt"], markers=True)
        # fig.update_traces(mode="lines+markers", line=dict(color="blue", width=2), marker=dict(size=10))
        # st.plotly_chart(fig)