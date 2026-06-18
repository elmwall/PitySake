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
    - One single blank label will be generated if there are empty fields
    - Recommended number: 1-12 labels per category
    """)
    submitted_fields = {
        "utility": [],
        "attribute": [],
        "origin": []
    }

    with col_2.container(border=True):
        st.markdown(f"""##### Main & secondary objects""", text_alignment="center")
        submitted_fields["utility"] = _label_fields(
            "utility", submitted["utility"], label_need_save, label_is_changed)

    with col_3.container(border=True):
        st.markdown("##### Main objects", text_alignment="center")
        submitted_fields["attribute"] = _label_fields(
            "attribute", submitted["attribute"], label_need_save, label_is_changed)

    with col_4.container(border=True):
        st.markdown("##### Main objects", text_alignment="center")
        submitted_fields["origin"] = _label_fields(
            "origin", submitted["origin"], label_need_save, label_is_changed)
        
    st.session_state["checklists"]["label_save"] = []
    for x in ["utility", "attribute", "origin"]:
        for y in submitted_fields[x]:
            st.session_state["checklists"]["label_save"].append(y)

    return submitted_fields


def _label_fields(group_key, submitted, label_need_save, label_is_changed):
    st.markdown(f"""Category: {submitted}""", text_alignment="center")
    label_count = st.number_input(
        "Number of labels", 
        min_value=1, 
        key=f"label_{group_key}_number"
    )
    key = f"label_{group_key}"
    keys = list()
    for x in range(label_count):
        key_txt = f"{key}_{x + 1}"
        keys.append(key_txt)
        st.text_input(
            group_key, 
            key=key_txt, 
            help="", 
            on_change=tools.need_update, 
            args=(label_need_save, label_is_changed), 
            kwargs={"all_required": False,},
            placeholder="Label name", 
            label_visibility="collapsed"
        )
    
    label_list = list()
    for key in keys:
        submitted_label = st.session_state[key]
        if submitted_label is not None:
            if len(submitted_label) == 0: submitted_label = None
        if submitted_label not in label_list:
            label_list.append(submitted_label)
        st.session_state["label_fields"][group_key][key] = submitted_label
    
    _check_duplicates(group_key)
    if st.session_state[f"{group_key}_multiples"]: st.warning("Multiples excluded")
    return label_list
    

def _check_duplicates(group_key):
    collect = list()
    check = list()
    for value in st.session_state["label_fields"][group_key].values():
        if value is not None: check.append(value in collect)
        collect.append(value)
    if any(check):
        st.session_state[f"{group_key}_multiples"] = True
    else: 
        st.session_state[f"{group_key}_multiples"] = False
    # for x in submitted_fields:

