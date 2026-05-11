import streamlit as st

import utils.tools as tools




def run_define_project(set_width, set_heigth):
    # Step 1: name title and label categories
    with st.container(border=False, key="guide", width=set_width, height="stretch", horizontal_alignment="center"):
        with st.container(horizontal_alignment="center"):
            _name_project()
    with st.expander("View example", width=set_width):
        col_1, col_2 = st.columns(2)
        # TODO: image of main selection
        col_1.image(
            "images/sample_obj.png", 
            caption="**Main objects** has three group of labels.", 
            output_format="PNG"
        )
        # TODO: image of secondary selection
        col_2.image(
            "images/sample_obj.png", 
            caption="**Secondary objects** only has the the first label group.", 
            output_format="PNG"
            )


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


def _name_project():
    col_prev, col_space, col_title, col_apply, col_next = st.columns([2, 2, 5, 2, 2])

    tools.navigate(col_prev, col_next, page=1)
    col_title.markdown("#### Naming your collection", text_alignment="center")
    st.space()


    col_info, col_requirements, col_sp2 = st.columns([1, 1, 1])
    col_info.markdown("""
        **Title** is viewed on the top of your display and names your project folder
                 
        **Main objects:** 3 labels, more detailed analysis, shown in history and timeline
        
        **Secondary objects:** 1 label, separate history but no timeline
    """)
    col_requirements.markdown("""
        **Labels** (named in the next stage) can be used for sorting and searchability in data tables.        
    """)

    col_2, col_3 = st.columns(2)
    project_need_save, project_is_changed = "project_need_save", "project_is_changed"

    with col_2.container(border=True, height="stretch"):
        st.markdown("##### Title and objects", text_alignment="center")
        st.text_input(
            "Project title", 
            key="ui_title", 
            on_change=tools.need_update,
            args=(project_need_save, project_is_changed), 
            help="Name for folder and display", 
            placeholder="Learning path"
        )

        st.space()
        help_primary = """
            Names object in view and database.  

            Main objects have more options for labels  
            and more in-depth view and data analysis.
        """
        help_secondary = """
            Names object in view and database.  

            Use for less complex and non-priority  
            objects which you still want to record.
        """
        st.text_input(
            "Primary object - 3 properties", 
            key="main", 
            on_change=tools.need_update, 
            args=(project_need_save, project_is_changed), 
            help=help_primary, 
            placeholder="Main course"
        )
        st.text_input(
            "Secondary object - 1 property", 
            key="secondary", 
            on_change=tools.need_update, 
            args=(project_need_save, project_is_changed), 
            help=help_secondary,
            placeholder="Side course"
        )

    with col_3.container(border=True, height="stretch"):
        st.markdown("##### Object categories", text_alignment="center")
        st.text_input(
            "1. Main/secondary object category name", 
            key="utility", 
            on_change=tools.need_update, 
            args=(project_need_save, project_is_changed), 
            help=""
        )
        st.text_input(
            "2. Main object category name", 
            key="attribute", 
            on_change=tools.need_update, 
            args=(project_need_save, project_is_changed), 
            help=""
        )
        st.text_input(
            "3. Main object category name", 
            key="origin", 
            on_change=tools.need_update, 
            args=(project_need_save, project_is_changed), 
            help=""
        )

            


    submission_key = "name_details"
    submission = {
        submission_key: {
            "ui_title": st.session_state["ui_title"],
            "main": st.session_state["main"],
            "secondary": st.session_state["secondary"],
            "utility": st.session_state["utility"],
            "attribute": st.session_state["attribute"],
            "origin": st.session_state["origin"]
        }
    }
    
    with col_apply:
        _apply("name_save", project_need_save, project_is_changed, submission_key, submission)




# if __name__ == "__main__":
#     run_form(settings)