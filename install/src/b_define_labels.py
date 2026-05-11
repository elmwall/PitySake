import json
import streamlit as st

import utils.tools as tools
# from utils.init import get_config_template as contem


# with open("config_template.json", "r", encoding="utf-8") as f:
#     settings = json.load(f)


def run_define_labels(set_width, set_heigth):
    with st.container(border=False, key="guide", width=set_width, height="stretch", horizontal_alignment="center"):
        with st.container(horizontal_alignment="center"):
            _name_labels()
    with st.expander("View example", width=set_width):
        col_1, col_2 = st.columns(2)

        # TODO: image of data view search
        col_1.image("sample_obj.png", caption="**Main objects** has three group of labels.", output_format="PNG")
        col_2.image("sample_obj.png", caption="**Secondary objects** only has the the first label group.", output_format="PNG")


def _apply(key, need_save, is_changed, submission_key, submission):
    st.button(
        "Save", 
        key=key, 
        on_click=tools.submit, 
        args=(need_save, is_changed, submission_key, submission), 
        type=st.session_state[need_save], 
        disabled=st.session_state[is_changed],
        width="stretch"
    )


def _name_labels():
    col_prev, col_space, col_title, col_apply, col_next = st.columns([2, 2, 5, 2, 2])
    tools.navigate(col_prev, col_next, page=2)
    label_need_save, label_is_changed = "label_need_save", "label_is_changed"

    col_title.markdown("#### Labels", text_alignment="center")
    col_info, col_requirements, col_sp = st.columns(3)
    col_info.markdown("""
        Name options for labeling objects.  
                      
        For a "none" or combined label, create such named e.g. 'None', 'Unknown', 'First/Second'.  
        
        The fields expand with the number of labels.  
        Optimal number: 1-12
    """)
    col_requirements.markdown("""
        - Name at least one option in each category
        - Options added here cannot be removed  
        - More can be added later.        
    """)
    col_2, col_3, col_4 = st.columns(3)
    
    label_keys = list()
    with col_2.container(border=True):
        st.markdown("##### 1. Main/secondary label", text_alignment="center")
        label1_count = st.number_input(
            "Number of labels", 
            min_value=1, 
            key="label_1_number"
        )
        key = "label_utility"
        for x in range(label1_count):
            key_txt = f"{key}_{x + 1}"
            label_keys.append(key_txt)
            st.text_input(
                "Utility", 
                key=key_txt, 
                on_change=tools.need_update, 
                args=(label_need_save, label_is_changed), 
                help="", 
                placeholder="Label name", 
                label_visibility="collapsed"
            )

    with col_3.container(border=True):
        st.markdown("##### 2. Main label", text_alignment="center")
        label2_count = st.number_input(
            "Number of labels", 
            min_value=1, 
            key="label_2_number"
        )
        key = "label_attribute"
        for x in range(label2_count):
            key_txt = f"{key}_{x + 1}"
            label_keys.append(key_txt)
            st.text_input(
                "Attribute", 
                key=key_txt, 
                on_change=tools.need_update, 
                args=(label_need_save, label_is_changed), 
                help="", 
                placeholder="Label name", 
                label_visibility="collapsed"
            )

    with col_4.container(border=True):
        st.markdown("##### 3. Main label", text_alignment="center")
        label3_count = st.number_input(
            "Number of labels", 
            min_value=1, 
            key="label_3_number"
        )
        key = "label_origin"
        for x in range(label3_count):
            key_txt = f"{key}_{x + 1}"
            label_keys.append(key_txt)
            st.text_input(
                "Origin", 
                key=key_txt, 
                on_change=tools.need_update, 
                args=(label_need_save, label_is_changed), 
                help="", 
                placeholder="Label name", 
                label_visibility="collapsed"
            )


        
    submission_key = "label_names"
    submission = {submission_key: {}}
    for x in label_keys:
        submission[submission_key][x] = st.session_state[x]

    with col_apply:
        _apply("label_save", "label_need_save", "label_is_changed", submission_key, submission)


# if __name__ == "__main__":
#     run_form(settings)