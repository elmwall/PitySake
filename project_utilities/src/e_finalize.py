import streamlit as st

from utils import tools


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
        submitted = st.session_state["submitted"]
        project = submitted["project_details"]["ui_title"]
        with col_apply:
            tools.register("register")
        col_title.markdown(
            f"#### Finalize Project: {project}", 
            text_alignment="center")
        st.space()
        col_1, col_3 = st.columns([1, 1])
        with col_1.container(border=True):
            _summarize_objects(submitted)
        with col_1.container(border=True, height="stretch"):
            _summarize_events(submitted)
        with col_3.container(border=True):
            _summarize_display(submitted)
        with col_3.container(border=True, height="stretch"):
            _summarize_files(submitted, project)
        

def _summarize_objects(submitted):
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

    st.markdown(f"""##### Object details""")
    st.markdown("Names of your objects and their labels store in object database.")
    labels = dict()

    for x in ["utility", "attribute", "origin"]:
        labels[x] = str()
        for y in registered_labels[x]:
            labels[x] += f"- {y}  \n"
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
    st.table(project_table, border="horizontal", width="stretch")


def _summarize_events(submitted):
    progress = submitted["event_terms"]["attempt"]
    sources = submitted["event_terms"]["sources_name"]
    st.markdown("##### Event data logging")
    st.markdown(f"""
        Object event data can be recorded with a value named '{progress}'.   
        Events are categorized by {sources}s:""")
    source_names = f":grey[{sources} events]  \n"
    sources_limit = ":grey[Value range]  \n"
    sources_eval = ":grey[Outcome evaluation]  \n"

    for x, y in submitted["progress_details"]["sources"].items():
        source_names += f"{x}  \n"
        if y["limit"]: 
            range = f"0–{y["limit"]}  \n"
        else:
            range = "No values  \n"
        sources_limit += range
        statement = "Yes" if y["evaluate"] else "No"
        sources_eval += f"{statement}  \n"

    c1, c2, c3 = st.columns([5, 2, 3])
    c1.markdown(source_names)
    c2.markdown(sources_limit)
    c3.markdown(sources_eval)


def _summarize_display(submitted):
    positive = submitted["event_terms"]["state_win"]
    negative = submitted["event_terms"]["state_loss"]
    neutral = submitted["event_terms"]["state_det"]
    use_highlights = submitted["progress_details"]["switches"]["use_highlights"]
    if use_highlights:
        reverse_positive = submitted["progress_details"]["switches"]["reverse_positive"]
        high_value = submitted["progress_details"]["high_limit"]
        low_value = submitted["progress_details"]["low_limit"]
    unit = submitted["progress_details"]["switches"]["unit"]
    
    st.markdown("##### Display method")
    st.markdown("Terms and indicators displayed for values")
    st.markdown("Outcome evaluation")
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
    st.table(outcome_table, border="horizontal", width="stretch")
    st.markdown("Value highlights")
    if use_highlights:
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
        st.table(highlight_table, border="horizontal", width="stretch")
    else:
        st.markdown("- You have disabled highlights - timeline values will not be color coded")
    print(type(unit) is str)
    if unit: 
        st.markdown(f"""Set unit: {unit}, values will be displayed as e.g. 300{unit}""")

def _summarize_files(submitted, project):
    file = submitted["project_details"]["ui_title"].replace(" ", "_")
    st.markdown(f"""##### File structure""")
    st.markdown("Where your files and data will be located.")
    file_table = {
        "Entity": [
            "Shortcut",
            "Launch file",
            "Folder"
        ],
        "Path/FileName": [
            f"PitySake/{project}",
            f"{file}.bat",
            f"PitySake/{file}/"
        ],
        "Comment": [
            "Shortcut to launch file",
            "Launches this project",
            "Location of project data"
        ]                
    }
    st.table(file_table, border="horizontal", width="stretch")