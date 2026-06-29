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

from app.initialize import TERMS
import app.data_access as hold


main_ref = TERMS["main"]
secondary_ref = TERMS["secondary"]
attempt_ref = TERMS["attempt"]
unit_ref = TERMS["unit"]
logger = logging.getLogger(__name__)


def timeline(component_key: str, set_height: int): 
    """
    Renders timeline of main objects based on processed data from data_access.
    """
    logger.info("Running")

    # Feature header
    if st.session_state["header_switch"]:
        with st.container(key=f"{component_key}_head", width="stretch", height="content"):
            help_text = f"""Timeline of events  
                - {main_ref}s with (○) or without (Δ) {attempt_ref}   
                - {secondary_ref}s with (□) or without (∇) {attempt_ref}    
                - Fill color highlights outcomes {TERMS["state_win"]} or {TERMS["state_loss"]}  
                - Line color highlights rare {attempt_ref} values"""
            st.markdown(f"##### *Timeline*", help=help_text, text_alignment="left")
    fheight = 300
    if set_height:
        if set_height < 300: 
            fheight = set_height

    # Main container
    with st.container(border=True, key=f"{component_key}_main", width="stretch", height=fheight):
        main_database = hold.load_main_database()
        secondary_database = hold.load_secondary_database()
        main_data = hold.process_main_db(main_database)["graph_data"]
        secondary_data = hold.process_secondary_db(secondary_database)["graph_data"]
        data = dict()
        for x in main_data.keys():
            data[x] = main_data[x] + secondary_data[x]
        
        # Settings: adapted theme; values for date, name, progress, and state
        positive_color = st.session_state["positive_color"]
        neutral_color = st.session_state["neutral_color"]
        negative_color = st.session_state["negative_color"]
        text_color = st.session_state["text_color"]
        background = st.session_state["background"]
        lines = st.session_state["input_field"]
        highlight = data["highlight"]

        options = hold.load_options()
        dates = data["date"]
        names = data["name"]
        value = data["attempt"]

        fig = go.Figure()
        # Set highlights for high/low depending on project settings
        if options:
            use_highlights = options["user_indicators"]["use_highlights"]
            if options["user_indicators"]["reverse_positive"]:
                high_color = negative_color
                low_color = positive_color
            else:
                high_color = positive_color
                low_color = negative_color
        else:
            use_highlights = True
            high_color, low_color = None, None
        
        for i in range(len(dates)):
            if value[i] is not None: 
                if use_highlights:
                    if highlight[i] is True:
                        hightlight_col = high_color
                    elif highlight[i] is False:
                        hightlight_col = low_color
                    elif highlight[i] is None:
                        hightlight_col = neutral_color
                else:
                    hightlight_col = neutral_color
                
                if data["state"][i] is True:
                    dot_col = positive_color
                elif data["state"][i] is False:
                    dot_col = negative_color
                else:
                    dot_col = neutral_color

                # Draw line
                fig.add_trace(
                    go.Scatter(
                        x=[dates[i], dates[i]], y=[0, value[i]], mode='lines',
                        line=dict(color=hightlight_col, width=1),
                        hoverlabel=dict(bgcolor="rgba(0, 0, 0, 1)"),
                        showlegend=False))
                
                if data["type"][i] == "main":
                    base_symbol = "circle" 
                    symbol_angle = 0
                else: 
                    base_symbol = "square"
                    symbol_angle = 180

                if data["attempt_made"][i]:
                    symbol_shape = base_symbol
                    symbol_size = 10
                    display_value = value[i]
                else: 
                    symbol_shape = "arrow"
                    symbol_size = 14
                    display_value = ""

                # Draw dot
                fig.add_trace(
                    go.Scatter(
                        x=[dates[i]], y=[value[i]], mode='markers+text',
                        hovertemplate=f"<b>{names[i]}: {display_value}</b><br>{dates[i]}<extra></extra>",
                        marker=dict(
                            color=dot_col, size=symbol_size, symbol=symbol_shape, angle=symbol_angle,
                            line=dict(color=background, width=1.7)),
                        hoverlabel=dict(bgcolor="rgba(0, 0, 0, 0)"),
                        name=names[i], showlegend=False))

        # Axes
        fig.update_xaxes(
            tickfont_color=text_color, gridcolor='white',
            tickformatstops = [
                dict(dtickrange=[None, 86400000], value="%b %d, %Y")
            ])
        fig.update_yaxes(
            zeroline=False, tickfont_color=text_color,
            gridcolor=lines, range=[-5, None])
        if unit_ref:
            fig.update_yaxes(
                title=f"{unit_ref} {attempt_ref}", 
                title_font_color=text_color)

        # Layout
        fig.update_layout(
            height=fheight-40, margin=dict(l=0, r=00, t=20, b=0), template="plotly_dark", 
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')

        # Build graph
        st.plotly_chart(fig, width="stretch")
