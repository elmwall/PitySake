import streamlit as st

from config import PAGES
# from utils.init import clear



def navigate(col_prev=None, col_next=None, page=0):
    if not col_prev and not col_next:
        col_prev, col_next = st.columns(2)
    prev_disabled = not st.session_state["page"] > 0
    if col_prev.button("Previous", key=f"prev_{page}", disabled=prev_disabled, width="stretch"):
        st.session_state["page"] -= 1
        st.rerun()

    next_disabled = not st.session_state["page"] < PAGES
    if col_next.button("Next", key=f"nex_{page}", disabled=next_disabled, width="stretch"):
        st.session_state["page"] += 1
        st.rerun()



def need_update(save_hightlight, save_disable):
    st.session_state[save_hightlight] = "primary"
    st.session_state[save_disable] = False


def apply(key, need_save, is_changed, submission_key, submission):
    st.button(
        "Save", 
        key=key, 
        on_click=submit, 
        args=(need_save, is_changed, submission_key, submission), 
        type=st.session_state[need_save], 
        disabled=st.session_state[is_changed],
        width="stretch"
    )


def submit(save_hightlight, save_disable, submission_key, submission):
    st.session_state[save_hightlight] = "secondary"
    st.session_state[save_disable] = True
    st.session_state["submitted"][submission_key] = submission


def dev_tools():
    
    if st.button("Clear"): clear()
    st.write(st.session_state)


def clear():
    for key in st.session_state.keys():
        del st.session_state[key]
    # st.session_state["cleared"] = True
    st.rerun()


