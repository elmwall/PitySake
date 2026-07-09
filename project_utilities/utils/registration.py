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
import os
from pathlib import Path
import platform
import shutil

import streamlit as st

os_name = platform.system()
if os_name == "Windows":
    import pythoncom
    from pyshortcuts import make_shortcut


def register(key: str, disable: bool = False, use_template: bool = False):
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
            "**Register**", key=key, type="primary", disabled=disable, width="stretch"):
        error = False
        # Collect and compile submission/template info
        submitted = st.session_state["submitted"]
        root = Path(__file__).resolve().parent.parent.parent
        templates_folder = root / "templates"
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
            template_path = templates_folder / submitted["project_details"]["template"]
            template = _collect_template(template_path)
            if template:
                config = template["config"]
                data_options = template["data_options"]
                progress = template["progress"]
                themes = template["themes"]
            else:
                st.rerun()
        title = submitted["project_details"]["ui_title"]
        if use_template: config["TERMS"]["ui_title"] = title
        file_name = submitted["project_details"]["file_name"]
        streamlit_config = _streamlit_config()
        bat_content = _bat(file_name)

        # Collect app and project info
        root_py = root / "user_project.py"
        folder_list = [x.name for x in root.iterdir() if x.is_dir()]
        streamlit_config_folder = root / ".streamlit"
        log_folder = root / "logs"

        # Define new project environment 
        project_folder = root / file_name
        project_py = root / f"{file_name}.py"
        project_bat = root / f"{file_name}.bat"
        # Prevent overwriting projects
        project_is_vacant = False
        if project_folder in folder_list:
            error = True
            msg = f"A project already exists named {title}."
            e = None
            _errors(e, "creating folder", f"In {project_folder}", msg, call_stop=True)
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
                if new_template: templates_folder.mkdir(exist_ok=True)
                log_folder.mkdir(exist_ok=True)
                project_is_vacant = True
            except FileExistsError as e:
                error = True
                msg = "A folder already exists."
                _errors(e, "creating folder", f"In {project_folder}", msg, call_stop=True)
            except Exception as e:
                error = True
                msg = "A folder could not be created."
                _errors(e, "creating folder", f"In {project_folder}", msg, call_stop=True)

        if error:
            return

        # Create project files
        if project_is_vacant:
            # Create template
            if not use_template:
                template_config = copy.deepcopy(config)
                template_config["TERMS"]["ui_title"] = None
                new_template = {
                    "config": copy.deepcopy(config),
                    "data_options": data_options,
                    "progress": progress,
                    "themes": themes
                }
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
            # Windows hortcuts
            os_name = platform.system()
            if os_name == "Windows":
                place = ""
                try:
                    target_terminal = os.environ.get("COMSPEC", "cmd.exe")
                    terminal_path = Path(target_terminal)
                    project_args = f'{terminal_path} /k "{project_bat}"'
                    # Required for creating shortcut on Windows while using Path
                    # without it, it may cause "CoInitialize has not been called"
                    pythoncom.CoInitialize()
                    place = "on desktop"
                    make_shortcut(
                        str(project_args), name=f"{title}.lnk", working_dir=str(root), 
                        icon=str(icon_path), desktop=True)
                    place = "in folder"
                    make_shortcut(
                        str(project_args), name=f"{title}.lnk", working_dir=str(root), 
                        icon=str(icon_path), folder=str(root_shortcut))
                except Exception as e:
                    error = True
                    msg = "Shortcut could not be created."
                    _errors(e, "creating shortcut", f"creating shortcut {place}", msg)
            st.session_state["registration_complete"] = True
            st.rerun()


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
            value = 0
            sets = {
                "sections": 250,
                "positions": 5
            }
        else:
            value = None
            sets = None
            
        state = "Uncertain" if details["evaluate"] else None
        progress[name] = {
            terms["attempt"]: value,
            "State": state,
            "active": True,
            "sets": sets
        }
        source_limit[name] = details["limit"]
        states[name] = details["evaluate"]

    collection_start_count = 0 if submitted["objects_details"]["start_from_0"] else 1
    none_value = "_Blank_"
    data_options = {
        terms["main"]: {
            terms["origin"]: [x if x else none_value for x in submitted["label_details"]["origin"]],
            terms["attribute"]: [x if x else none_value for x in submitted["label_details"]["attribute"]],
            terms["utility"]: [x if x else none_value for x in submitted["label_details"]["utility"]]
        },
        "results": [
            submitted["event_terms"]["state_win"],
            submitted["event_terms"]["state_det"],
            submitted["event_terms"]["state_loss"]
        ],
        "source_limit": source_limit,
        "states": states,
        "value_limits": {
            "date": [
                None,
                None
            ],
            "collection_start_count": collection_start_count
        },
        "user_indicators": {
            "use_highlights": submitted["progress_details"]["switches"]["use_highlights"],
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
        "active": "Theme 1",
        "Theme 1": {
            "background": "#161616",
            "input_field": "#3e4646",
            "highlights": "#2fda1b",
            "highlight_text": "#000000",
            "text_color": "#baffd2",
            "main_container": "#112525",
            "main_gradient": "#0e171a",
            "sub_container": "#0e171a",
            "small_widget": "#182325",
            "positive_color": "#3cd827",
            "neutral_color": "#81b2b7",
            "negative_color": "#d66627",
            "header_switch": True
        },
        "Theme 2": {
            "background": "#d2d2d2",
            "input_field": "#dadada",
            "highlights": "#027fc3",
            "highlight_text": "#ffffff",
            "text_color": "#000000",
            "main_container": "#c5c5c5",
            "main_gradient": "#d2d2d2",
            "sub_container": "#d4d4d4",
            "small_widget": "#d8d8d8",
            "positive_color": "#01ad57",
            "neutral_color": "#000000",
            "negative_color": "#c3023b",
            "header_switch": True
        },
        "Theme 3": {
            "background": "#021923",
            "input_field": "#034856",
            "highlights": "#7cffb9",
            "highlight_text": "#000000",
            "text_color": "#d4e6f3",
            "main_container": "#031d2b",
            "main_gradient": "#082837",
            "sub_container": "#082837",
            "small_widget": "#032735",
            "positive_color": "#05dc3a",
            "neutral_color": "#86bada",
            "negative_color": "#cb3c00",
            "header_switch": True
        },
        "Theme 4": {
            "background": "#000000",
            "input_field": "#291f1f",
            "highlights": "#ff0000",
            "highlight_text": "#000000",
            "text_color": "#ff7110",
            "main_container": "#2b0808",
            "main_gradient": "#390304",
            "sub_container": "#460607",
            "small_widget": "#1a0202",
            "positive_color": "#00ff51",
            "neutral_color": "#ff7111",
            "negative_color": "#ff0004",
            "header_switch": True
        },
        "Theme 5": {
            "background": "#000000",
            "input_field": "#41183d",
            "highlights": "#ff00a8",
            "highlight_text": "#000000",
            "text_color": "#00e8ff",
            "main_container": "#00191a",
            "main_gradient": "#000f10",
            "sub_container": "#000000",
            "small_widget": "#051212",
            "positive_color": "#7dff00",
            "neutral_color": "#00e8ff",
            "negative_color": "#ff00a8",
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

[client]
toolbarMode = "minimal"

[browser]
gatherUsageStats = false

[logger]
level = "warning"

[theme]
backgroundColor = '#000000'
secondaryBackgroundColor = '#620d5b'
primaryColor = '#ff00a8'
textColor = '#00e8ff'
font = 'sans serif'"""


def _bat(name: str, dev: bool = False):
    """
    Compiles shortcut script batch file.

    Args:
        name (str):
            project file name

    Returns:
        (str):
            text ready for save as {name}.bat
    """
    if dev:
        prefix = ""
    else:
        prefix = ".venv\\Scripts\\python.exe -m "
    
    return f"""@echo off
{prefix}streamlit run {name}.py
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
    except FileNotFoundError as e:
        msg = f"Failed to read file {template}."
        print(msg)
        _errors(e, "Collecting template", template, msg, call_stop=True)
        return False
    except json.JSONDecodeError as e:
        msg = f"File {template} could not be decoded as JSON."
        print(msg)
        _errors(e, "Collecting template", template, msg, call_stop=True)
        return False
    except Exception as e:
        msg = f"Failed to read file {template}."
        print(e)
        print(msg)
        _errors(e, "collecting template", template, msg, call_stop=True)
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
        try: 
            with open(file_path, "x", encoding="utf-8") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
        except FileExistsError as e:
            msg = f"File '{file} already exists.'"
            _errors(e, "writing JSON file", file_path, msg)
        except Exception as e:
            msg = f"Could not create file '{file}.'"
            _errors(e, "writing JSON file", file_path, msg)
    elif file_type == "toml":
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(data)
        except Exception as e:
            msg = f"Could not create file '{file}.'"
            _errors(e, "writing TOML file", file_path, msg)
    elif file_type == "bat":
        try:
            with open(file_path, "x", encoding="utf-8") as f:
                f.write(data)
        except FileExistsError as e:
            msg = f"File '{file} already exists.'"
            _errors(e, "writing batch file", file_path, msg)
        except Exception as e:
            msg = f"Could not create file '{file}.'"
            _errors(e, "writing batch file", file_path, msg)


def _errors(exception, file, process, msg, call_stop=False):
    st.session_state["error"] = {
        "state": True,
        "process": process,
        "file": file,
        "message": msg,
        "exception": exception
    }
    if call_stop: st.rerun()