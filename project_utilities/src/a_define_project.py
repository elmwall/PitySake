from pathlib import Path

import streamlit as st

from utils import tools


# Step 1: name project title, objects and label categories
def define_project(set_width, set_heigth):
    with st.container(
            border=False, width=set_width, 
            height="stretch", horizontal_alignment="center"):
        if not all(st.session_state["submitted"]["objects_details"].values()):
            st.session_state["page_incomplete"] = True
        else:
            st.session_state["page_incomplete"] = False

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
        submission_key = "objects_details"
        objects_need_save = "objects_need_save"
        objects_is_changed = "objects_is_changed"
        with st.container(horizontal_alignment="center"):
            submission = _name_objects(objects_need_save, objects_is_changed, submission_key)
        with col_apply:
            tools.apply("objects_save", objects_need_save, objects_is_changed, submission_key, submission)

        # Demo
        col_d1, col_d2 = st.columns(2)
        with col_d1.expander("Explanation"):
            with st.container(border=False, height=300):
                st.markdown("""**Main and secondary objects:**  objects are the items or subjects you want to track. Events associate them with a date with a value and evaluation.  
                - Main objects support detailed anaysis and statistics  
                - Secondary are tracked separately with reduced detail  
                - Appear in separate history tables  
                - Both contribute to overall totals and evaluations""")
                st.markdown("""**Labels:** help organizing tables and locating items.  
                - Sorting and searching tables  
                - Occurrences are included in statistics""")
        with col_d2.expander("View example", width=set_width):
            with st.container(border=False, height=300):
                st.image(
                    "images/sample_obj.png", 
                    caption="**Main objects** has three group of labels.", 
                    output_format="PNG"
                )


def _name_objects(objects_need_save, objects_is_changed, submission_key):
    col_1, col_2, col_3 = st.columns([1, 1.5, 1.5])
    # Instructions
    col_1.markdown("Define the names used in your project.")
    col_1.markdown("""
        - **Title:** display name and project folder
        - **Main objects:** your primary tracked item
        - **Secondary objects:** additional tracked item
    """)
    col_1.markdown("""
        - **Labels:** categories for sorting and searchability 
    """)

    with col_2.container(border=True, height="stretch"):
        root = Path(__file__).resolve().parent.parent.parent
        folder_list = [x.name for x in root.iterdir() if x.is_dir()]
        # print("folders", folder_list)

        st.markdown("##### Objects", text_alignment="center")
        # st.text_input(
        #     "Project title", 
        #     key="ui_title", 
        #     on_change=tools.need_update,
        #     args=(objects_need_save, objects_is_changed), 
        #     help="Name for folder and display", 
        #     placeholder="e.g. Learning path / Activity log / Collection"
        # )

        # if st.session_state["ui_title"]:
        #     objects_folder = st.session_state["ui_title"].lower().replace(" ", "_")
        #     if objects_folder in folder_list:
        #         st.error("A project already exists with that name.")

        help_primary = """
            Actual objects for each suggestion could e.g. be:  
            - (learning: course) Python Fundamentals
            - (activity: workout) 5K Running Plan
            - (collection: figure) Obsidian figurine
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
            args=(objects_need_save, objects_is_changed), 
            help=help_primary, 
            placeholder="e.g. Course / Workout / Collectible"
        )
        st.text_input(
            "Secondary object", 
            key="secondary", 
            on_change=tools.need_update, 
            args=(objects_need_save, objects_is_changed), 
            help=help_secondary,
            placeholder="e.g. Tutorial / Walk / Accessory"
        )

    with col_3.container(border=True, height="stretch"):
        st.markdown("##### Object labels", text_alignment="center")
        st.text_input(
            "1. Label for main and secondary objects", 
            key="utility", 
            on_change=tools.need_update, 
            args=(objects_need_save, objects_is_changed), 
            help="Use a broad label which can apply to both object types",
            placeholder="e.g. Topic / Effort / Series"
        )
        st.text_input(
            "2. Label for main object", 
            key="attribute", 
            on_change=tools.need_update, 
            args=(objects_need_save, objects_is_changed), 
            placeholder="e.g. Platform / Activity type / Manufacturer"
        )
        st.text_input(
            "3. Label for main object", 
            key="origin", 
            on_change=tools.need_update, 
            args=(objects_need_save, objects_is_changed), 
            placeholder="e.g. Examination / Muscle group / Scale"
        )

    st.session_state["checklists"]["objects_save"] = [
        # st.session_state["ui_title"],
        st.session_state["main"],
        st.session_state["secondary"],
        st.session_state["utility"],
        st.session_state["attribute"],
        st.session_state["origin"],
    ]

    return {
        # "ui_title": st.session_state["ui_title"],
        "main": st.session_state["main"],
        "secondary": st.session_state["secondary"],
        "utility": st.session_state["utility"],
        "attribute": st.session_state["attribute"],
        "origin": st.session_state["origin"]
    }

    