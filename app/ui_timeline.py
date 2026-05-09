import streamlit as st
import plotly.graph_objects as go

import app.data_access as hold

from settings.config import TERMS


def timeline(component_key, set_height): 
    if st.session_state["header_switch"]:
        with st.container(key=f"{component_key}_head", width="stretch", height="content"):
            st.markdown(f"##### *Timeline*", help=f"All time {TERMS["event"].lower()}s of {TERMS["main"].lower()}s. Dot color highlights {TERMS["state_win"].lower()}; line color highlights rare {TERMS["attempt"].lower()} values, good or bad.", text_alignment="left")
    fheight = 300 if set_height > 300 else set_height
    with st.container(border=True, key=f"{component_key}_main", width="stretch", height=fheight):
        object_database = hold.load_main_database()
        data = hold.process_collection_db(object_database, "main")["graph_data"]
        theme = {
            "positive": st.session_state["positive_color"],
            "neutral": st.session_state["neutral_color"],
            "negative": st.session_state["negative_color"],
            "text": st.session_state["text_color"],
            "background": st.session_state["background"],
            "subarea": st.session_state["sub_container"]
        }

        dates = data["date"]
        names = data["name"]
        value = data["attempt"]
        state = data["state"]

        fig = go.Figure()

        for i in range(len(dates)):
            if value[i] is not None: 
                if value[i] > 79:
                    hightlight_col = theme["negative"]
                elif value[i] < 50:
                    hightlight_col = theme["positive"]
                else:
                    hightlight_col = theme["text"]
                
                if state[i] is True:
                    dot_col = theme["positive"]
                elif state[i] is False:
                    dot_col = theme["negative"]
                else:
                    dot_col = theme["text"]

                # Draw line
                fig.add_trace(go.Scatter(
                    x=[dates[i], dates[i]],
                    y=[0, value[i]],
                    mode='lines',
                    line=dict(color=hightlight_col, width=1),
                    hoverlabel=dict(
                        bgcolor="rgba(0, 0, 0, 1)"
                    ),
                    showlegend=False
                ))

                # Draw dot
                fig.add_trace(go.Scatter(
                    x=[dates[i]],
                    y=[value[i]],
                    mode='markers+text',
                    hovertemplate=f"<b>{names[i]} - {value[i]}</b><br>{dates[i]}<extra></extra>",
                    marker=dict(color=dot_col, size=10, line=dict(color=theme["background"], width=2)),
                    hoverlabel=dict(
                        bgcolor="rgba(0, 0, 0, 0)"
                    ),
                    name=names[i],
                    showlegend=False
                ))

        # Axes
        fig.update_xaxes(
            tickfont_color=theme["text"],
            gridcolor='white',
        )
        fig.update_yaxes(
            zeroline=False,
            tickfont_color=theme["text"],
            gridcolor=theme["subarea"],
            range=[-5, None],
        )

        # Layout
        fig.update_layout(
            height=fheight-40,
            margin=dict(l=0, r=00, t=20, b=0),
            template="plotly_dark",
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)', 
        )

        st.plotly_chart(fig, width="stretch")
