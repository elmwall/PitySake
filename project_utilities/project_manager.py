import os
import json

import streamlit as st

from src.a_define_project import define_project
from src.b_define_labels import define_labels
from src.c_define_event_terms import define_event_terms
from src.d_define_limits import define_event_limits
from src.e_finalize import finalize
from utils import init
from utils import tools
from config import SET_WIDTH, SET_HEIGHT
# import utils.init as init
# import utils.tools as tools
# import form

with open("config_template.json", "r", encoding="utf-8") as f:
    settings = json.load(f)
# col_main, col_dev = st.columns([8, 2])


def welcome(set_width, set_height):
    with st.container(border=False, key="guide", width=set_width, height=set_height, horizontal_alignment="center"):
        st.progress(1, width="stretch")
        col_prev, col_space, col_title, col_apply, col_next = st.columns([2, 2, 5, 2, 2])
        col_title.markdown("#### Welcome to *PitySake*", text_alignment="center")
        tools.navigate(col_prev, col_next)
        disable_reset = len(st.session_state["submitted"]) == 0
        if col_apply.button("Reset", type="primary", disabled=disable_reset, width="stretch"):
            tools.clear()

        # col_title.title("Welcome to *PitySake*")

        col_1, col_2, col_3 = st.columns([1, 1, 1])
        col_2.markdown("""PitySake is a tool for tracking event-based values tied to subjects/objects you have registered in different categories. For further details: [go here](https://github.com/elmwall/PitySake).
        """)

        col_2.markdown("""
        Here you can setup a new project or collection and adapt terms, categories and values for your own needs.
                       
        Examples are included in each step and you can review your setup and associations in the final stage.
        """)


st.set_page_config(layout="wide", initial_sidebar_state="collapsed")
col_page_left, col_page_center, col_page_right = st.columns([1, 12, 1])

init.initialize()
if st.session_state["initialized"]:
    with col_page_center.container(horizontal_alignment="center"):
        if st.session_state["page"] == 0:
            welcome(SET_WIDTH, SET_HEIGHT)
        elif st.session_state["page"] == 1:
            define_project(SET_WIDTH, SET_HEIGHT)
        elif st.session_state["page"] == 2:
            define_labels(SET_WIDTH, SET_HEIGHT)
        elif st.session_state["page"] == 3:
            define_event_terms(SET_WIDTH, SET_HEIGHT)
        elif st.session_state["page"] == 4:
            define_event_limits(SET_WIDTH, SET_HEIGHT)
        elif st.session_state["page"] == 5:
            finalize(SET_WIDTH, SET_HEIGHT)
    tools.dev_tools()

