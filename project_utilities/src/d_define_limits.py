import streamlit as st

from utils import tools


# Step 4: define limits
def define_event_limits(set_width, set_heigth):
    with st.container(
            border=False, width=set_width, 
            height="stretch", horizontal_alignment="center"):
        if not all(st.session_state["submitted"]["progress_details"].values()):
            st.session_state["page_incomplete"] = True
        else:
            st.session_state["page_incomplete"] = False

        # Header
        st.progress(80, width="stretch")
        col_prev, col_space, col_title, col_apply, col_next = st.columns(
            [2, 2, 5, 2, 2])
        tools.navigate(col_prev, col_next)
        col_title.markdown(
            "#### Sources and value limits", text_alignment="center")
        st.space()

        # Form
        submission_key = "progress_details"
        progress_need_save = "progress_need_save"
        progress_is_changed = "progress_is_changed"
        with st.container(horizontal_alignment="center"):
            submission = _define_sources(progress_need_save, progress_is_changed, submission_key)
        with col_apply:
            tools.apply("progress_save", progress_need_save, progress_is_changed, submission_key, submission)

        # Demo
        col_d1, col_d2 = st.columns(2)
        with col_d1.expander("Explanation"):
            with st.container(border=False, height=300):
                st.markdown("""
                ##### Sources:
                - Group related events
                - Each event registered belong to a source
                - Sources control whether events store values (with separate range limits) and if they are included in statistics (success/fail counts)
                - You can add or remove sources and adjust limits later
                
                ##### Timeline highlights
                - Mark values you consider notable
                - Mark 'success' and 'fail' outcomes
                - They do not affect calculations
                            
                Behavior:
                - If high values are 'positive': 
                    - low value → negative color
                    - high value → positive color
                - If low values are 'positive': 
                    - high value → negative color
                    - low value → positive color
                
                ##### Value rules
                            
                - Values are optional depending on source settings
                - Values must be integers (no decimal values)
                - Recommended range: 1-99999 
                - Unit suffix affects is only a display indicator of your value sizes, values themselves are displayed exactly as you enter them  
                """)
        with col_d2.expander("View example", width=set_width):
            with st.container(border=False, height=300):
                st.image(
                    "images/sample_obj.png", 
                    caption="**Main objects** has three group of labels.", 
                    output_format="PNG"
                )


def _define_sources(progress_need_save, progress_is_changed, submission_key):
    col_1, col_2, col_3 = st.columns([1, 1.5, 1.5])

    col_1.markdown("""
        Define how events are categorized and adjust their value limits.
        - Each source is a separate category for logging events and tracking values
        - Sources can optionally store outcome evaluation (previous page) and values
        - Timline highlights: to distiguish notable values and outcomes
        - Unit suffix affects display only. Stored values are not converted. 
    """)
    source_dict = dict()
    checks = dict()
    names = dict()
    with col_2.container(border=True, height="stretch"):
        st.markdown("##### Sources", text_alignment="center")
        num_msg = """Number of event sources  
        *Create at least 1 - can be edited later*"""
        source_count = st.number_input(num_msg, min_value=1)

        key = "source"
        for x in range(source_count):
            st.divider()
            with st.container():
                col_left, col_right = st.columns(2)
                key_txt = f"{key}_{x + 1}_name"
                key_evaluation = f"{key}_{x + 1}_evaluation"
                key_disable_value = f"{key}_{x + 1}_disable_value"
                key_num = f"{key}_{x + 1}_limit"
                col_left.text_input(
                    "Source name", 
                    key=key_txt, 
                    help="",
                    on_change=tools.need_update, 
                    args=(progress_need_save, progress_is_changed)
                )
                col_right.checkbox("Outcome evaluation", key=key_evaluation, value=True)
                disable_values = not col_right.checkbox("Include values", key=key_disable_value, value=True)
                col_right.number_input(
                    "Source-specific value limit", 
                    key=key_num, 
                    min_value=1, 
                    value=100,
                    on_change=tools.need_update, 
                    args=(progress_need_save, progress_is_changed),
                    disabled=disable_values
                )

                word_is_invalid = tools.symbol_validation(st.session_state[key_txt])
                name_value = None if word_is_invalid else st.session_state[key_txt]
                if word_is_invalid: 
                    col_left.error(word_is_invalid)
                names[key_txt] = name_value

                checks[f"name_{x}"] = name_value
                if disable_values:
                    value = None
                    checks[f"value_{x}"] = True
                else:
                    value = st.session_state[key_num]
                    checks[f"value_{x}"] = value
                source_dict[st.session_state[key_txt]] = {
                    "limit": value,
                    "evaluate": st.session_state[key_evaluation]
                }
            

    with col_3.container(border=True):
        st.markdown("##### Timeline highlights", text_alignment="center")
        col_left, col_right = st.columns(2)

        disable_highlights = col_left.checkbox("Use highlights", value=True, key="use_highlights") == False
        col_right.checkbox("High values are positive", key="reverse_positive", disabled=disable_highlights)
        col_left.number_input("Low value threshold", min_value=-1, value=10, key="low_value", disabled=disable_highlights)
        col_right.number_input("High value threshold", min_value=0, value=90, key="high_value", disabled=disable_highlights)
        if disable_highlights:
            checks["low"], checks["high"] = True, True
        else:
            checks["low"], checks["high"] = st.session_state["low_value"], st.session_state["high_value"]

    with col_3.container(border=True):
        st.markdown("##### Display units", text_alignment="center")
        col_left, col_right = st.columns(2)
        text = """Use suffix to signify:  
            M: Mega (× 1 000 000)  
            k: kilo (× 1 000)  
            None: skip  
            m: milli (÷ 1 000)  
            µ: micro (÷ 1 000 000)
            """     
        col_left.markdown(text)
        col_right.selectbox(
            "suffix", 
            options=["M", "k", "None", "m", "µ"], 
            index=2, 
            key="unit",
            on_change=tools.need_update, 
            args=(progress_need_save, progress_is_changed)
        )
    
    unit = None if st.session_state["unit"] == "None" else st.session_state["unit"]
    st.session_state["checklists"]["progress_save"] = list(checks.values())
    print(checks)

    switches = {
        "unit": unit,
        "reverse_positive": not st.session_state["reverse_positive"],
        "use_highlights": st.session_state["use_highlights"]

    }

    return  {
        "sources": source_dict,
        "switches": switches,
        "high_limit": st.session_state["high_value"],
        "low_limit": st.session_state["low_value"]
    }







