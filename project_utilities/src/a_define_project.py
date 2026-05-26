import streamlit as st

import utils.tools as tools


# Step 1: name project title, objects and label categories
def define_project(set_width, set_heigth):
    with st.container(
            border=False, width=set_width, 
            height="stretch", horizontal_alignment="center"):
        # Header
        st.progress(20, width="stretch")
        col_prev, col_space, col_title, col_apply, col_next = st.columns(
            [2, 2, 5, 2, 2])
        tools.navigate(col_prev, col_next)
        col_title.markdown(
            "#### Naming your project and collections", 
            text_alignment="center")
        st.space()

        # Form
        submission_key = "project_details"
        project_need_save = "project_need_save"
        project_is_changed = "project_is_changed"
        with st.container(horizontal_alignment="center"):
            submission = _name_project(project_need_save, project_is_changed, submission_key)
        with col_apply:
            tools.apply("project_save", project_need_save, project_is_changed, submission_key, submission)

    # Demo
    with st.expander("View example", width=set_width):
        col_1, col_2 = st.columns(2)
        col_1.image(
            "images/sample_obj.png", 
            caption="**Main objects** has three group of labels.", 
            output_format="PNG"
        )
        col_2.image(
            "images/sample_obj.png", 
            caption="**Secondary objects** only has the the first label group.", 
            output_format="PNG"
            )


# def _apply(key, need_save, is_changed, submission_key, submission):
#     st.button(
#         "Save", 
#         key=key, 
#         on_click=tools.submit, 
#         args=(need_save, is_changed, submission_key, submission), 
#         type=st.session_state[need_save], 
#         disabled=st.session_state[is_changed],
#         width="stretch"
#     )


def _name_project(project_need_save, project_is_changed, submission_key):
    col_1, col_2, col_3 = st.columns([1, 1.5, 1.5])
    # Instructions
    col_1.markdown("""You need to name your project and the overall name of your collections/subjects with one major and one minor type (you will see one history table for each).""")
    col_1.markdown("""
        - **Title:** displayed name and project folder name
        - **Main objects:** timeline and more detailed analysis
        - **Secondary objects:** less analysis, no timeline
    """)
    col_1.markdown("""
        - **Labels:** Can be used for sorting and searchability in event history tables. 
    """)

    with col_2.container(border=True, height="stretch"):
        st.markdown("##### Title and objects", text_alignment="center")
        st.text_input(
            "Project title", 
            key="ui_title", 
            on_change=tools.need_update,
            args=(project_need_save, project_is_changed), 
            help="Name for folder and display", 
            placeholder="Learning path / Reading / Collection / Activity"
        )

        help_primary = """
            Actual objects for each suggestion could e.g. be:  
            - (learning: course) Python Fundamentals
            - (reading: book) The Two Towers
            - (collection: figure) Obsidian figurine
            - (activity: workout) 5K Running Plan
        """
        help_secondary = """
            Use for less complex or non-priority  
            objects which you still want to record,  
            or things you want tracked separately.
        """
        st.text_input(
            "Main object", 
            key="main", 
            on_change=tools.need_update, 
            args=(project_need_save, project_is_changed), 
            help=help_primary, 
            placeholder="Course / Book / Workout / Collectible"
        )
        st.text_input(
            "Secondary object", 
            key="secondary", 
            on_change=tools.need_update, 
            args=(project_need_save, project_is_changed), 
            help=help_secondary,
            placeholder="Tutorial / Article / Walk / Accessory"
        )

    with col_3.container(border=True, height="stretch"):
        st.markdown("##### Object labels", text_alignment="center")
        st.text_input(
            "1. Label for main and secondary objects", 
            key="utility", 
            on_change=tools.need_update, 
            args=(project_need_save, project_is_changed), 
            help="Use a broad label which can apply to both object types",
            placeholder="Topic / Genre / Effort / Series"
        )
        st.text_input(
            "2. Label for main object", 
            key="attribute", 
            on_change=tools.need_update, 
            args=(project_need_save, project_is_changed), 
            placeholder="Platform / Author / Type / Manufacturer"
        )
        st.text_input(
            "3. Label for main object", 
            key="origin", 
            on_change=tools.need_update, 
            args=(project_need_save, project_is_changed), 
            placeholder="Examination / Format / Muscle group / Scale"
        )

    return {
        "ui_title": st.session_state["ui_title"],
        "main": st.session_state["main"],
        "secondary": st.session_state["secondary"],
        "utility": st.session_state["utility"],
        "attribute": st.session_state["attribute"],
        "origin": st.session_state["origin"]
    }

    