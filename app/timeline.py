"""
Timeline of main object events and progress

Manages
- identifying fail/success states and values beyond highlight limits and sets color
- renders timeline graph according to style and highlights
- graph x: date, y: progress value, dots: events of main objects
"""

import logging

import streamlit as st
import plotly.graph_objects as go

import app.data_access as hold


TERMS = st.session_state["TERMS"]
logger = logging.getLogger(__name__)


def timeline(component_key: str, set_height: int): 
    """
    Renders timeline of main objects based on processed data from data_access.
    """
    logger.info("Running")

    # Feature header
    if st.session_state["header_switch"]:
        with st.container(key=f"{component_key}_head", width="stretch", height="content"):
            help_text = f"""All {TERMS["event"].lower()}s of {TERMS["main"].lower()}s.  
                Dot color highlights {TERMS["state_win"].lower()};  
                Line color highlights rare {TERMS["attempt"].lower()} values, good or bad."""
            st.markdown(f"##### *Timeline*", help=help_text, text_alignment="left")
    fheight = 300 if set_height > 300 else set_height

    # Main container
    with st.container(border=True, key=f"{component_key}_main", width="stretch", height=fheight):
        object_database = hold.load_main_database()
        data = hold.process_collection_db(object_database, "main")["graph_data"]
        
        # Settings: adapted theme; values for date, name, progress, and state
        theme = {
            "positive": st.session_state["positive_color"],
            "neutral": st.session_state["neutral_color"],
            "negative": st.session_state["negative_color"],
            "text": st.session_state["text_color"],
            "background": st.session_state["background"],
            "subarea": st.session_state["sub_container"]
        }
        options = hold.load_options()
        dates = data["date"]
        names = data["name"]
        value = data["attempt"]
        state = data["state"]

        fig = go.Figure()
        # Set highlights for high/low depending on project settings
        if options["user_indicators"]["reverse_positive"]:
            high_color = theme["negative"]
            low_color = theme["positive"]
        else:
            high_color = theme["positive"]
            low_color = theme["negative"]
        for i in range(len(dates)):
            if value[i] is not None: 
                    
                if value[i] > options["user_indicators"]["high_highlight"]:
                    hightlight_col = high_color
                elif value[i] < options["user_indicators"]["low_highligh"]:
                    hightlight_col = low_color
                else:
                    hightlight_col = theme["neutral"]
                
                if state[i] is True:
                    dot_col = theme["positive"]
                elif state[i] is False:
                    dot_col = theme["negative"]
                else:
                    dot_col = theme["neutral"]

                # Draw line
                fig.add_trace(
                    go.Scatter(
                        x=[dates[i], dates[i]], y=[0, value[i]], mode='lines',
                        line=dict(color=hightlight_col, width=1),
                        hoverlabel=dict(bgcolor="rgba(0, 0, 0, 1)"),
                        showlegend=False))

                # Draw dot
                fig.add_trace(
                    go.Scatter(
                        x=[dates[i]], y=[value[i]], mode='markers+text',
                        hovertemplate=f"<b>{names[i]}: {value[i]}</b><br>{dates[i]}<extra></extra>",
                        marker=dict(
                            color=dot_col, size=10, 
                            line=dict(color=theme["background"], width=2)),
                        hoverlabel=dict(bgcolor="rgba(0, 0, 0, 0)"),
                        name=names[i], showlegend=False))

        # Axes
        fig.update_xaxes(
            tickfont_color=theme["text"], gridcolor='white')
        fig.update_yaxes(
            zeroline=False, tickfont_color=theme["text"],
            gridcolor=theme["subarea"], range=[-5, None])
        if TERMS["unit"]:
            fig.update_yaxes(
                title=f"{TERMS["unit"]} {TERMS["attempt"]}", 
                title_font_color=theme["text"])

        # Layout
        fig.update_layout(
            height=fheight-40, margin=dict(l=0, r=00, t=20, b=0), template="plotly_dark", 
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')

        # Build graph
        st.plotly_chart(fig, width="stretch")
