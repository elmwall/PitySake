import json
import streamlit as st

import utils.tools as tools


# Step 3: name terms for progress, sources and outcome
def define_event_terms(set_width, set_heigth):
    with st.container(
            border=False, width=set_width, 
            height="stretch", horizontal_alignment="center"):
        # Header
        st.progress(60, width="stretch")
        col_prev, col_space, col_title, col_apply, col_next = st.columns([2, 2, 5, 2, 2])
        tools.navigate(col_prev, col_next, page=2)
        col_title.markdown("#### Progress and events", text_alignment="center")
        st.space()

        # Form
        submission_key = "event_terms"
        event_need_save = "event_need_save"
        event_is_changed = "event_is_changed"
        with st.container(horizontal_alignment="center"):
            submission = _name_events(event_need_save, event_is_changed, submission_key)
        with col_apply:
            tools.apply("event_save", event_need_save, event_is_changed, submission_key, submission)

    with st.expander("View example", width=set_width):
        col_1, col_2 = st.columns(2)



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



def _name_events(event_need_save, event_is_changed, submission_key):

    col_info, col_requirements, col_sp = st.columns(3)
    col_1, col_2, col_3 = st.columns([1, 1.5, 1.5])
    col_1.markdown("""
        Events are associated with a value, which can signify e.g. stages completed, score, attempts before success, worth.
    """)
    col_1.markdown("""
        - asdf
        - asdf 
        - sdf        
    """)

    with col_2.container(border=True, height="stretch"):
        st.markdown("##### Efforts and events", text_alignment="center")
        st.markdown("")
        st.text_input("Progress/value", key= "attempt", help="What tasks or value is counted as your progress?", placeholder="Chapters")
        st.text_input("Completed task", key= "active_attempts", help="A single task completed.", placeholder="Completed chapter")
        st.text_input("Event/milestone with associated tasks", key= "event", help="A set of tasks completed associated associated with your progress value.", placeholder="Session")
        st.text_input("Event source/type", key= "event_name", help="A broad category associated with your progress.", placeholder="Remote course")
        ## TODO progress --> progress calculcator

    with col_3.container(border=True, height="stretch"):
        st.markdown("##### Prognosis", text_alignment="center")
        st.text_input("Expected outcome or state", key="state", help="Simply a term associated with the prognosis.", placeholder="Prognosis")
        st.text_input("Uncertain prognosis", key="state_rand",  help="", placeholder="To be decided")

    with col_3.container(border=True, height="stretch"):
        st.markdown("##### Outcome", text_alignment="center")

        neu_help = """
            An result neither positive or negative, or that is already determined.  
            
            This will not give any highlighted indication in your timeline.
        """
        st.text_input("Neutral outcome", key="state_det", help=neu_help, placeholder="Not applicable")

        pos_help = """
            A positive result, will have a positive highlight in your timeline.
        """
        st.text_input("Positive outcome", key="state_win", help=pos_help, placeholder="Pass")
        
        neg_help = """
            A negative result, will have a negative highlight in your timeline.
        """
        st.text_input("Negative outcome", key="state_loss", help=neg_help, placeholder="Fail")

    return {}


