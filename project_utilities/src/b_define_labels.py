"""
Page B: Create labels in different categories

Guide: explain label functionality  
Example image: object registration feature 

Manages:
- Form: collect all labels within each (3) categories
"""

import streamlit as st

from utils import tools


# Step 2: name object labels
def define_labels(set_width: int|str):
    """
    (Optional) Define labels in all categories - present user info and collect details.

    Behavior:
    - next button is always enabled - non-critical info
    - disables save button unless any field is changed
    """
    
    with st.container(
            border=False, width=set_width, 
            height="stretch", horizontal_alignment="center"):
        # Header
        st.progress(40, width="stretch")
        col_prev, col_space, col_title, col_apply, col_next = st.columns(
            [2, 2, 5, 2, 2])
        tools.navigate(col_prev, col_next)
        col_title.markdown(
            "#### Object labels", text_alignment="center")
        st.space()

        # Form
        submission_key = "label_details"
        button_format_key = "label_need_save"
        is_changed_key = "label_is_changed"
        with st.container(horizontal_alignment="center"):
            submission = _name_labels(button_format_key, is_changed_key)
        with col_apply:
            if st.session_state["page_initial_state"]:
                tools.need_update(button_format_key, is_changed_key, invalid_data=True)
            tools.apply("label_save", button_format_key, is_changed_key, 
                        submission_key, submission, all_required=False)

        # Demo
        col_d1, col_d2 = st.columns(2)
        with col_d1.expander("Explanation"):
            with st.container(border=False):
                st.markdown("""
                - Each objects registered need a single label per category  
                - Labels help organize, search, and filter objects  
                - Labels are counted in statistics  
                - Special cases:  
                    - If you need cominations:  
                        e.g. labels 'A/B' for something that is both 'A' and 'B'.
                    - For objects that do not fit a category, create labels such as 'None', 
                    'Unknown' or 'Not applicable'
                    """)
        with col_d2.expander("View example", width=set_width):
            with st.container(border=False):
                st.image(
                    "../accessories/object_reg2_notes2.png", 
                    caption="""Example: Honkai Star Rail""", 
                    output_format="PNG")


def _name_labels(button_format_key: str, is_changed_key: str) -> dict:
    """
    User info and input fields for labels:  
    - Define number of labels  
    - Corresponding number of text input fields are generated   

    Args:
        button_format_key (str):
            format key, setting discrete or highlighted save button
        is_changed_key (str): 
            control key for behavior upon change

    Returns:
        (dict):
            utility, attribute, origin"""
    col_1, col_2, col_3, col_4 = st.columns(4)
    submitted_categories = st.session_state["submitted"]["objects_details"]
    
    # User info
    col_1.markdown(f"""Name labels for your categories:""")  
    col_1.markdown("""
    - Can be added or edited later
    - One single blank label will be generated if there are empty fields
    - Recommended number: 0-20 labels per category depending on length
    """)

    submitted_fields = {
        "utility": [],
        "attribute": [],
        "origin": []
    }
    
    # Input fields
    st.session_state["label_checks"] = []
    valid_list = list()
    with col_2.container(border=True):
        st.markdown(f"""##### Main & secondary objects""", text_alignment="center")
        submitted_fields["utility"], is_valid = _label_fields(
            "utility", submitted_categories["utility"], button_format_key, is_changed_key)
        valid_list.append(is_valid)
    with col_3.container(border=True):
        st.markdown("##### Main objects", text_alignment="center")
        submitted_fields["attribute"], is_valid = _label_fields(
            "attribute", submitted_categories["attribute"], button_format_key, is_changed_key)
        valid_list.append(is_valid)
    with col_4.container(border=True):
        st.markdown("##### Main objects", text_alignment="center")
        submitted_fields["origin"], is_valid = _label_fields(
            "origin", submitted_categories["origin"], button_format_key, is_changed_key)
        valid_list.append(is_valid)

    return submitted_fields


def _label_fields(group_key: str, label_name: str, button_format_key: str, is_changed_key: str):
    """
    Generate label input fields.  
    Generate error message for invalid names or duplicates.

    Args:
        group_key (str):
            key for generating unique widget key
        submitted (str):
            submitted name of the label category 

    Returns:
        (list):
            utility, attribute, origin
    """
    st.markdown(f"""Category: {label_name}""", text_alignment="center")
    label_count = st.number_input(
        "Number of labels", 
        min_value=1, 
        key=f"label_{group_key}_number"
    )
    key = f"label_{group_key}"
    keys = list()
    # Generate text input fields corresponding to selected number of labels
    validated = dict()
    for x in range(label_count):
        key_txt = f"{key}_{x + 1}"
        keys.append(key_txt)
        label = st.text_input(
            group_key, 
            key=key_txt, 
            help="", 
            on_change=tools.need_update, 
            args=(button_format_key, is_changed_key), 
            kwargs={"all_required": False,},
            placeholder="Label name", 
            label_visibility="collapsed")
        # Check label validity for filled fields, display error if needed
        if label is not None:
            if len(label) != 0:
                word_is_invalid = tools.symbol_validation(label)
                value = None if word_is_invalid else label
                validated[key_txt] = value
                if word_is_invalid: 
                    st.error(f"{word_is_invalid}")
                    tools.need_update(button_format_key, is_changed_key, invalid_data=True)
    
    label_list = list()
    # Collect valid input 
    # - 0-length or invalid are replaced by None
    # - duplicates are ignored (one single none-type is passed as an empty label)
    for key in keys:
        submitted_label = st.session_state[key]
        if submitted_label is not None:
            if len(submitted_label) == 0 or not validated[key]: 
                submitted_label = None
        if submitted_label not in label_list:
            label_list.append(submitted_label)            
        st.session_state["label_fields"][group_key][key] = submitted_label

    # Notify that there are ignored multiples
    tools.check_duplicates(st.session_state["label_fields"][group_key].values())
    return label_list, all(validated.values())

