import json
import streamlit as st

from utils import tools


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
            tools.apply("label_save", label_need_save, label_is_changed, 
                        submission_key, submission, all_required=False)

        # Demo
        col_d1, col_d2 = st.columns(2)
        with col_d1.expander("Explanation"):
            with st.container(border=False, height=300):
                st.markdown("""
                - Each objects registered need a single label per category  
                - Labels help organize, search, and filter objects  
                - Labels are counted in statistics  
                - Special cases:  
                    - If you need cominations:  
                        e.g. labels 'A/B' for something that is both 'A' and 'B'.
                    - For objects that do not fit a category, create labels such as 'None', 'Unknown' or 'Not applicable'
                    """)
        with col_d2.expander("View example", width=set_width):
            with st.container(border=False, height=300):
                st.image(
                    "images/sample_obj.png", 
                    caption="**Main objects** has three group of labels.", 
                    output_format="PNG"
                )


def _name_labels(label_need_save, label_is_changed, submission_key):
    col_1, col_2, col_3, col_4 = st.columns(4)
    submitted = st.session_state["submitted"]["objects_details"]
    col_1.markdown(f"""**Name labels for your categories:**""")  
    col_1.markdown("""
    - Can be added or edited later
    - lank labels will be generated for empty fields
    - Recommended number: 1-12 labels per category
    """)
    submission = {
        "utility": [],
        "attribute": [],
        "origin": []
    }

    with col_2.container(border=True):
        st.markdown(f"""##### Main & secondary objects""", text_alignment="center")
        st.markdown(f"""Category: {submitted["utility"]}""", text_alignment="center")
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
                kwargs={"all_required": False,},
                placeholder="Label name", 
                label_visibility="collapsed"
            )
        for x in utility_keys:
            _define_labels(x, submission["utility"])
        print("util", submission["utility"])

    with col_3.container(border=True):
        st.markdown("##### Main objects", text_alignment="center")
        st.markdown(f"""Category: {submitted["attribute"]}""", text_alignment="center")
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
                kwargs={"all_required": False,},
                placeholder="Label name", 
                label_visibility="collapsed"
            )
        for x in attribute_keys:
            _define_labels(x, submission["attribute"])
        print("attr", submission["attribute"])

    with col_4.container(border=True):
        st.markdown("##### Main objects", text_alignment="center")
        st.markdown(f"""Category: {submitted["origin"]}""", text_alignment="center")
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
                kwargs={"all_required": False,},
                placeholder="Label name", 
                label_visibility="collapsed"
            )
        for x in origin_keys:
            _define_labels(x, submission["origin"])
        print("ori", submission["origin"])
    
    st.session_state["checklists"]["label_save"] = []
    for x in ["utility", "attribute", "origin"]:
        for y in submission[x]:
            st.session_state["checklists"]["label_save"].append(y)

    return submission


def _define_labels(key, submission):
    submitted_label = st.session_state[key]
    print(submitted_label)
    if submitted_label is not None:
        if len(submitted_label) == 0: submitted_label = None
    print(submission)
    if submitted_label not in submission:
        submission.append(submitted_label)
    else:
        st.warning("Multiples excluded")