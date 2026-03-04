import os

from file_manager import Archivist
from settings.config import PATHWAYS, TERMS
from info_manager import Librarian
from input_controller import Negotiator


def main(object_type, datatype, data_options, update_check):
    """
    Call function for adding, deleting or updating entry.
    Calls functions for backup, to add updated info to previous data and to save file.
    """

    print("-"*50)

    # Specify name, the main key for locating its data later.
    # Enter "remove" to delete previous entry.
    name = input(f"Enter {object_type.lower()} name: ").title()

    # Switch between remove, enter new object, or add event data to existing object
    if name == "Remove":
        new_object = None
    elif update_check:
        new_object = librarian.enter_event(name, data_options, object_type==TERMS["Misc"])
    else:
        library = arciv.reader()
        # Option to change entry info without removing events
        if name in library.keys():
            update_check = negotiator.listed_options(
                f"{name} is already in library.\nDo you wish to update details for {name}?", 
                ["Yes"])
            new_object = {name: library[name]}
            new_object[name].update(librarian.enter_data(name, data_options)[name])
        else:
            new_object = librarian.enter_data(name, data_options)

    # Backup interval 
    # Number from biggest to smallest interval. Decides at which update interval backup is performed. E.g. [30, 10, 2] performs backups every 2nd, 10th, and 30th update.
    backup_frequency = [30, 10, 2]

    # Performing backup and joining data with library data before writing to file
    if arciv.backup(negotiator, backup_frequency, datatype): # Backup prior to file changes.
        updated_library = arciv.join_data(new_object, name, update=update_check)
    if updated_library:
        arciv.writer(updated_library)
        print(f"\nLibrary updated with {name}!\n")


# Class:
# Option displayer/collector
negotiator = Negotiator()

# User input for program selection:
# Select object type and action ==> Load settings and file via configuration data
char = "Character"
tool = "Tool"
misc = "Misc"
types = [char, tool, misc]
object_type = negotiator.listed_options(
    "Select object type", 
    [TERMS[char], TERMS[misc], TERMS[tool]])
for x in types:
    if object_type == TERMS[x]: 
        filepath = PATHWAYS[x]
        datatype = x + "_data"
file = os.path.join(PATHWAYS["DataFolder"], filepath)

# Class:
# File/backup management
arciv = Archivist(PATHWAYS, file)
# Information collection and management
librarian = Librarian(arciv, negotiator)

check_lib = "Check library"
update_lib = "Update library"
update_check = "Register event"
action_selection = negotiator.listed_options(
    "Select action among:",
    [check_lib, update_lib, update_check])
option_list = list()

# Check library and quit, 
# or prepare function configurations for data collection
if action_selection == check_lib:
    action_selection = negotiator.listed_options(
        f"Select view option for printing data:", 
        [f"By {object_type}", "By date"])
    library = arciv.reader()
    report = librarian.reciter(library, object_type, action_selection, file)
    if action_selection == f"By {object_type}":
        report_name = f"{object_type} report"
    else:
        report_name = f"{object_type} report date"
    arciv.save_report(report, report_name)
    quit()
elif action_selection == update_lib:
    option_list.append(object_type)
elif action_selection == update_check:
    if object_type != TERMS[misc]:
        option_list.append(TERMS["Event"])
    else:
        option_list.append(TERMS["Collection"])
event_options = librarian.collect_settings(option_list)

main(object_type, datatype, event_options, action_selection==update_check)




