import json
import streamlit as st

from utils import tools


# Step 4: define limits
def define_event_limits(set_width, set_heigth):
    with st.container(
            border=False, width=set_width, 
            height="stretch", horizontal_alignment="center"):
        # Header
        st.progress(80, width="stretch")
        col_prev, col_space, col_title, col_apply, col_next = st.columns(
            [2, 2, 5, 2, 2])
        tools.navigate(col_prev, col_next)
        col_title.markdown(
            "#### Progress sources", text_alignment="center")
        st.space()

        # Form
        submission_key = "progress_details"
        progress_need_save = "progress_need_save"
        progress_is_changed = "progress_is_changed"
        with st.container(horizontal_alignment="center"):
            submission = _define_sources(progress_need_save, progress_is_changed, submission_key)
        with col_apply:
            tools.apply("progress_save", progress_need_save, progress_is_changed, submission_key, submission)

    with st.expander("View example", width=set_width):
        st.image("images/sample_att.png")
    



def _define_sources(progress_need_save, progress_is_changed, submission_key):
    col_1, col_2, col_3 = st.columns([1, 1.5, 1.5])

    col_1.markdown("""
        Here you can register separate sources.
        - **Sources:** will be displayed in your event history table, showing what your progress counts as.
        - **Limit:** if your source has a definite max value, set this as limit. **General limit** should be the highest expected among them. Otherwise you can set the limits as an impossibly high values for your progress.
        - **Highlight threshold:** a threshold for exceptionally high or low values. Depending on whether high/low are positive/negative, these values will be highlighted as such.
        - **Unit prefix:** if your tracked value is very large or small, adjust the value size so that it can be displayed with 1-5 digits. Decimals cannot be used (will only affect displayed value and not any functionality).
    """)

    # with col_2.container(border=True):
    #     st.text_input("Event source/type", key= "event_name", help="A broad category associated with your progress.", placeholder="Backend devenlopment / Epics / Cardio / Crystals")
        # st.markdown("##### Required event sources")
        # st.markdown("Required events")
        # col_left, col_right = st.columns(2)
        # col_left.text_input(f"{1}", help="")
        # col_right.number_input("temp limit", min_value=1)

        # col_left.text_input(f"{2}", help="")
        # col_right.number_input("mix limit", min_value=1)

        # col_left.text_input(f"{3}", help="")
        # col_right.number_input("common limit", min_value=1)

        # col_left.text_input(f"{4}", help="")
    source_dict = dict()
    with col_2.container(border=True):
        st.markdown("##### Sources", text_alignment="center")
        st.number_input("General limit", min_value=0, value=100, key="general_limit")
        source_count = st.number_input("Number of event sources", min_value=1)
        col_left, col_right = st.columns(2)

        key = "source"
        for x in range(source_count):
            key_txt = f"{key}_{x + 1}_name"
            key_num = f"{key}_{x + 1}_limit"
            col_left.text_input(
                "Source name", 
                key=key_txt, 
                help="",
                on_change=tools.need_update, 
                args=(progress_need_save, progress_is_changed)
            )
            col_right.number_input(
                "Limit", 
                key=key_num, 
                min_value=1, 
                value=100,
                on_change=tools.need_update, 
                args=(progress_need_save, progress_is_changed)
            )
            source_dict[st.session_state[key_txt]] = st.session_state[key_num]

    with col_3.container(border=True):
        st.markdown("##### Highlight threshold", text_alignment="center")
        st.checkbox("High values are positive", key="reverse_positive")
        col_left, col_right = st.columns(2)
        col_left.number_input("High value threshold", min_value=-1, value=10, key="high_value")
        col_right.number_input("Low value threshold", min_value=0, value=90, key="low_value")

    with col_3.container(border=True):
        st.markdown("##### Unit prefix", text_alignment="center")
        col_left, col_right = st.columns(2)
        text = """
M: Mega (× 1 000 000)  
k: kilo (× 1 000)  
None: skip  
m: milli (÷ 1 000)  
µ: micro (÷ 1 000 000)
"""     
        col_left.markdown(text)
        col_right.selectbox(
            "Prefix", 
            options=["M", "k", None, "m", "µ"], 
            index=2, 
            key="unit",
            on_change=tools.need_update, 
            args=(progress_need_save, progress_is_changed)
        )
    
    if st.session_state["reverse_positive"]:
        positive, negative = st.session_state["low_value"], st.session_state["high_value"]
    else:
        negative, positive = st.session_state["low_value"], st.session_state["high_value"]

    st.session_state["checklists"]["progress_save"] = [
        st.session_state["general_limit"],
        st.session_state["high_value"],
        st.session_state["low_value"]
    ] + list(source_dict.keys()) + list(source_dict.values())

    return  {
        "sources": source_dict,
        "unit": st.session_state["unit"],
        "general_limit": st.session_state["general_limit"],
        "reverse_positive": not st.session_state["reverse_positive"],
        "positive_value": positive,
        "negative_value": negative
    }







