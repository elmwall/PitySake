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
        col_prev, col_space, col_title, col_apply, col_next = st.columns(
            [2, 2, 5, 2, 2])
        tools.navigate(col_prev, col_next)
        col_title.markdown(
            "#### Progress and events", text_alignment="center")
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




        # In your history you will see events focused on a specific registered object. The timeline shows such events with an associated value in progress. You can also track work in progress, a value associated with a source without an object.

def _name_events(event_need_save, event_is_changed, submission_key):

    col_1, col_2, col_3 = st.columns([1, 1.5, 1.5])
    col_1.markdown("""
        You track changes in your project in two ways: progress values and events via a source. 
    """)
        
    col_1.markdown("""
        - **Progress:** can optionally be added to events, and can be stages complete, efforts or a change in value.  
        - **Events:** can signify receiving a new object or achieving a goal.  
        - **Source:** a specific area, subject or collection you count your progress or efforts towards. Here you name your term for sources, in the next step you can register specific sources. 
    """)
    col_1.markdown("""
        - **Outcome:** you can optionally mark events with a prognosis an outcome, which can be e.g. difficulty, goal reached, pass/fail.
    """)

    with col_2.container(border=True, height="stretch"):
        st.markdown("##### Efforts and events", text_alignment="center")
        st.markdown("")
        st.text_input(
            "Progress/value", 
            key= "attempt", 
            help="What tasks or value is counted as your progress?", 
            on_change=tools.need_update, 
            args=(event_need_save, event_is_changed), 
            placeholder="Exercises / Chapters / Length / Value")
        st.text_input(
            "Event/milestone with associated tasks", 
            key= "event", 
            help="A set of tasks completed associated associated with your progress value.", 
            on_change=tools.need_update, 
            args=(event_need_save, event_is_changed), 
            placeholder="Study, Reading, or Workout session / Purchase")
        st.text_input(
            "What are your sources/subjects you make progress in?", 
            key= "sources_name", 
            help="A broad category within which you track your progress.", 
            on_change=tools.need_update, 
            args=(event_need_save, event_is_changed), 
            placeholder="Track / Category / Program / Collection")

    # with col_3.container(border=True, height="stretch"):
    #     st.markdown("##### Prognosis", text_alignment="center")
    #     st.text_input("Expected outcome or state", key="state", help="Simply a term associated with the prognosis.", placeholder="Prognosis")
    #     st.text_input("Uncertain prognosis", key="state_rand",  help="", placeholder="To be decided")

    with col_3.container(border=True, height="stretch"):
        st.markdown("##### Outcome", text_alignment="center")

        neu_help = """
            A result neither positive or negative, or that is already determined.  
            
            This will not give any highlighted indication in your timeline.
        """
        st.text_input(
            "Neutral outcome", 
            key="state_det", 
            help=neu_help,
            on_change=tools.need_update, 
            args=(event_need_save, event_is_changed), 
            placeholder="Neutral / Mid / Not applicable / Expected")

        pos_help = """
            A positive result, will have a positive highlight in your timeline.
        """
        st.text_input(
            "Positive outcome", 
            key="state_win", 
            help=pos_help, 
            on_change=tools.need_update, 
            args=(event_need_save, event_is_changed), 
            placeholder="Easy / Good / Success / High value")
        
        neg_help = """
            A negative result, will have a negative highlight in your timeline.
        """
        st.text_input(
            "Negative outcome", 
            key="state_loss", 
            help=neg_help, 
            on_change=tools.need_update, 
            args=(event_need_save, event_is_changed), 
            placeholder="Hard / Bad / Fail / Low value")

    return  {
        "attempt": st.session_state["attempt"],
        "event": st.session_state["event"],
        "sources_name": st.session_state["sources_name"],
        "state_det": st.session_state["state_det"],
        "state_win": st.session_state["state_win"],
        "state_loss": st.session_state["state_loss"]
    }


