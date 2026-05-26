import streamlit as st

import utils.tools as tools


# Step 5: finalize and save
def finalize(set_width, set_heigth):
    with st.container(
            border=False, width=set_width, 
            height="stretch", horizontal_alignment="center"):
        # Header
        st.progress(100, width="stretch")
        col_prev, col_space, col_title, col_apply, col_next = st.columns(
            [2, 2, 5, 2, 2])
        tools.navigate(col_prev, col_next)
        col_title.markdown(
            "#### Finalize", 
            text_alignment="center")
        st.space()

        with col_apply:
            tools.register("register")

        submitted = st.session_state["submitted"]
        project = submitted["project_details"]["ui_title"]
        main = submitted["project_details"]["main"]
        secondary = submitted["project_details"]["secondary"]
        utility = submitted["project_details"]["utility"]
        attribute = submitted["project_details"]["attribute"]
        origin = submitted["project_details"]["origin"]

        progress = submitted["event_terms"]["attempt"]
        events = submitted["event_terms"]["event"]
        sources = submitted["event_terms"]["sources_name"]

        positive = submitted["event_terms"]["state_win"]
        negative = submitted["event_terms"]["state_loss"]
        neutral = submitted["event_terms"]["state_det"]

        general_limit = submitted["progress_details"]["general_limit"]
        reverse_positive = submitted["progress_details"]["reverse_positive"]
        positive_value = submitted["progress_details"]["positive_value"]
        negative_value = submitted["progress_details"]["negative_value"]
        unit = submitted["progress_details"]["unit"]
        label_terms = {
            "utility": utility,
            "attribute": attribute,
            "origin": origin
        }
        registered_labels = {
            "utility": submitted["label_details"]["utility"],
            "attribute": submitted["label_details"]["attribute"],
            "origin": submitted["label_details"]["origin"]
        }

        # registered_sources = submitted["progress_details"]["source_list"]

        col_1, col_sp1, col_2, col_sp2, col_3 = st.columns([1.5, 0.2, 0.7, 0.2, 1.3])
        prefix = str()
        if unit: prefix = f", value prefix {unit}"
        col_1.markdown(f"""
Your defined project: {project}  
Your project will track {main} and {secondary} entries.  

{events} can be recorded with:
- date
- {sources}.
- (optional) {progress}{prefix}
- (optional) outcome evaluation: {positive}, {negative} or {neutral}

{main} and {secondary} can be categorized with: {label_terms['utility']}.  
{main} can also be categorized with: {label_terms['attribute']} and {label_terms['origin']}.
""")

        util = str()
        attr = str()
        orig = str()
        labels_str = str()

        for x in ["utility", "attribute", "origin"]:
            labels_str += f"\n\n{label_terms[x]}:\n"
            for y in registered_labels[x]:
                labels_str += f"- {y}\n"
            labels_str += "\n"

        col_2.markdown(f"You have registered labels: {labels_str}")

        sources_str = str()
        for x, y in submitted["progress_details"]["sources"].items():
            sources_str += f"\n\n{x}: {y}"
        
        if reverse_positive:
            positive_statement, negative_statement = "below", "above"
        else:
            negative_statement, positive_statement = "below", "above"
        col_3.markdown(f"""{progress} values are positive when {positive_statement} {positive_value}  
                       and negative when {negative_statement} {negative_value}.""")

        col_3.markdown(f"Your general {progress} limit: {general_limit}")
        
        col_3.markdown(f"You have registered the following {sources} with {progress} limits: {sources_str}")