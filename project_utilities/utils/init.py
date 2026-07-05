import copy
import json
import streamlit as st


PAGES = 5
SET_WIDTH = 1200
INIT = {
    "initialized": False,
    "in_use": {},
    "checklists": {
        "project_save": None,
        "objects_save": None,
        "label_save": {
            "utility": None,
            "attribute": None,
            "origin": None
        },
        "event_save": None,
        "progress_save": None
    },
    "submitted": {
        "project_details": {
            "ui_title": None,
            "file_name": None,
            "template": None
        },
        "objects_details": {
            "ui_title": None,
            "main": None,
            "secondary": None,
            "utility": None,
            "attribute": None,
            "origin": None
        },
        "label_details": {
            "utility": [None,],
            "attribute": [None,],
            "origin": [None,]
        },
        "event_terms": {
            "attempt": None,
            "event": None,
            "sources_name": None,
            "state_det": None,
            "state_win": None,
            "state_loss": None
        },
        "progress_details": {
            "sources": None,
            "unit": None,
            "general_limit": None,
            "reverse_positive": None,
            "positive_value": None,
            "negative_value": None
        }
    },
    # Pages
    "page_initial_state": True,
    "page": 0,
    "page_incomplete": True,
    # Status
    "project_need_save": "secondary",
    "project_is_changed": False,
    "objects_need_save": "secondary",
    "objects_is_changed": False,
    "event_need_save": "secondary",
    "event_is_changed": False,
    "progress_need_save": "secondary",
    "progress_is_changed": False,
    "registration_complete": False,
    "error": {
        "state": False,
        "process": None,
        "file": None,
        "message": None,
        "exception": None
    },
    # Project
    "ui_title": None,
    "title_is_valid": False,
    "selected_template": None,
    # Objects
    "main": None,
    "secondary": None,
    "utility": None,
    "attribute": None,
    "origin": None,
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
    "label_attribute_multiples": False,
    "label_origin_multiples": False,
    "label_utility_multiples": False,
    "label_fields": {
        "utility": {},
        "attribute": {},
        "origin": {}
    }
}


def initialize():
    init = copy.deepcopy(INIT)
    for key, value in init.items():
        if key not in st.session_state: st.session_state[key] = value

    st.html("""
    <style>
        .st-key-guide p, li {font-weight: 300;}  
        .st-key-name_save p {font-weight: 700;}
        header {visibility: hidden;}  
    </style>
    """)

    # st.session_state["checklists"] = {
    #     "objects_save": [],
    #     "b_labels": [],
    #     "c_event": [],
    #     "d_limit": []
    # }

    st.session_state["initialized"] = True




