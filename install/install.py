import os
import json

import streamlit as st

from src.a_define_project import define_project
from src.b_define_labels import define_labels
from src.c_define_event_terms import define_event_terms
from src.d_define_limits import define_event_limits
import utils.init as init
import utils.tools as tools
from config import SET_WIDTH, SET_HEIGHT
# import form


with open("config_template.json", "r", encoding="utf-8") as f:
    settings = json.load(f)
# col_main, col_dev = st.columns([8, 2])


def welcome(set_width, set_height):
    with st.container(border=False, key="guide", width=set_width, height=set_height, horizontal_alignment="center"):
        col_prev, col_space, col_title, col_apply, col_next = st.columns([2, 2, 5, 2, 2])
        col_title.markdown("#### Welcome to *PitySake*", text_alignment="center")

        tools.navigate(col_prev, col_next, page=1)
        # col_title.title("Welcome to *PitySake*")

        st.markdown("PitySake is a tool for tracking events or progress tied to a set of subjects.")

        st.markdown("""
        Here you can setup a new project or collection and adapt terms, categories and values for your own needs.
        """)
        st.write("test")

        # return 

# st.sidebar.title("dsfsdf")
st.set_page_config(layout="wide", initial_sidebar_state="collapsed")
col_page_left, col_page_center, col_page_right = st.columns([1, 12, 1])

# with open("config_template.json", "r", encoding="utf-8") as f:
#     settings = json.load(f)

# pages = [
#     st.Page("pages/1_welcome.py", title="Welcome to PitySake")
# ]
# pg = st.navigation(pages)

# if "initialized" not in st.session_state:
init.initialize()
if st.session_state["initialized"]:
    with col_page_center.container(horizontal_alignment="center"):
        if st.session_state["page"] == 0:
            # pass
            welcome(SET_WIDTH, SET_HEIGHT)
        elif st.session_state["page"] == 1:
            define_project(SET_WIDTH, SET_HEIGHT)
        elif st.session_state["page"] == 2:
            define_labels(SET_WIDTH, SET_HEIGHT)
        elif st.session_state["page"] == 3:
            define_event_terms(SET_WIDTH, SET_HEIGHT)
        elif st.session_state["page"] == 4:
            define_event_limits(SET_WIDTH, SET_HEIGHT)
    # with col_page_left:
        # pass
    tools.dev_tools()
#     pg.run()
    # if info_page.welcome():
    # form.run_form(settings)

