import os
import json
from pathlib import Path

import streamlit as st

from src.a_define_project import define_project
from src.b_define_labels import define_labels
from src.c_define_event_terms import define_event_terms
from src.d_define_limits import define_event_limits
from src.e_finalize import finalize
from utils import init
from utils import tools
from config import SET_WIDTH, SET_HEIGHT


def welcome(set_width, set_height):
    with st.container(border=False, key="guide", width=set_width, height=set_height, horizontal_alignment="center"):
        if not st.session_state["submitted"]["project_details"]["ui_title"]:
            st.session_state["page_incomplete"] = True
        else:
            st.session_state["page_incomplete"] = False

        st.progress(1, width="stretch")
        col_prev, col_reset, col_title, col_apply, col_next = st.columns([2, 2, 5, 2, 2])
        col_title.markdown("#### *PitySake Project Installer*", text_alignment="center")
        tools.navigate(col_prev, col_next)
        disable_reset = not any([
            st.session_state["submitted"]["project_details"]["ui_title"],
            any(st.session_state["submitted"]["project_details"].values()),
            # any(st.session_state["submitted"]["label_details"].values()),
            any(st.session_state["submitted"]["event_terms"].values()),
            any(st.session_state["submitted"]["progress_details"].values()),
        ])

        col_1, col_sp1, col_2, col_sp2, col_3 = st.columns([8, 1, 10, 1, 8])
        col_2.space("xsmall")
        col_2.markdown("""
        This wizard will guide you through creating a new project, with custimized terminology, categories and adjustments.
        """)

        
        # Form
        submission_key = "project_details"
        project_need_save = "project_need_save"
        project_is_changed = "project_is_changed"
        submission = _define_project(col_2, project_need_save, project_is_changed, submission_key)

        with col_apply:
            if not submission["template"]:
                tools.apply("project_save", project_need_save, project_is_changed, submission_key, submission)
            elif submission[["ui_title"]]:
                tools.register("register", use_template=True)

        if col_reset.button("Reset", type="primary", disabled=disable_reset, width="stretch"):
            tools.clear()
                       
        # Tips
        col_1.space("xsmall")
        with col_1.container(border=True):
            st.markdown("""
            *What can I use this for?*  
            - Register courses: track lessons and study sessions  
            - Track activity: evaluate your averages and changes over time  
            - Catalogue collections: note values and rarities of objects collected  
            - Track challenges: log attempts and outcome  
            """)
    
        col_3.space("xsmall")
        col_3.markdown("""
        Example subjects throughout the wizard: 
        - Learning path
        - Exercise 
        - Collectibles
        """)


def _define_project(col, project_need_save, project_is_changed, submission_key):
    root = Path(__file__).resolve().parent.parent
    folder_list = [x.name for x in root.iterdir() if x.is_dir()]
    col.space(1)
    col.markdown("""**New project:** enter a unique name for project files and display.""")
    col.text_input(
        "Project title", 
        key="ui_title", 
        on_change=tools.need_update,
        args=(project_need_save, project_is_changed), 
        help="Name for folder and display", 
        placeholder="e.g. Learning path / Activity log / Collection",
        label_visibility="collapsed"
    )

    if st.session_state["ui_title"]:
        project_folder = st.session_state["ui_title"].lower().replace(" ", "_")
        if project_folder in folder_list:
            st.error("A project already exists with that name.")
    
    col.markdown("""Select template setup from previously installed projects   
                 – skips further customization steps.""")
    templates = [x.name for x in Path("templates").iterdir() if x.is_dir()]
    templates.append(None)
    selected_template = col.selectbox("Templates", options=templates, label_visibility="collapsed")

    st.session_state["checklists"]["project_save"] = [st.session_state["ui_title"],]
    return {
        "ui_title": st.session_state["ui_title"],
        "template": selected_template}


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




