"""
Registration functions for compiling info and saving to files.

Actions
- dollects info from submission and/or from template file
- defines main file and folder names from project name
- checks conflicts with existing files
- compiles project-unique and independent settings 
  and saves in settings folder as:  
  data_options.json, config.json, ui_themes.json, config.toml 
- in data folder, creates initial tracking file (progress.json) 
  and other data file as empty files
- creates shortcuts and .bat files for start without terminal
"""

import copy
import json
from pathlib import Path
import platform
import shutil

import streamlit as st
import pythoncom
from pyshortcuts import make_shortcut


def register(key: str, use_template: bool = False):
    """
    Controls submission data compiling, generating folders and files for defined project.
    
    Actions:
    - Compiles data for JSON files data_options, config, progress, and themes
    - Defines project info for file/folder environment
    - Writes project files
    - Copies template main py (user_project.py) for new project main py
    - Creates desktop and in-folder shortcuts for new project

    Args:
        key (str):
            button identifier
        use_template (bool):
            controls collection of data from template and saving of new template
    """
    if st.button(
            "**Register**", key=key, type="primary", width="stretch"):
        # Collect and compile submission/template info
        submitted = st.session_state["submitted"]
        if not use_template:
            new_template = True
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
            new_template = False
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
        if new_template: templates_folder = root / "templates"
        streamlit_config_folder = root / ".streamlit"
        log_folder = root / "logs"

        # Define new project environment 
        project_folder = root / file_name
        project_py = root / f"{file_name}.py"
        project_bat = root / f"{file_name}.bat"
        # Prevent overwriting projects
        project_is_vacant = False
        if project_folder in folder_list:
            st.error(f"A project already exists named {title}.")
            name_ok = False
        else:
            name_ok = True
        # Define project subfolders
        backup_folder = project_folder / "backup"
        data_folder = project_folder / "data"
        settings_folder = project_folder / "settings"

        # Establish project environment
        if name_ok:
            try:
                project_folder.mkdir(exist_ok=False)
                backup_folder.mkdir(exist_ok=False)
                data_folder.mkdir(exist_ok=False)
                settings_folder.mkdir(exist_ok=False)
                templates_folder.mkdir(exist_ok=True)
                log_folder.mkdir(exist_ok=True)
                project_is_vacant = True
            except FileExistsError as e:
                quit()

        # Create project files
        if project_is_vacant:
            # Create template
            if not use_template:
                new_template = {
                    "config": copy.deepcopy(config),
                    "data_options": data_options,
                    "progress": progress,
                    "themes": themes
                }
                new_template["config"]["TERMS"][title] = None
                _write(new_template, templates_folder, f"{file_name}.json", check_existing=True)
            # Streamlit config file
            _write(streamlit_config, streamlit_config_folder, "config.toml", file_type="toml")
            # Data folder content
            _write({}, data_folder, "backup_meta.json")
            _write({}, data_folder, "main.json")
            _write(progress, data_folder, "progress.json")
            _write({}, data_folder, "secondary.json")
            # Settings fodler content
            _write(config, settings_folder, "config.json")
            _write(data_options, settings_folder, "data_options.json")
            _write(themes, settings_folder, "ui_themes.json")
            # Create project main module
            shutil.copy(root_py, project_py)
            # Shortcut bat script
            _write(bat_content, root, project_bat, file_type="bat")
            icon_path = root / "accessories/icon1.ico"
            root_shortcut = root
            # Windows shortcuts
            os_name = platform.system()
            if os_name == "Windows":
                pythoncom.CoInitialize()
                make_shortcut(
                    str(project_bat), name=f"{title}.lnk", working_dir=str(root), 
                    icon=str(icon_path), desktop=True)
                make_shortcut(
                    str(project_bat), name=f"{title}.lnk", working_dir=str(root), 
                    icon=str(icon_path), folder=str(root_shortcut))


def _config(terms: dict) -> dict:
    """
    Compiles project confuguration settings file.
    
    Args:
        terms (dict):
            submitted terms from forms

    Returns:
        (dict):
            dict ready for save as config.json
    """
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


def _data_options(terms: dict, submitted: dict) -> dict:
    """
    Compiles project data options settings file.

    Args:
        terms (dict):
            submitted terms from forms 
        submitted (dict):
            submitted info from forms for variable info

    Returns:
        (dict):
            dict ready for save as data_options.json
    """
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
        "source": list(submitted["progress_details"]["sources"].keys()),
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
            "collection_start_count": submitted["objects_details"]["start_from_0"]
        },
        "user_indicators": {
            "reverse_positive": submitted["progress_details"]["switches"]["use_highlights"],
            "reverse_positive": submitted["progress_details"]["switches"]["reverse_positive"],
            "high_highlight": submitted["progress_details"]["high_limit"],
            "low_highlight": submitted["progress_details"]["low_limit"]
        }
    }

    return data_options, progress


def _themes():
    """
    Compiles UI themes settings file.

    Returns:
        (dict):
            dict ready for save as ui_themes.json
    """
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


def _streamlit_config() -> str:
    """
    Compiles Streamlit configuration file.

    Returns:
        (str):
            text ready for save as config.toml
    """
    return """[server]
runOnSave = true
address = "127.0.0.1"

[browser]
gatherUsageStats = false

[theme]
backgroundColor = '#000000'
secondaryBackgroundColor = '#620d5b'
primaryColor = '#ff00a8'
textColor = '#00e8ff'
font = 'sans serif'"""


def _bat(name: str):
    """
    Compiles shortcut script batch file.

    Args:
        name (str):
            project file name

    Returns:
        (str):
            text ready for save as {name}.bat
    """
    return f"""@echo off
streamlit run {name}.py
pause
"""


def _collect_template(template: str) -> dict|bool:
    """
    Load template data for defining new project.

    Args:
        template (str):
            template name
    
    Returns:
        (dict|bool):
            JSON load or False upon exception
    """
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


def _write(data: dict|str, folder: Path, file: str, 
           file_type: str = "json", check_existing: bool = False):
    """
    Write data to defined folder and file type.

    Args:
        data (data|str):
            file content
        folder (Path):
            pathlib object for folder
        file (str)
            file name
        file_type (str):
            identifier for save as .json, .toml, or .bat
        check_existing (bool):
            control for adding _{n} to file name
    """
    file_path = folder / file
    # Most project files SHOULD NOT have a file with the same name existing
    if check_existing:
        if file_path.exists():
            n = 1
            while True:
                file_path = folder / f"{file_path.stem}_{n}{file_path.suffix}"
                if not file_path.exists(): break
                file_path = folder / file
                n += 1
        if file_path.exists():
            file_path = folder
    if file_type == "json":
        with open(file_path, "x", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
    elif file_type == "toml":
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(data)
    elif file_type == "bat":
        with open(file_path, "x", encoding="utf-8") as f:
            f.write(data)