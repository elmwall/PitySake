import json
import streamlit as st


with open("config_template.json", "r", encoding="utf-8") as f:
    settings = json.load(f)


def run_define_event_limits(set_width, set_heigth):
    col_main, col_dev = st.columns([8, 2])
    # Step 1: name title and label categories
    with col_main.container(key="guide", width=1200, horizontal_alignment="center"):
 
        with st.container():
            st.divider()
            st.markdown("#### Event sources", text_alignment="center")
            col_3, col_4, col_5 = st.columns([3, 3, 4])

            with col_3.container(border=True):
                st.markdown("##### Required event sources")
                st.markdown("Required events")
                col_left, col_right = st.columns(2)
                col_left.text_input(f"{settings["TERMS"]["temp"]}", help="")
                col_right.number_input("temp limit", min_value=1)

                col_left.text_input(f"{settings["TERMS"]["mix"]}", help="")
                col_right.number_input("mix limit", min_value=1)

                col_left.text_input(f"{settings["TERMS"]["common_source"]}", help="")
                col_right.number_input("common limit", min_value=1)

                col_left.text_input(f"{settings["TERMS"]["gift"]}", help="")

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

            col_5.image("sample_att.png")







def _need_update(save_hightlight, save_disable):
    st.session_state[save_hightlight] = "primary"
    st.session_state[save_disable] = False



def _submit(save_hightlight, save_disable, submission_key, submission):
    st.session_state[save_hightlight] = "secondary"
    st.session_state[save_disable] = True
    st.session_state["submitted"][submission_key] = submission


def _apply(key, need_save, is_changed, submission_key, submission):
    st.button(
        "Save", 
        key=key, 
        on_click=_submit, 
        args=(need_save, is_changed, submission_key, submission), 
        type=st.session_state[need_save], 
        disabled=st.session_state[is_changed],
        width="stretch"
    )

