import json
import streamlit as st

import utils.tools as tools


# Step 4: define limits
def define_event_limits(set_width, set_heigth):
    with st.container(
            border=False, width=set_width, 
            height="stretch", horizontal_alignment="center"):
        # Header
        st.progress(80, width="stretch")
        col_prev, col_space, col_title, col_apply, col_next = st.columns(
            [2, 2, 5, 2, 2])
        tools.navigate(col_prev, col_next, page=2)
        col_title.markdown(
            "#### Object labels", text_alignment="center")
        st.space()

        # Form
        submission_key = "limits_details"
        limits_need_save = "limits_need_save"
        limits_is_changed = "limits_is_changed"
        with st.container(horizontal_alignment="center"):
            submission = _define_sources(limits_need_save, limits_is_changed, submission_key)
        with col_apply:
            tools.apply("limits_save", limits_need_save, limits_is_changed, submission_key, submission)

    with st.expander("View example", width=set_width):
        st.image("images/sample_att.png")
    



def _define_sources(limits_need_save, limits_is_changed, submission_key):
    with st.container():
        st.divider()
        st.markdown("#### Event sources", text_alignment="center")
        col_3, col_4, col_5 = st.columns([3, 3, 4])

        with col_3.container(border=True):
            st.markdown("##### Required event sources")
            st.markdown("Required events")
            col_left, col_right = st.columns(2)
            col_left.text_input(f"{1}", help="")
            col_right.number_input("temp limit", min_value=1)

            col_left.text_input(f"{2}", help="")
            col_right.number_input("mix limit", min_value=1)

            col_left.text_input(f"{3}", help="")
            col_right.number_input("common limit", min_value=1)

            col_left.text_input(f"{4}", help="")

        with col_4.container(border=True):
            st.markdown("##### Extra event sources")
            st.markdown("Required events")
            source_count = st.number_input("Number of extra event sources", min_value=1)
            col_left, col_right = st.columns(2)
            key = "source_extra"
            for x in range(source_count):
                key_txt = f"{key}_{x + 1}_name"
                key_num = f"{key}_{x + 1}_limit"

                col_left.text_input("extra", key=key_txt, help="")
                col_right.number_input("limit", key=key_num, min_value=1)









