import os
from pyshortcuts import make_shortcut

utilities_directory = os.path.dirname(
    os.path.abspath(__file__))
root_directory = os.path.dirname(utilities_directory)

quick_start = "user_project.py"
# utilities_directory = os.path.join(current_directory, "project_utilities")
accessory_directory = os.path.join(root_directory, "accessories")
project_configuration = os.path.join(utilities_directory, "project_manager.bat")
root_file_list = os.listdir(root_directory)

# if not "User_Project.lnk" in root_file_list:
#     print("not up")
# else:
#     print("up!")
# if not "New_Project.lnk" in root_file_list:
#     print("not np")
# else:
#     print("np!")

print("Creating user project desktop shortcut...")
project_icon_path = os.path.join(accessory_directory, "icon1.ico")
make_shortcut("user_project.py", name="User_Project.lnk", working_dir=root_directory, icon=str(project_icon_path), desktop=True)
if not "User_Project.lnk" in root_file_list:
    print("Creating user project shortcut in PitySake/...")
    make_shortcut("user_project.py", name="User_Project.lnk", working_dir=root_directory, icon=str(project_icon_path), folder=root_directory, desktop=False)
if not "New_Project.lnk" in root_file_list:
    print("Creating wizard shortcut in PitySake/...")
    icon_path = os.path.join(accessory_directory, "icon2.ico")
    make_shortcut(project_configuration, name="New_Project.lnk", working_dir=utilities_directory, icon=str(icon_path), folder=root_directory, desktop=False)