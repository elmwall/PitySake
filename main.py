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
    # Specify keys for specifik actions:
    # - enter remove/rename/correct to perform action on database entry
    # - enter a unique name to create a new database entry
    msg_remove, msg_change, msg_correction = "Remove", "Rename", "Correct"
    if update_check:
        user_prompt = f"Enter name of {object_type} to register new {TERMS["Event"].lower()}"
    else:
        space = 15
        user_prompt = (f"Options for editing library\n"
                       f"\nTo edit existing {object_type.lower()}, type:"
                       f"\n  {msg_remove.lower():{space}} to remove an entry"
                       f"\n  {msg_change.lower():{space}} to edit entry name"
                       f"\n  {msg_correction.lower():{space}} to edit entry info\n"
                       f"\nTo add new: type the name of the new {object_type.lower()}.")
    # Specify modification action or name - the main key for locating its data later.
    name = negotiator.request_word(user_prompt, "Enter selection").title()
    delete_check, change_name, edit_info = [name == x for x in [msg_remove, msg_change, msg_correction]]
    # If modification action: specify object for modification
    if any([delete_check, change_name, edit_info]):
        name = negotiator.request_word(
            f"You requested to {name.lower()} an object in {object_type.lower()} database.", 
            f"Enter EXISTING name in database to {name.upper()}").title()
    
    # Switch between remove, enter new object, or add/change data to existing object
    if delete_check or change_name:
        new_object = None
        if change_name:
            change_name = negotiator.request_word(
                f"To change name of {name}:", 
                f"Enter NEW name").title()
    elif update_check:
        is_misc = object_type==TERMS["Misc"]
        new_object = librarian.enter_event(name, data_options, is_misc)
    else:
        library = arciv.reader()
        # Option to change entry info without removing events
        if edit_info:
            option_list.clear()
            option_list.append(TERMS["Event"])
            data_options = librarian.collect_settings(option_list)
            print(data_options)
            # quit()
            action_selection = negotiator.listed_options(
                f"To edit details regarding {name} you need to re-enter part of the info.", 
                [f"Basic info", f"{TERMS["Event"]}"])
            new_object = librarian.edit_data(name, library, object_type, data_options, action_selection)
            update_check = True
        else: new_object = librarian.enter_data(name, data_options)

    # Backup interval 
    # Number from biggest to smallest interval. Decides at which update interval backup is performed. E.g. [30, 10, 2] performs backups every 2nd, 10th, and 30th update.
    backup_frequency = [30, 10, 2]
    # Performing backup and joining data with library data before writing to file
    print(update_check)
    if arciv.backup(negotiator, backup_frequency, datatype): # Backup prior to file changes.
        updated_library, action_performed = arciv.join_data(new_object, name, delete_check, change_name, update=update_check)
    if updated_library:
        arciv.writer(updated_library)
        print(f"\nLibrary updated, {action_performed}!\n")
    


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
data_options = librarian.collect_settings(option_list)

main(object_type, datatype, data_options, action_selection==update_check)




