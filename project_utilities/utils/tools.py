import copy
import json
from pathlib import Path
import pythoncom
from pyshortcuts import make_shortcut
import shutil

import streamlit as st

from config import PAGES


def navigate(col_prev=None, col_next=None):
    if not col_prev and not col_next:
        col_prev, col_next = st.columns(2)
    prev_disabled = not st.session_state["page"] > 0
    if col_prev.button("Previous", key=f"prev_page", disabled=prev_disabled, width="stretch"):
        st.session_state["page"] -= 1
        st.rerun()

    page_incomplete = st.session_state["page_incomplete"]
    no_next = st.session_state["page"] == PAGES
    if page_incomplete or no_next:
        next_disabled = True
    else:
        next_disabled = False

    if col_next.button("Next", key=f"nex_page", disabled=next_disabled, width="stretch"):
        st.session_state["page"] += 1
        st.rerun()


def need_update(save_hightlight, changed_setting, all_required=True):
    st.session_state[save_hightlight] = "primary"
    st.session_state[changed_setting] = True
    if all_required:
        st.session_state["page_incomplete"] = True


def apply(key, need_save, is_changed, submission_key, submission, all_required=True):
    save_disabled = True
    if st.session_state[is_changed]:
        if all_required:
            if all(st.session_state["checklists"][key]):
                save_disabled = False
        else:
            save_disabled = False

    st.button(
        "Save", 
        key=key, 
        on_click=submit, 
        args=(need_save, is_changed, submission_key, submission), 
        type=st.session_state[need_save], 
        disabled=save_disabled,
        width="stretch"
    )
    

def submit(save_hightlight, is_changed, submission_key, submission):
    st.session_state[save_hightlight] = "secondary"
    st.session_state[is_changed] = False
    st.session_state["submitted"][submission_key] = submission
    st.session_state["page_incomplete"] = False


def dev_tools():
    
    if st.button("Clear"): clear()
    st.write(st.session_state)


def clear():
    for key in st.session_state.keys():
        del st.session_state[key]
    # st.session_state["cleared"] = True
    st.rerun()


print(Path(__file__).resolve().parent.parent.parent)
def register(key, use_template=False):
    if st.button(
            "Register", 
            key=key, 
            type="primary", 
            width="stretch"):
        
        submitted = st.session_state["submitted"]
        if not use_template:
            terms = {
                "attempt": submitted["event_terms"]["attempt"],
                "attribute": submitted["objects_details"]["attribute"],
                "main": submitted["objects_details"]["main"],
                "negative": submitted["event_terms"]["state_loss"],
                "neutral": submitted["event_terms"]["state_det"],
                "origin": submitted["objects_details"]["origin"],
                "positive": submitted["event_terms"]["state_win"],
                "secondary": submitted["objects_details"]["secondary"],
                "source": submitted["event_terms"]["sources_name"],
                "ui_title": submitted["project_details"]["ui_title"],
                "unit": submitted["progress_details"]["switches"]["unit"],
                "utility": submitted["objects_details"]["utility"]
            }
            # Compile project file contents
            title = terms["ui_title"]
            config = _config(terms)
            data_options, progress = _data_options(terms, submitted)
            themes = _themes()
        else:
            template = _collect_template(submitted["template"])
            config = template["config"]
            data_options = template["data_options"]
            progress = template["progress"]
            themes = template["themes"]
        title = submitted["project_details"]["ui_title"]
        file_name = submitted["project_details"]["file_name"]
        streamlit_config = _streamlit_config()
        bat_content = _bat(file_name)

        # Collect app and project info
        root = Path(__file__).resolve().parent.parent.parent
        root_py = root / "user_project.py"
        folder_list = [x.name for x in root.iterdir() if x.is_dir()]
        templates_folder = root / "templates"
        streamlit_config_folder = root / ".streamlit"

        # Define new project environment 
        project_folder = root / file_name
        project_py = root / f"{file_name}.py"
        project_bat = root / f"{file_name}.bat"
        # Prevent overwriting projects
        project_is_vacant = False
        if project_folder in folder_list:
            st.error("A project already exists with that name.")
            name_ok = False
        else:
            name_ok = True
        # Define project subfolders
        backup_folder = project_folder / "backup"
        data_folder = project_folder / "data"
        settings_folder = project_folder / "settings"

        if name_ok:
            print()
            print("------ Evaluation --------")
            print("project_folder", project_folder)
            print("backup_folder", backup_folder)
            print("data_folder", data_folder)
            print("settings_folder", settings_folder)
            result = {
                "config": config,
                "progress": progress,
                "data_options": data_options,
                "themes": themes
            }
            for x in ["config", "progress", "data_options", "themes"]:
                print()
                print("..............")
                print(f"{x} content:")
                for y, z in result[x].items():
                    if type(z) is dict:
                        print(f"{y}:")
                        for z1, z2 in z.items():
                            print(f"   {z1:20} {z2}")
                    else:
                        print(f"{y:20} {z}")
            print("\nstreamlit_config content:")
            print(streamlit_config)
            print("\nbat_content content:")
            print(bat_content)
            print()
            print("general file name", templates_folder)
            print("root", root)
            print(f"folders:\n   {project_folder},\n   {backup_folder},\n   {data_folder},\n   {settings_folder}\n   {templates_folder}")
            print(f"files\n  copied:\n   {root_py}\n  made:\n   {project_py},\n   {project_bat},\n")
        # name_ok = False
        # Establish project environment
        if name_ok:
            try:
                project_folder.mkdir(exist_ok=False)
                backup_folder.mkdir(exist_ok=False)
                data_folder.mkdir(exist_ok=False)
                settings_folder.mkdir(exist_ok=False)
                templates_folder.mkdir(exist_ok=False)
                project_is_vacant = True
            except FileExistsError as e:
                print(e)
                print(f"A folder with name {file_name} already exists.")
                quit()
        # Create project files
        if project_is_vacant:
            
            if not use_template:
                new_template = {
                    "config": copy.deepcopy(config),
                    "data_options": data_options,
                    "progress": progress,
                    "themes": themes
                }
                new_template["config"]["TERMS"][title] = None
                _write(new_template, templates_folder, file_name)

            _write(streamlit_config, streamlit_config_folder, "config.toml", file_type="toml")

            _write({}, data_folder, "backup_meta.json")
            _write({}, data_folder, "main.json")
            _write(progress, data_folder, "progress.json")
            _write({}, data_folder, "secondary.json")

            _write(config, settings_folder, "config.json")
            _write(data_options, settings_folder, "data_options.json")
            # _write({"theme": "Theme 1"}, project_folder, "meta.json")
            _write(themes, settings_folder, "ui_themes.json")

            # Create project main module
            shutil.copy(root_py, project_py)
            
            _write(bat_content, root, project_bat, file_type="bat")
            # desktop_path = Path.home() / "Desktop"
            # desktop_shortcut = desktop_path / f"{title}.lnk"
            icon_path = root / "accessories/icon1.ico"
            root_shortcut = root
            
            pythoncom.CoInitialize()
            make_shortcut(str(project_bat), name=f"{title}.lnk", working_dir=root, icon=str(icon_path), desktop=True)
            make_shortcut(str(project_bat), name=f"{title}.lnk", working_dir=root, icon=str(icon_path), folder=str(root_shortcut))


def _config(terms):
    return {
        "DIRECTORIES": {
            "BackupFolder": "backup",
            "DataFolder": "data",
            "SettingsFolder": "settings",
            "UIFolder": "settings"
        },
        "SETTINGS": {
            "Options": "data_options.json",
            "Presets": "init_values.json",
            "Validation": "data_validation.json",
            "UISettings": "ui_settings.json",
            "Themes": "ui_themes.json"
        },
        "DATAPATH": {
            "backup_meta": "backup_meta.json",
            f"{terms["main"]}": "main.json",
            f"{terms["secondary"]}": "secondary.json",
            "progress": "progress.json"
        },
        "TERMS": {
            "active_attempts": f"added {terms["attempt"]}",
            "attempt": f"{terms["attempt"]}",
            "attribute": f"{terms["attribute"]}",
            "event": "event",
            "event_calculator": f"{terms["attempt"]} calculator",
            "event_name": f"{terms["source"]}",
            "main": f"{terms["main"]}",
            "origin": f"{terms["origin"]}",
            "progress": f"{terms["attempt"]}",
            "source": f"{terms["source"]}",
            "secondary": f"{terms["secondary"]}",
            "sets": "Rows",
            "state": "Outcome",
            "state_win": f"{terms["positive"]}",
            "state_loss": f"{terms["negative"]}",
            "state_det": f"{terms["neutral"]}",
            "state_det_symbol": "☆",
            "state_rand": "Uncertain",
            "state_rand_symbol": "?",
            "title": "PitySake",
            "unit": terms["unit"],
            "utility": f"{terms["utility"]}",
            "ui_title": f"{terms["ui_title"]}"
        }
    }


def _data_options(terms, submitted):
    progress = dict()
    source_limit = dict()
    states = dict()
    for name, details in submitted["progress_details"]["sources"].items():
        if details["limit"]:
            state = "Uncertain" if details["evaluate"] else None
            progress[name] = {
                terms["attempt"]: 0,
                "State": state,
                "sets": {
                    "pages": 250,
                    "rows": 5
                }
            }
        source_limit[name] = details["limit"]
        states[name] = details["evaluate"]

    data_options = {
        terms["main"]: {
            terms["origin"]: submitted["label_details"]["origin"],
            terms["attribute"]: submitted["label_details"]["attribute"],
            terms["utility"]: submitted["label_details"]["utility"]
        },
        "main_required": {
            terms["origin"]: [],
            terms["attribute"]: [],
            terms["utility"]: []
        },
        "source": list(submitted["progress_details"]["sources"].keys()),
        "source_required": [],
        "results": [
            submitted["event_terms"]["state_win"],
            submitted["event_terms"]["state_loss"],
            submitted["event_terms"]["state_det"]
        ],
        "source_limit": source_limit,
        "states": states,
        "value_limits": {
            "date": [
                None,
                None
            ],
            "collection_start_count": 0
        },
        "user_indicators": {
            "reverse_positive": submitted["progress_details"]["switches"]["reverse_positive"],
            "high_highlight": submitted["progress_details"]["high_limit"],
            "low_highligh": submitted["progress_details"]["low_limit"]
        }
    }

    return data_options, progress


def _themes():
    return {
        "active": "Theme 5",
        "Theme 1": {
            "background": "#040a20",
            "input_field": "#251e2b",
            "highlights": "#bc0083",
            "highlight_text": "#000000",
            "text_color": "#ffffff",
            "main_container": "#020720",
            "feature_header": "#06011c",
            "sub_container": "#01062b",
            "small_widget": "#12022b",
            "positive_color": "#00ff80",
            "neutral_color": "#ae00de",
            "negative_color": "#ff0067",
            "header_switch": True
        },
        "Theme 2": {
            "background": "#1c0420",
            "input_field": "#251e2b",
            "highlights": "#00bc64",
            "highlight_text": "#000000",
            "text_color": "#8dff94",
            "main_container": "#2d0936",
            "feature_header": "#231E2B",
            "sub_container": "#34113C",
            "small_widget": "#460b46",
            "positive_color": "#00ff1a",
            "neutral_color": "#ffffff",
            "negative_color": "#ff0004",
            "header_switch": True
        },
        "Theme 3": {
            "background": "#8fcadc",
            "input_field": "#d1f3e2",
            "highlights": "#9be3ff",
            "highlight_text": "#000000",
            "text_color": "#000000",
            "main_container": "#74bbce",
            "feature_header": "#2da3b5",
            "sub_container": "#78d2ea",
            "small_widget": "#bbdacf",
            "positive_color": "#00ffde",
            "neutral_color": "#000000",
            "negative_color": "#fd4ac7",
            "header_switch": True
        },
        "Theme 4": {
            "background": "#000000",
            "input_field": "#291f24",
            "highlights": "#ff0000",
            "highlight_text": "#000000",
            "text_color": "#ff7110",
            "main_container": "#2b0808",
            "feature_header": "#000000",
            "sub_container": "#460607",
            "small_widget": "#1a0202",
            "positive_color": "#00ff51",
            "neutral_color": "#ff7111",
            "negative_color": "#ff0004",
            "header_switch": True
        },
        "Theme 5": {
            "background": "#000000",
            "input_field": "#620d5b",
            "highlights": "#ff00a8",
            "highlight_text": "#000000",
            "text_color": "#00e8ff",
            "main_container": "#00191a",
            "feature_header": "#000000",
            "sub_container": "#000000",
            "small_widget": "#051212",
            "positive_color": "#00ff1a",
            "neutral_color": "#00e8ff",
            "negative_color": "#ff0004",
            "header_switch": True
        }
    }


def _streamlit_config():
    toml_string = "[server]\nrunOnSave = true\n\n[theme]\nbackgroundColor = '#000000'\nsecondaryBackgroundColor = '#620d5b'\nprimaryColor = '#ff00a8'\ntextColor = '#00e8ff'\nfont = 'sans serif'"

    return toml_string


def _bat(name):
    return f"""@echo off
streamlit run {name}.py
pause
"""


def _collect_template(template):
    try:
        with open(template, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Failed to read file {template}.")
        return False
    except json.JSONDecodeError:
        print(f"File {template} could not be decoded as JSON.")
        return False
    except Exception as e:
        print(e)
        print(f"Failed to read file {template}.")
        return False



def _write(data, folder, file, file_type="json"):
    file_path = folder / file
    if file_type == "json":
        with open(file_path, "x", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
    elif file_type == "toml":
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(data)
    elif file_type == "bat":
        with open(file_path, "x", encoding="utf-8") as f:
            f.write(data)