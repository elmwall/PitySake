import streamlit as st

from utils import tools


# Step 3: name terms for progress, sources and outcome
def define_event_terms(set_width, set_heigth):
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
        event_need_save = "event_need_save"
        event_is_changed = "event_is_changed"
        with st.container(horizontal_alignment="center"):
            submission = _name_events(event_need_save, event_is_changed, submission_key)
        with col_apply:
            tools.apply("event_save", event_need_save, event_is_changed, submission_key, submission)

        # Demo
        col_d1, col_d2 = st.columns(2)
        with col_d1.expander("Explanation"):
            with st.container(border=False, height=300):
                st.markdown("""
                ##### Events  
                Events may be recorded with or without value or outcome, but:  
                - An event is required for an object event to appear in history
                - An event with a value is required for timeline visualization
                - Events without an outcome or with a neutral outcome do not affect evaluation statistics
                
                ##### Outcomes  
                Outcomes do not need to be good or bad states, examples:  
                - Easy / Medium / Hard  
                - Legendary / Rare / Common  
                - Expected / Unexpected / Common
                
                The 'positive' and 'negative' states receive have unique color annotations in the timeline and are used when calculating outcome statistics.
                """)
        with col_d2.expander("View example", width=set_width):
            with st.container(border=False, height=300):
                st.image(
                    "images/sample_obj.png", 
                    caption="**Main objects** has three group of labels.", 
                    output_format="PNG"
                )


def _name_events(event_need_save, event_is_changed, submission_key):
    submitted = st.session_state["submitted"]["objects_details"]
    col_1, col_2, col_3 = st.columns([1, 1.5, 1.5])
    col_1.markdown("Terms regarding values and occurrences")
    col_1.markdown(f"""
        - **Value:** a value associated with objects ({submitted["main"]} and {submitted["secondary"]})  
        - **Events:** object events record information about date, source, outcome, and value  
        - **Source:** event categories which can be associated with values
    """)
    col_1.markdown("""
        - **Outcome:** for evaluating your events with a particular state (e.g. positive/negative/neutral)
    """)

    with col_2.container(border=True, height="stretch"):
        st.markdown("##### Values and events", text_alignment="center")
        st.markdown("")
        st.text_input(
            "Name the term for values", 
            key= "attempt", 
            help="What tasks or value is counted as your progress?", 
            on_change=tools.need_update, 
            args=(event_need_save, event_is_changed), 
            placeholder="Exercises / Length / Value")
        st.text_input(
            "Create a collective term for your event sources", 
            key= "sources_name", 
            help="A broad category within which you track your progress.", 
            on_change=tools.need_update, 
            args=(event_need_save, event_is_changed), 
            placeholder="Learning track / Workout program / Collection")

    with col_3.container(border=True, height="stretch"):
        st.markdown("##### Outcome evaluations", text_alignment="center")

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
            placeholder="Neutral / Not applicable / Expected")

        pos_help = """
            A positive result, will have a positive highlight in your timeline.
        """
        st.text_input(
            "Positive outcome", 
            key="state_win", 
            help=pos_help, 
            on_change=tools.need_update, 
            args=(event_need_save, event_is_changed), 
            placeholder="Easy / Success / High value")
        
        neg_help = """
            A negative result, will have a negative highlight in your timeline.
        """
        st.text_input(
            "Negative outcome", 
            key="state_loss", 
            help=neg_help, 
            on_change=tools.need_update, 
            args=(event_need_save, event_is_changed), 
            placeholder="Hard / Fail / Low value")
        
    st.session_state["checklists"]["event_save"] = [
        st.session_state["attempt"],
        st.session_state["sources_name"],
        st.session_state["state_det"],
        st.session_state["state_win"],
        st.session_state["state_loss"],
    ]

    return  {
        "attempt": st.session_state["attempt"],
        "sources_name": st.session_state["sources_name"],
        "state_det": st.session_state["state_det"],
        "state_win": st.session_state["state_win"],
        "state_loss": st.session_state["state_loss"]
    }


