import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import datetime

from .data_access import Holder

from settings.config import TERMS


def timeline(component_key): 
    hold = Holder()
    # st.space("xsmall")
    with st.container(key=f"{component_key}_head", height="content"):
        st.markdown(f"##### *Timeline*", text_alignment="left")
    with st.container(border=True, key=f"{component_key}_main", width="stretch", height="stretch"):
        
        object_database = hold.load_main_database()
        attempt_list = list()
        att_date = dict()
        for main_data in object_database.values():
            for date, ev_data in main_data[TERMS["event"]].items():
                att = ev_data[TERMS["attempt"]]
                if att: 
                    attempt_list.append(att)
                    att_date[f"{date}"] = att
                state = ev_data[TERMS["state"]]

        time_dict = dict()
        time_dict["date"] = list()
        time_dict["attempt"] = list()
        time_dict["name"] = list()
        collected = dict()
        def data_to_df(object_database, object_type):
            rows = []

            for name, info in object_database.items():
                collected[name] = 0
                for index, details in info[TERMS["event"]].items():

                    date, idx = index.split("-")
                    if object_type == "Character": 
                        viewname = f"{name} C{collected[name]}"
                    else:
                        viewname = name
                    attempt = details[TERMS["attempt"]] if details[TERMS["attempt"]] else None
                    source = details[TERMS["source"]] if details[TERMS["source"]] else None
                    state = details[TERMS["state"]] if details[TERMS["state"]] else None
                    thedate = "20"+ date[0:2] + "-" + date[2:4] + "-" + date[4:6]
                    fulldata = "20" + date
                    fdate = datetime.datetime.strptime(fulldata, "%Y%m%d").strftime("%Y-%m-%d")
                    rows.append({
                        "date": date,
                        "Name": viewname,
                        "Index": idx,
                        "event": attempt,
                        "source": source,
                        TERMS["state"]: state
                    })
                    collected[name] += 1
                time_dict["date"].append(fdate)
                time_dict["attempt"].append(attempt)
                time_dict["name"].append(name)
            df = pd.DataFrame(rows)

            return time_dict
 
        data = data_to_df(object_database, TERMS["main"].capitalize())
        # st.set_page_config(layout="wide")


        dates = pd.to_datetime(time_dict["date"])
        names = time_dict["name"]
        value = time_dict["attempt"]

        fig = go.Figure()

        for i in range(len(dates)):
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

        fig.update_layout(
            height=230,
            margin=dict(l=0, r=00, t=20, b=0),
            template="plotly_dark",
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            
        )

        st.plotly_chart(fig, width="stretch")
