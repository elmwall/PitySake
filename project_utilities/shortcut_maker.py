import os
import platform
from pyshortcuts import make_shortcut

file_location = os.path.abspath(__file__)
utilities_directory = os.path.dirname(file_location)
root_directory = os.path.dirname(utilities_directory)

project_main = os.path.join(root_directory, "user_project.bat")
accessory_directory = os.path.join(root_directory, "accessories")
project_configuration = os.path.join(utilities_directory, "project_manager.bat")
root_file_list = os.listdir(root_directory)

target_terminal = os.environ.get("COMSPEC", "cmd.exe")
project_args = f'{target_terminal} /k "{project_main}"'
config_args = f'{target_terminal} /k "{project_configuration}"'

os_name = platform.system()
if os_name == "Windows":
    print("OS: Windows")
    print("Creating user project shortcut...")
    project_icon_path = os.path.join(accessory_directory, "icon1.ico")
    # make_shortcut(
    #     project_args, name="User_Project.lnk", working_dir=root_directory, 
    #     icon=str(project_icon_path), terminal=False, desktop=True)
    print("Creating user project shortcut in PitySake/...")
    try:
        make_shortcut(
            str(project_args), name="User_Project.lnk", working_dir=root_directory, 
            icon=str(project_icon_path), folder=root_directory, terminal=False, desktop=False)
    except:
        print(f"Failed to create shortcut for standard User Project")

    print("Creating wizard shortcut in PitySake/...")
    icon_path = os.path.join(accessory_directory, "icon2.ico")
    try:
        make_shortcut(
            str(config_args), name="New_Project.lnk", working_dir=utilities_directory, 
            icon=str(icon_path), folder=root_directory, terminal=False, desktop=False)
    except:
        print(f"Failed to create shortcut for Wizard")
        
    for x in root_file_list:
        file, extension = os.path.splitext(x)
        if extension == ".bat":
            if x not in ["module_installer.bat", "user_project.bat", "clear_cache.bat"]:
                print(f"Creating shortcut for project: {file}")
                try:
                    batfile_args = f'{target_terminal} /k "{x}"'
                    make_shortcut(
                        str(batfile_args), name=f"{file}.lnk", working_dir=root_directory, 
                        icon=str(project_icon_path), folder=root_directory, terminal=False, desktop=False)
                    make_shortcut(
                        str(batfile_args), name=f"{file}.lnk", working_dir=root_directory, 
                        icon=str(project_icon_path), terminal=False, desktop=False)
                except:
                    print(f"Failed to create shortcut for {x}")
        
else:
    print("OS: not Windows. No shortcut made.")