import os
# import platform
from pyshortcuts import make_shortcut

file_location = os.path.abspath(__file__)
utilities_directory = os.path.dirname(file_location)
root_directory = os.path.dirname(utilities_directory)

project_main = os.path.join(root_directory, "user_project.bat")
accessory_directory = os.path.join(root_directory, "accessories")
project_configuration = os.path.join(utilities_directory, "project_manager.bat")
root_file_list = os.listdir(root_directory)

# os_name = platform.system()
# if os_name == "Windows":
    # print("OS: Windows")
print("Creating user project desktop shortcut...")
project_icon_path = os.path.join(accessory_directory, "icon1.ico")
make_shortcut(
    project_main, name="User_Project.lnk", working_dir=root_directory, 
    icon=str(project_icon_path), desktop=True)
if not "User_Project.lnk" in root_file_list:
    print("Creating user project shortcut in PitySake/...")
    make_shortcut(
        project_main, name="User_Project.lnk", working_dir=root_directory, 
        icon=str(project_icon_path), folder=root_directory, desktop=False)
if not "New_Project.lnk" in root_file_list:
    print("Creating wizard shortcut in PitySake/...")
    icon_path = os.path.join(accessory_directory, "icon2.ico")
    make_shortcut(
        project_configuration, name="New_Project.lnk", working_dir=utilities_directory, 
        icon=str(icon_path), folder=root_directory, desktop=False)
# else:
#     print("OS: not Windows. No shortcut made.")