import json
import streamlit as st



INIT = {
    "initialized": False,
    # Page
    "page": 0,
    # Form
    "submitted": dict(),
    # Names
    "ui_title": None,
    "main": None,
    "secondary": None,
    "utility": None,
    "attribute": None,
    "origin": None,
    "project_need_save": "secondary",
    "project_is_changed": False,
    "event_need_save": "secondary",
    "event_is_changed": False,
    "limits_need_save": "secondary",
    "limits_is_changed": False,
    # Labels
    "label_1_number": 1,
    "label_2_number": 1,
    "label_3_number": 1,
    "label_utility_1": None,
    "label_attribute_1": None,
    "label_origin_1": None,
    "label_utility": None,
    "label_attribute": None,
    "label_origin": None,
    "label_need_save": "secondary",
    "label_is_changed": False,
}

def initialize():
    for key, value in INIT.items():
        if key not in st.session_state: st.session_state[key] = value

    st.html("""
    <style>
        .st-key-guide p, li {font-weight: 300;}  
        .st-key-name_save p {font-weight: 700;}
        header {visibility: hidden;}  
    </style>
    """)

    st.session_state["initialized"] = True
    get_config_template()


@st.cache_data
def get_config_template():
    with open("config_template.json", "r", encoding="utf-8") as f:
        return json.load(f)



