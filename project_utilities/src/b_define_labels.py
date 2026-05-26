import json
import streamlit as st

import utils.tools as tools


# Step 2: name object labels
def define_labels(set_width, set_heigth):
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
        label_need_save = "label_need_save"
        label_is_changed = "label_is_changed"
        with st.container(horizontal_alignment="center"):
            submission = _name_labels(label_need_save, label_is_changed, submission_key)
        with col_apply:
            tools.apply("label_save", label_need_save, label_is_changed, submission_key, submission)

    # Demo
    with st.expander("View example", width=set_width):
        col_1, col_2 = st.columns(2)
        col_1.image(
            "images/sample_obj.png", 
            caption="**Main objects** has three group of labels.", 
            output_format="PNG")
        col_2.image(
            "images/sample_obj.png", 
            caption="**Secondary objects** only has the the first label group.", 
            output_format="PNG")


# def _apply(key, need_save, is_changed, submission_key, submission):
#     st.button(
#         "Save", 
#         key=key, 
#         on_click=tools.submit, 
#         args=(need_save, is_changed, submission_key, submission), 
#         type=st.session_state[need_save], 
#         disabled=st.session_state[is_changed],
#         width="stretch"
#     )


def _name_labels(label_need_save, label_is_changed, submission_key):
    col_1, col_2, col_3, col_4 = st.columns(4)
    col_1.markdown("""
        **Name labels under your three categories:** 1, 2, 3  
                      
    """)
    col_1.markdown("""
        If you save without adding any, each category will have a blank label, which you can change later or add others.
                      
        Objects need one label per category; for combined labels, create such e.g. 'First/Second'.
        

    """)
    col_1.markdown("""
        The fields expand with the number of labels.  
        Optimal number: 1-12     
    """)
    
    submission = {
        "utility": [],
        "attribute": [],
        "origin": []
    }
    with col_2.container(border=True):
        st.markdown("##### 1. Main/secondary label", text_alignment="center")
        label1_count = st.number_input(
            "Number of labels", 
            min_value=1, 
            key="label_1_number"
        )
        key = "label_utility"
        utility_keys = list()
        for x in range(label1_count):
            key_txt = f"{key}_{x + 1}"
            utility_keys.append(key_txt)
            st.text_input(
                "Utility", 
                key=key_txt, 
                help="", 
                on_change=tools.need_update, 
                args=(label_need_save, label_is_changed), 
                placeholder="Label name", 
                label_visibility="collapsed"
            )
        for x in utility_keys:
            submission["utility"].append(st.session_state[x])

    with col_3.container(border=True):
        st.markdown("##### 2. Main label", text_alignment="center")
        label2_count = st.number_input(
            "Number of labels", 
            min_value=1, 
            key="label_2_number"
        )
        key = "label_attribute"
        attribute_keys = list()
        for x in range(label2_count):
            key_txt = f"{key}_{x + 1}"
            attribute_keys.append(key_txt)
            st.text_input(
                "Attribute", 
                key=key_txt, 
                help="", 
                on_change=tools.need_update, 
                args=(label_need_save, label_is_changed), 
                placeholder="Label name", 
                label_visibility="collapsed"
            )
        for x in attribute_keys:
            submission["attribute"].append(st.session_state[x])

    with col_4.container(border=True):
        st.markdown("##### 3. Main label", text_alignment="center")
        label3_count = st.number_input(
            "Number of labels", 
            min_value=1, 
            key="label_3_number"
        )
        key = "label_origin"
        origin_keys = list()
        for x in range(label3_count):
            key_txt = f"{key}_{x + 1}"
            origin_keys.append(key_txt)
            st.text_input(
                "Origin", 
                key=key_txt, 
                help="", 
                on_change=tools.need_update, 
                args=(label_need_save, label_is_changed), 
                placeholder="Label name", 
                label_visibility="collapsed"
            )
        for x in origin_keys:
            submission["origin"].append(st.session_state[x])
    
    return submission

