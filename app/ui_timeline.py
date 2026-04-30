import streamlit as st
import plotly.graph_objects as go
import os
import pandas as pd
import plotly.express as px
import altair as alt
import datetime
from streamlit_timeline import st_timeline

def timeline(component_key, feature_size_left, arciv, negotiator, DATAPATH, TERMS, attempts): 
    st.space("large")
    with st.container(key=f"{component_key}_head", width="stretch", height="content"):
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

        time_dict = dict()
        time_dict["date"] = list()
        time_dict["attempt"] = list()
        time_dict["name"] = list()
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
                    thedate = "20"+ date[0:2] + "-" + date[2:4] + "-" + date[4:6]
                    # thedate = datetime.datetime(
                    #     int("20"+date[0:2]),
                    #     int(date[2:4]), 
                    #     int(date[4:6])).strftime("%Y-%m-%d")
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
                # time_dict.append({"id": f"{name} {attempt}", "content":  f"{name}", "start": f"{fdate}"})
                time_dict["date"].append(fdate)

                time_dict["attempt"].append(attempt)
                time_dict["name"].append(name)

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
        st.markdown("""
            <style>
            iframe[class^="stCustomComponentV1"], 
                iframe[class*="stCustomComponentV1"] {
                    background-color: #111111 !important; /* Din önskade bakgrund */
    
                }
                
                /* Target för containern runt om */
                div.stCustomComponentV1 {
                    background-color: #222222 !important;
                    color: black;
            }
            </style>
            """, unsafe_allow_html=True)
        # st.html("<style> .st-emotion-cache-1lf6j0f {background-color: #ffffff;}  </style>")
        # timeline = st_timeline(data, groups=[], options={}, height="300px", key="timel")
        # st.subheader("Selected item")
        # st.write(timeline)
        # Data
        dates = pd.to_datetime(time_dict["date"])
        names = time_dict["name"]
        value = time_dict["attempt"]
        # Exempeldata
        data = {
            'Datum': pd.to_datetime(['2025-01-10', '2025-01-15', '2025-02-05', '2025-02-20']),
            'Objekt': ['Server A', 'Databas B', 'Server A', 'Webb C'],
            'Värde': [15, 25, 10, 30]
        }
        df = pd.DataFrame(data)

        fig = go.Figure()

        # print("dates", dates)
        # print("names", names)
        # print("value", value)
        for i in range(len(dates)):
            # print(dates[i], names[i], value[i])
            # Rita "pinnen"
            fig.add_trace(go.Scatter(
                x=[dates[i], dates[i]],
                y=[0, value[i]],
                mode='lines',
                line=dict(color="#27A82D", width=1),
                hoverlabel=dict(
                    bgcolor="rgba(0, 0, 0, 1)"
                ),
                showlegend=False
            ))
            # Rita "huvudet" (punkten)
            fig.add_trace(go.Scatter(
                x=[dates[i]],
                y=[value[i]],
                mode='markers+text',
                hovertemplate=f"<b>{names[i]} - {value[i]}</b><br>{dates[i].strftime("%Y-%m-%d")}<extra></extra>",
                marker=dict(color="blue", size=10, line=dict(color='MediumPurple', width=2)),
                hoverlabel=dict(
                    bgcolor="rgba(0, 0, 0, 0)"
                ),
                name=names[i],
                showlegend=False
            ))
            # fig.add_annotation(
            #     x=dates[i],
            #     y=value[i],
            #     text=names[i],
            #     showarrow=False,
            #     textangle=-90,
            #     xanchor="center",
            #     yanchor="bottom",
            #     xshift=0,
            #     yshift=0,
            #     font=dict(color="white", size=11)
            # )

        fig.update_layout(
            height=200,
            margin=dict(l=0, r=00, t=0, b=0),
            template="plotly_dark", # Anpassa efter ditt tema
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            
        )

        st.plotly_chart(fig, width="stretch")

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