"""
Page C: Name personalized terms

Guide: explain concept of value, source, and outcomes  
Example images: 
- table feature (source and value)
- timeline feature (positive/negative/netral outcomes)
- object registration feature (source, value, outcome)

Manages:
- Form: collect terms for each
"""

import streamlit as st

from utils import tools


# Step 3: name terms for progress, sources and outcome
def define_event_terms(set_width: int|str):
    """
    Define terms for values, sources and outcomes - present user info and collect details.

    Behavior:
    - disables save button until all fields are filled, re-enables if a field is changed
    - disables next button until first save
    """
    with st.container(
            border=False, width=set_width, 
            height="stretch", horizontal_alignment="center"):
        if not all(st.session_state["submitted"]["event_terms"].values()):
            st.session_state["page_incomplete"] = True
        else:
            st.session_state["page_incomplete"] = False

        # Header
        st.progress(60, width="stretch")
        col_prev, col_space, col_title, col_apply, col_next = st.columns(
            [2, 2, 5, 2, 2])
        tools.navigate(col_prev, col_next)
        col_title.markdown(
            "#### Values and events", text_alignment="center")
        st.space()

        # Form
        submission_key = "event_terms"
        button_format_key = "event_need_save"
        is_changed_key = "event_is_changed"
        with st.container(horizontal_alignment="center"):
            submission = _name_events(button_format_key, is_changed_key)
        with col_apply:
            tools.apply("event_save", button_format_key, is_changed_key, submission_key, submission)

        # Demo
        col_d1, col_d2 = st.columns(2)
        with col_d1.expander("Explanation"):
            with st.container(border=False):
                st.markdown("""
                ##### Events  
                - Events registered are always associated with a date and a source and is displayed in history.  
                - They may be recorded with or without value or outcome, but:  
                    - An event with a value is required for timeline visualization
                    - Events without an outcome or with a neutral outcome do not affect evaluation statistics
                
                ##### Outcomes  
                Outcomes do not need to be good or bad states, examples:  
                - Easy / Medium / Hard  
                - Legendary / Rare / Common  
                - Expected / Unexpected / Common
                
                The 'positive' and 'negative' states receive have unique color annotations in the timeline and are used when calculating outcome statistics.
                """)
        with col_d2.expander("View examples", width=set_width):
            with st.container(border=False):
                st.image(
                    "../accessories/tab_notes.png", 
                    output_format="PNG"
                )
                st.image(
                    "../accessories/timeline2_notes.png", 
                    output_format="PNG"
                )
                st.image(
                    "../accessories/object_reg2_notes3.png", 
                    output_format="PNG"
                )


def _name_events(button_format_key: str, is_changed_key: str) -> dict:
    """
    User info and input fields for terms.  
    Generate error message for invalid names.

    Args:
        button_format_key (str):
            format key, setting discrete or highlighted save button
        is_changed_key (str): 
            control key for behavior upon change

    Returns:
        (dict):
            attempt, sources_name, state_det, state_win, state_loss"""
    col_1, col_2, col_3 = st.columns([1, 1.5, 1.5])

    # User info
    col_1.markdown("For events registered, here you name recorded values, sources and outcomes.")
    col_1.markdown(f"""
        - **Events:** recorded for individual objects, with date, source, value, and outcome
        - **Value:** a value associated with the event  
        - **Source:** event categories
    """)
    col_1.markdown("""
        - **Outcome:** for evaluating your events with a particular state (e.g. positive/negative/neutral)
    """)

    # Input fields
    # - Value and source terms
    with col_2.container(border=True, height="stretch"):
        st.markdown("##### Value and event terms", text_alignment="center")
        st.markdown("")
        st.text_input(
            "Value", 
            key= "attempt", 
            help="""A name for the value you track for objects,  
            e.g. a count, a result, or cost.""", 
            on_change=tools.need_update, 
            args=(button_format_key, is_changed_key), 
            placeholder="Exercises / Length / Value")
        st.text_input(
            """Event source, as in  
            'I achieved this in a ...'  
            'I received this from a ...'  
            'I added this to a ...'""", 
            key= "sources_name", 
            help="""You track values within one source,  
            here you set a name for sources as a group (in singular).""", 
            on_change=tools.need_update, 
            args=(button_format_key, is_changed_key), 
            placeholder="Learning track / Workout program / Collection")
        
    # - Outcome terms
    with col_3.container(border=True, height="stretch"):
        st.markdown("##### Outcome evaluations terms", text_alignment="center")

        neu_help = """
            A result neither positive or negative, or that is already determined.  
            This will not give any highlighted indication in your timeline.
        """
        st.text_input(
            "Neutral outcome", 
            key="state_det", 
            help=neu_help,
            on_change=tools.need_update, 
            args=(button_format_key, is_changed_key), 
            placeholder="Neutral / Not applicable / Expected")

        pos_help = """
            A positive result, will have a positive highlight in your timeline.
        """
        st.text_input(
            "Positive outcome", 
            key="state_win", 
            help=pos_help, 
            on_change=tools.need_update, 
            args=(button_format_key, is_changed_key), 
            placeholder="Easy / Success / High value")
        
        neg_help = """
            A negative result, will have a negative highlight in your timeline.
        """
        st.text_input(
            "Negative outcome", 
            key="state_loss", 
            help=neg_help, 
            on_change=tools.need_update, 
            args=(button_format_key, is_changed_key), 
            placeholder="Hard / Fail / Low value")
    
    # Word validation
    validated = dict()
    ref = {
        "attempt": "value term",
        "sources_name": "event source term",
        "state_det": "neutral outcome term",
        "state_win": "positive outcome term",
        "state_loss": "negative outcome term"
    }
    for x in ref.keys():
        word_is_invalid = tools.symbol_validation(st.session_state[x])
        value = None if word_is_invalid else st.session_state[x]
        validated[x] = value
        if word_is_invalid: 
            if x in ["attempt", "sources_name"]:
                col_2.error(f"{ref[x].capitalize()}: {word_is_invalid}")
            else:
                col_3.error(f"{ref[x].capitalize()}: {word_is_invalid}")

    # Checklist for enabling save
    st.session_state["checklists"]["event_save"] = [
        validated["attempt"],
        validated["sources_name"],
        validated["state_det"],
        validated["state_win"],
        validated["state_loss"],
    ]

    return  {
        "attempt": st.session_state["attempt"],
        "sources_name": st.session_state["sources_name"],
        "state_det": st.session_state["state_det"],
        "state_win": st.session_state["state_win"],
        "state_loss": st.session_state["state_loss"]
    }


