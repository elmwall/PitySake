"""
Page A: Object name and label category form

Guide: 
- Explain object differences and label use
- Explain object counting (from 0 or 1 and up)
- Example image: object registration feature 

Manages:
- Form: object and label categories
"""

from copy import deepcopy 

import streamlit as st

from utils import tools


# Step 1: name objects and label categories
def define_objects(set_width: int|str):
    """
    Object and label categories - present user info and collect details.

    Behavior:
    - disables save button until all fields are filled, re-enables if a field is changed
    - disables next button until first save
    """
    with st.container(
            border=False, width=set_width, 
            height="stretch", horizontal_alignment="center"):
        check_status = deepcopy(st.session_state["submitted"]["objects_details"])
        if "start_from_0" in check_status: check_status.pop("start_from_0")
        if not all(check_status.values()):
            st.session_state["page_incomplete"] = True
        else:
            st.session_state["page_incomplete"] = False

        # Header
        st.progress(20, width="stretch")
        col_prev, col_space, col_title, col_apply, col_next = st.columns(
            [2, 2, 5, 2, 2])
        tools.navigate(col_prev, col_next)
        col_title.markdown(
            "#### Naming your project and collections", 
            text_alignment="center")
        st.space()

        # Form
        submission_key = "objects_details"
        button_format_key = "objects_need_save"
        is_changed_key = "objects_is_changed"
        with st.container(horizontal_alignment="center"):
            submission = _name_objects(button_format_key, is_changed_key)
        with col_apply:
            tools.apply("objects_save", button_format_key, is_changed_key, submission_key, submission)

        # Demo
        col_d1, col_d2 = st.columns(2)
        with col_d1.expander("Explanation"):
            with st.container(border=False):
                st.markdown("""
                ##### Main and secondary objects  
                Objects are the items or subjects you want to track. Events associate them with a date with a value and evaluation.  
                - Main objects support detailed anaysis and statistics  
                - Secondary are tracked separately with reduced detail  
                - Main and secondary are viewed in separate tables: 
                    - history of events  
                    - collection of objects
                - Both contribute to overall totals and evaluations""")
                st.space(1)
                st.markdown("""
                ##### Collection count    
                How multiples of the same object is counted.  
                - Enabled will count how many times *new* objects of the same have been received.  
                - Disabled will show the true count of the object.""")
                st.space(1)
                st.markdown("""
                ##### Labels   
                Object details for further categorization.  
                - Useful for sorting and searching tables  
                - Occurrences are included in statistics""")
        with col_d2.expander("View example", width=set_width):
            with st.container(border=False):
                st.image(
                    "../accessories/object_reg2_notes.png", 
                    caption="""**Main objects** have three groups of labels.  
                    Example: Honkai Star Rail""", 
                    output_format="PNG")
                st.image(
                    "../accessories/tab_notes2.png", 
                    caption="""Object counts can start at 0 or 1.""", 
                    output_format="PNG")


def _name_objects(button_format_key: str, is_changed_key: str) -> dict:
    """
    User info and input fields for object and label category names.  
    Generate error message for invalid names.

    Args:
        button_format_key (str):
            format key, setting discrete or highlighted save button
        is_changed_key (str): 
            control key for behavior upon change

    Returns:
        (dict):
            main, secondary, start_from_0, utility, attribute, origin"""
    col_1, col_2, col_3 = st.columns([1, 1.5, 1.5])

    # User info
    col_1.markdown("Define the names used in your project.")
    col_1.markdown("""
        - **Main objects:** your primary tracked item
        - **Secondary objects:** additional tracked item
    """)
    col_1.markdown("""
        - **Collection count start at 0:** if enabled, the first event of an object counts as '0', 
        otherwise it counts from 1
    """)
    col_1.markdown("""
        - **Labels:** categories for sorting and searchability 
    """)

    # Input fields
    # - Main and secondary objects
    with col_2.container(border=True, height="stretch"):
        st.markdown("##### Objects", text_alignment="center")
        help_primary = """
            Actual objects for each suggestion could e.g. be:  
            - (learning: course) Python Fundamentals
            - (activity: workout) 5K Running Plan
            - (collection: figure) Obsidian figurine
        """
        help_secondary = """
            Use for less complex or non-priority  
            objects which you still want to record,  
            or things you want tracked separately.
        """
        st.text_input(
            "Main object", 
            key="main", 
            on_change=tools.need_update, 
            args=(button_format_key, is_changed_key), 
            help=help_primary, 
            placeholder="e.g. Course / Workout / Collectible")
        st.text_input(
            "Secondary object", 
            key="secondary", 
            on_change=tools.need_update, 
            args=(button_format_key, is_changed_key), 
            help=help_secondary,
            placeholder="e.g. Tutorial / Walk / Accessory")
        st.checkbox("Start object collection count at 0", value=True, key="start_from_0")

    # - Label categories
    # The keys "utilit", "attribute", "origin" are placeholder names 
    # "utility" represents shared label, otherwise no functional difference between them
    with col_3.container(border=True, height="stretch"):
        st.markdown("##### Object label categories", text_alignment="center")
        st.text_input(
            "1. Label for main and secondary objects", 
            key="utility", 
            on_change=tools.need_update, 
            args=(button_format_key, is_changed_key), 
            help="Use a broad label which can apply to both object types",
            placeholder="e.g. Topic / Effort / Series")
        st.text_input(
            "2. Label for main object", 
            key="attribute", 
            on_change=tools.need_update, 
            args=(button_format_key, is_changed_key), 
            placeholder="e.g. Platform / Activity type / Manufacturer")
        st.text_input(
            "3. Label for main object", 
            key="origin", 
            on_change=tools.need_update, 
            args=(button_format_key, is_changed_key), 
            placeholder="e.g. Examination / Muscle group / Scale")

    # Word validation
    validated = dict()
    ref = {
        "main": "main object",
        "secondary": "secondary object",
        "utility": "label 1",
        "attribute": "label 2",
        "origin": "label 3"
    }
    for x in ref.keys():
        word_is_invalid = tools.symbol_validation(st.session_state[x])
        value = None if word_is_invalid else st.session_state[x]
        validated[x] = value
        if word_is_invalid: 
            if x in ["main", "secondary"]:
                col_2.error(f"{ref[x].capitalize()}: {word_is_invalid}")
            else:
                col_3.error(f"{ref[x].capitalize()}: {word_is_invalid}")

    # Checklist for enabling save
    st.session_state["checklists"]["objects_save"] = [
        validated["main"],
        validated["secondary"],
        validated["utility"],
        validated["attribute"],
        validated["origin"],
    ]
    # Send preliminary submission from current info
    return {
        "main": st.session_state["main"],
        "secondary": st.session_state["secondary"],
        "start_from_0": st.session_state["start_from_0"],
        "utility": st.session_state["utility"],
        "attribute": st.session_state["attribute"],
        "origin": st.session_state["origin"]
    }

    