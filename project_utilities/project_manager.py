"""
Project installation wizard main

Intro page guide: examples of uses, case sensitivity  
Example image: full page

Manages:
- Page settings
- Calls for initialization
- Construct intro page or page a-e
- Reset entered info
- Form: project title (required), select template
- Directs to registration if template
"""

from pathlib import Path

import streamlit as st

from src.a_define_project import define_objects
from src.b_define_labels import define_labels
from src.c_define_event_terms import define_event_terms
from src.d_define_limits import define_event_limits
from src.e_finalize import finalize
from utils import init
from utils import tools
from utils import registration as reg
from config import SET_WIDTH


def welcome(set_width: int):
    """
    Wizard welcome page with intro information; collect new project info.

    Behavior:
    - previous disabled, disables next button until a valid title is saved
    - activates reset button if any changes are detected  
        -> clear all session state keys
    - directs to save -> next without template
        - disables save button until title is filled, re-enables if title is changed
    - directs to register if template (replaces save button)
    """
    with st.container(border=False, key="guide", width=set_width, height="content", horizontal_alignment="center"):
        # Header
        # Navigation control
        # Disabled if a template is selected (goes directly to register), or if lacking title
        if not all([st.session_state["submitted"]["project_details"]["ui_title"], 
               not st.session_state["selected_template"]]):
            st.session_state["page_incomplete"] = True
        else:
            st.session_state["page_incomplete"] = False
        # Progress bar
        st.progress(1, width="stretch")
        col_prev, col_reset, col_title, col_apply, col_next = st.columns([2, 2, 5, 2, 2])
        # Title
        col_title.markdown("#### *PitySake Project Installer*", text_alignment="center")
        tools.navigate(col_prev, col_next)
        # Reset button
        disable_reset = not any([
            st.session_state["submitted"]["project_details"]["ui_title"],
            any(st.session_state["submitted"]["project_details"].values()),
            any(st.session_state["submitted"]["event_terms"].values()),
            any(st.session_state["submitted"]["progress_details"].values())])

        # User info
        col_1, col_sp1, col_2, col_sp2, col_3 = st.columns([8, 1, 10, 1, 8])
        col_2.space("xsmall")
        col_2.markdown("""This wizard will guide you through creating a new project, 
                       with custimized terminology, categories and adjustments.""")
        # Form
        submission_key = "project_details"
        button_format_key = "project_need_save"
        is_changed_key = "project_is_changed"
        submission = _define_project(col_2, button_format_key, is_changed_key)
        # Apply & reset buttons
        with col_apply:
            if not submission["template"]:
                tools.apply(
                    "project_save", button_format_key, is_changed_key, submission_key, 
                    submission, invalid_input=not st.session_state["title_is_valid"])
            else:
                reg.register("register", disable=not submission["ui_title"], use_template=True)
        if col_reset.button("**Reset**", type="primary", disabled=disable_reset, width="stretch"):
            tools.clear()
                       
        # User tips
        col_1.space("xsmall")
        with col_1.container(border=True):
            st.markdown("""
            *What can I use this for?*  
            - Register courses: track lessons and study sessions  
            - Track activity: evaluate your averages and changes over time  
            - Catalogue collections: note values and rarities of objects collected  
            - Track challenges: log attempts and outcome  
            """)

        col_3.space("xsmall")
        col_3.markdown("""
        Example subjects throughout the wizard  
        shown as placeholders: 
        - Learning path
        - Exercise 
        - Collectibles
        """)

        # Expander: sample images
        with st.expander("Finished example"):
            st.image(
                "../accessories/theme1.png", 
                caption="Example for collections in game: Honkai Star Rail", 
                output_format="PNG")


def _define_project(col, button_format_key: str, is_changed_key: str) -> dict:
    """
    User info and input fields for project name and template.  
    Generate error message for invalid file name formats.

    Args:
        button_format_key (str):
            format key, setting discrete or highlighted save button
        is_changed_key (str): 
            control key for behavior upon change

    Returns:
        (dict):
            title, file_name, template
    """
    # Title
    col.space(1)
    col.markdown("""**New project:** enter a unique name for project files and display.  
                 Case sensitive: as you EnTeR terms is how they are shown.""")
    entered_title = col.text_input(
        "Project title", 
        key="ui_title", 
        on_change=tools.need_update,
        args=(button_format_key, is_changed_key), 
        help="Name for folder and display", 
        placeholder="e.g. Learning path / Activity log / Collection",
        label_visibility="collapsed")
    # Files - check files if there is a project folder with the name
    root = Path(__file__).resolve().parent.parent
    folder_list = [x.name for x in root.iterdir() if x.is_dir()]
    if st.session_state["ui_title"]:
        project_folder = st.session_state["ui_title"].lower().replace(" ", "_")
        if project_folder in folder_list:
            st.error("A project already exists with that name.")
    
    # Template - check template folder for existing json with the same 
    col.markdown("""Select template setup from previously installed projects   
                 – skips further customization steps.""")
    template_path = root / "templates"
    template_files = [x.name for x in Path(template_path).iterdir() if x.is_file()]
    templates = [None,] + template_files
    # Selecting template sends info directly to submission
    # Clearing template clears submission - Save button then required to submit title
    selected_template = col.selectbox(
        "Templates", options=templates, index=0,
        format_func=lambda x:f"{x}".replace("_", " ").replace(".json", "").title(), 
        key="selected_template", on_change=_set_submission, args=(button_format_key, is_changed_key),
        label_visibility="collapsed")
    st.session_state["checklists"]["project_save"] = [st.session_state["ui_title"],]

    # Validate title name
    # Enforce strict validation, as it is used for folder/file names
    word_is_invalid = tools.symbol_validation(st.session_state["ui_title"], strict=True)
    if word_is_invalid or len(str(st.session_state["ui_title"])) < 1:
        title = None
        st.session_state["title_is_valid"] = False
        if word_is_invalid: col.error(word_is_invalid)
    else:
        title = st.session_state["ui_title"]
        st.session_state["title_is_valid"] = True
        if selected_template: _set_submission(button_format_key, is_changed_key)

    return {
        "ui_title": title,
        "file_name": str(st.session_state["ui_title"]).lower().replace(" ", "_"),
        "template": selected_template}


def _set_submission(button_format_key: str, is_changed_key: str):
    """
    Adapts submission:
    - If template is selected, subission is defined
    - Without template, submission is cleared until Save is pressed

    Args:
        button_format_key (str):
            format key, setting discrete or highlighted save button
        is_changed_key (str): 
            control key for behavior upon change
    """
    if st.session_state["selected_template"]:
        st.session_state["submitted"]["project_details"] = {
            "ui_title": st.session_state["ui_title"],
            "file_name": str(st.session_state["ui_title"]).lower().replace(" ", "_"),
            "template": st.session_state["selected_template"]}
    else:
        st.session_state["submitted"]["project_details"] = {
            "ui_title": None,
            "file_name": None,
            "template": None}
        if st.session_state["ui_title"]:
            tools.need_update(button_format_key, is_changed_key)


def done(set_width):
    with st.container(border=False, key="done", width=set_width, height="content", horizontal_alignment="center"):
        # Header
        # Progress bar
        st.progress(100, width="stretch")
        col_prev, col_reset, col_title, col_apply, col_next = st.columns([2, 2, 5, 2, 2])
        # Title
        col_title.markdown("#### *Done!*", text_alignment="center")
        col_1, col_sp1, col_2, col_sp2, col_3 = st.columns([8, 1, 10, 1, 8])

        col_2.markdown(
            f"#### Project :green[{st.session_state["submitted"]["project_details"]["ui_title"]}] created.", 
            text_alignment="center")
        col_2.markdown("Data files are now in PitySake folder.", text_alignment="center")
        col_2.info("Close the terminal before starting your project or initializing a new project.")


def error(set_width):
    with st.container(border=False, key="error_view", width=set_width, height="content", horizontal_alignment="center"):
        # Header
        # Progress bar
        st.progress(100, width="stretch")
        col_prev, col_reset, col_title, col_apply, col_next = st.columns([2, 2, 5, 2, 2])
        # Title
        col_title.markdown("#### *Something went wrong...*", text_alignment="center")
        col_1, col_sp1, col_2, col_sp2, col_3 = st.columns([8, 1, 10, 1, 8])
        project = st.session_state["submitted"]["project_details"]["file_name"]
        error_details = st.session_state["error"]
        col_2.markdown(f"#### :red[Error!] {error_details["message"]}")
        if error_details["exception"]: exception = error_details["exception"]
        col_2.markdown(f"""{exception}  \nOccurred while {error_details["process"]}""")
        col_2.markdown(f"File details: {error_details["file"]}")
        col_2.markdown(f"""
        - Check files in PitySake folder named :orange[{project}]
        - Try to start the project.
        - If shortcuts are missing, you can start it using {project}.bat
        - If it doesn't work, all files/folders named :orange[{project}] can be removed safely.""")


# Settings
st.set_page_config(page_icon = "../accessories/icon2.ico", layout="wide", initial_sidebar_state="collapsed")
col_page_left, col_page_center, col_page_right = st.columns([1, 12, 1])
init.initialize()

# Build app pages
if st.session_state["initialized"]:
    with col_page_center.container(horizontal_alignment="center"):
        if st.session_state["error"]["state"]:
            error(SET_WIDTH)
        elif st.session_state["registration_complete"]:
            done(SET_WIDTH)
        elif st.session_state["page"] == 0:
            welcome(SET_WIDTH)
        elif st.session_state["page"] == 1:
            define_objects(SET_WIDTH)
        elif st.session_state["page"] == 2:
            define_labels(SET_WIDTH)
        elif st.session_state["page"] == 3:
            define_event_terms(SET_WIDTH)
        elif st.session_state["page"] == 4:
            define_event_limits(SET_WIDTH)
        elif st.session_state["page"] == 5:
            finalize(SET_WIDTH)
    tools.dev_tools(True)




