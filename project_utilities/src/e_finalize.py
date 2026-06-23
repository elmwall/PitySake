"""
Page E: Review and register

Guide: show tables with selected settings in context  

Manages:
- Retrieves submitted values and formats information for view
- Directs to registration
"""
import platform

import streamlit as st

from utils import tools
from utils import registration as reg


# Step 5: finalize and save
def finalize(set_width):
    """
    Review page of all submitted options with context associations.
    - save button replaced by register -> sends to registration
    - generates a container with tables for
        - object details: 
            - object categories
            - label categories
            - labels next to their category
        - event logging:
            - value term
            - source term
            - sources with respective settings
        - display:
            - outcomes: positive/negative/neutral terms
            - highlights: low/high threshold
                color indications dependent on reversal enabled
    """
    # Object details
    with st.container(
            border=False, width=set_width, 
            height="stretch", horizontal_alignment="center"):
        # Header
        st.progress(100, width="stretch")
        col_prev, col_space, col_title, col_apply, col_next = st.columns(
            [2, 2, 5, 2, 2])
        tools.navigate(col_prev, col_next)
        submitted = st.session_state["submitted"]
        project = submitted["project_details"]["ui_title"]
        with col_apply:
            reg.register("register")
        col_title.markdown(
            f"#### Finalize Project: {project}", 
            text_alignment="center")
        st.space()
        col_1, col_3 = st.columns([1, 1])
        
        # Build view
        with col_1.container(border=True):
            _summarize_objects(submitted)
        with col_1.container(border=True, height="stretch"):
            _summarize_events(submitted)
        with col_3.container(border=True):
            _summarize_display(submitted)
        with col_3.container(border=True, height="stretch"):
            _summarize_files(submitted, project)
        

def _summarize_objects(submitted):
    "Creates context view of object and label categories."
    # Collect data
    main = submitted["objects_details"]["main"]
    secondary = submitted["objects_details"]["secondary"]
    utility = submitted["objects_details"]["utility"]
    attribute = submitted["objects_details"]["attribute"]
    origin = submitted["objects_details"]["origin"]

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
    labels = dict()
    # Create string lists for labels paired with category
    for x in ["utility", "attribute", "origin"]:
        labels[x] = str()
        for y in registered_labels[x]:
            labels[x] += f"- {y}  \n"
    # Generate table for view as "table column header": list of rows in column
    project_table = {
        "Concept": [
            "Main object", 
            "Secondary object",
            "Label: main & secondary",
            "Label: main only",
            "Label: main only"
        ],
        "Display name": [
            main,
            secondary,
            label_terms['utility'],
            label_terms['attribute'],
            label_terms['origin'],
        ],
        "Details": [
            "Most essential object group",
            "Additional tracked object",
            labels['utility'],
            labels['attribute'],
            labels['origin'],
        ]
    }

    # Build view content
    st.markdown(f"""##### Object details""")
    st.markdown("Names of your objects and their labels store in object database.")
    st.table(project_table, border="horizontal", width="stretch")


def _summarize_events(submitted):
    "Creates context view of value and source terms, and defined sources."
    # Collect info
    progress = submitted["event_terms"]["attempt"]
    sources = submitted["event_terms"]["sources_name"]

    # Generate table
    source_names = list()
    source_limits = list()
    source_evals = list()
    for x, y in submitted["progress_details"]["sources"].items():
        source_names.append(x)
        source_limits.append(y["limit"])
        source_evals.append(y["evaluate"])
    event_table = {
        f":grey[{sources} events]": source_names,
        ":grey[Value range]": source_limits,
        ":grey[Outcome evaluation]": source_evals
    }

    # Build view content
    st.markdown("##### Event data logging")
    st.markdown(f"""
        Object event data can be recorded with a value named '{progress}'.   
        Events are categorized by {sources}s:""")

    st.table(event_table, border="horizontal", width="stretch")


def _summarize_display(submitted):
    "Creates context view of outcome names and highlight settings."
    # Collect data
    positive = submitted["event_terms"]["state_win"]
    negative = submitted["event_terms"]["state_loss"]
    neutral = submitted["event_terms"]["state_det"]
    use_highlights = submitted["progress_details"]["switches"]["use_highlights"]
    
    # Generate tables
    # - Outcomes
    outcome_table = {
        "Outcome": [
            ":green['Positive']",
            "'Neutral'",
            ":red['Negative']",
        ],
        "Display name": [
            positive,
            neutral,
            negative
        ],
        "Comment": [
            "For 'positive' evaluations",
            "For 'neutral' evaluations",
            "For 'negative' evaluations"
        ]
    }
    # - Highlights
    if use_highlights:
        reverse_positive = submitted["progress_details"]["switches"]["reverse_positive"]
        high_value = submitted["progress_details"]["high_limit"]
        low_value = submitted["progress_details"]["low_limit"]
        if reverse_positive:
            high_statement, low_statement = ":red['negative']", ":green['positive']"
        else:
            high_statement, low_statement = ":green['positive']", ":red['negative']"
        highlight_table = {
            "Category": [
                "Low values",
                "Mid values",
                "High values"
            ],
            "Threshold": [
                f"up to {low_value}",
                f"between {low_value} and {high_value}",
                f"from {high_value}"
            ],
            "Highlight": [
                f"Marked as {low_statement}",
                "No highlight",
                f"Marked as {high_statement}"
            ]
        }
    unit = submitted["progress_details"]["switches"]["unit"]

    # Build view content
    # - Outcomes
    st.markdown("##### Display method")
    st.markdown("Terms and indicators displayed for values")
    st.markdown("Outcome evaluation")
    st.table(outcome_table, border="horizontal", width="stretch")
    # - Highlights
    st.markdown("Value highlights")
    if use_highlights:
        st.table(highlight_table, border="horizontal", width="stretch")
    else:
        st.markdown("- You have disabled highlights - timeline values will not be color coded")
    if unit: 
        st.markdown(f"""Set unit: {unit}, values will be displayed as e.g. 300{unit}""")

def _summarize_files(submitted, project):
    "Creates context view of project name and derived folders/files."
    # Collect data
    file = submitted["project_details"]["file_name"]
    
    # Generate table
    file_table = {
        "Entity": [
            "Folder",
            "Launch file"
        ],
        "Path/FileName": [
            f"PitySake/{file}/",
            f"{file}.bat"
        ],
        "Comment": [
            "Location of project data",
            "Launches this project"
        ]                
    }
    os_name = platform.system()
    if os_name == "Windows":
        file_table["Entity"].append("Shortcuts")
        file_table["Path/FileName"].append(
            f"Desktop/{project.replace(" ", "_")}  \nPitySake/{project.replace(" ", "_")}")
        file_table["Comment"].append("Shortcut to launch file")

    # Build view content
    st.markdown(f"""##### File structure""")
    st.markdown("Where your files and data will be located.")
    st.table(file_table, border="horizontal", width="stretch")