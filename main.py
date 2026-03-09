import os

from file_manager import Archivist
from settings.config import PATHWAYS, TERMS
from info_manager import Librarian
from input_controller import Negotiator



def main(library, object_type, action_selection, event_term):
    """
    Call function for adding, deleting or updating entry.
    Calls functions for backup, to add updated info to previous data and to save file.
    """
    
    static_check = False
    data_option_key = object_type
    print("-"*50)
    # Specify keys for specifik actions:
    # - enter remove/rename/correct to perform action on database entry
    # - enter a unique name to create a new database entry
    msg_remove, msg_change, msg_correction = "Remove", "Rename", "Correct"
    if action_selection==reg_event:
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
    while True:
        name = negotiator.request_word(user_prompt, "Enter selection").title()
        delete_check, change_name, edit_info = [name == x for x in [msg_remove, msg_change, msg_correction]]
        if action_selection==reg_event:
            break
        elif name in library.keys(): 
            user_prompt += f"\n{name} is already in library."
        else:
            break
    # Specifications regarding object and details to edit
    if any([delete_check, change_name, edit_info]):
        message = str()
        while True:
            rename = negotiator.request_word(
                f"You requested to {name.lower()} an object in {object_type.lower()} database.\n{message}", 
                f"Enter EXISTING name in database to {name.upper()}").title()
            if rename not in library.keys():
                message += f"\nNo {object_type} named {rename} in library."
            else:
                name = rename
                break
    if edit_info:
        edit_selection = negotiator.listed_options(
            f"To edit details regarding {name} you need to re-enter part of the info.", 
            ["Basic info", event_term])
        data_option_key = event_term if edit_selection==event_term else object_type       
    elif action_selection==reg_event: data_option_key = event_term
    data_options = librarian.collect_settings(data_option_key)

    # Data gathering
    # Switch between remove, enter new object, or add/change data to existing object
    if delete_check or change_name:
        new_object = None
        if change_name:
            message = str()
            while True:
                change_name = negotiator.request_word(
                    f"Renaming {name}\n{message}", 
                    f"Enter NEW name").title()
                if change_name in library.keys():
                    message += f"\nThe name {change_name} is already taken."
                else:
                    break
    elif action_selection==reg_event:
        new_object = librarian.enter_event(name, data_options, object_type, event_term)
    else:
        # Option to change entry info without removing events
        if edit_info:
            new_object = librarian.edit_data(name, library, object_type, data_options, edit_selection, event_term)
            static_check = True
        else: new_object = librarian.enter_data(name, data_options)

    # Backup interval. E.g. [30, 10, 2] performs backups every 2nd, 10th, and 30th update.
    backup_frequency = [30, 10, 2]
    
    if action_selection==reg_event or edit_info: static_check = True
    
    # Performing backup and joining data with library data before writing to file
    if arciv.backup(negotiator, backup_frequency, object_type[:6]+"_data"): 
        updated_library, action_performed = arciv.join_data(new_object, name, delete_check, change_name, static=static_check)
    if updated_library:
        arciv.writer(updated_library)
        print(f"\nLibrary updated, {action_performed}!\n")
    
# Library print/report generator
def review(library, file, object_type):
    action_selection = negotiator.listed_options(
        f"Select view option for printing data:", 
        [f"By {object_type}", "By date"])
    
    # TODO: add option to select file format
    report = librarian.reciter(library, object_type, action_selection, file)
    if action_selection == f"By {object_type}":
        report_name = f"{object_type} report"
    else:
        report_name = f"{object_type} report date"
    arciv.save_report(report, report_name)
    quit()


# Class:
# Option displayer/collector
negotiator = Negotiator()

# User input for program selection:
# Select object type and action ==> Load settings and file via configuration data
char = TERMS["Character"]
tool = TERMS["Tool"]
misc = TERMS["Misc"]
types = [char, tool, misc]
object_type = negotiator.listed_options(
    "Select object type", 
    [char, misc, tool])
event_term = TERMS[f"{object_type} event"]
filepath = PATHWAYS[object_type]
file = os.path.join(PATHWAYS["DataFolder"], filepath)

# Class:
# File/backup management
arciv = Archivist(PATHWAYS, file)
# Information collection and management
librarian = Librarian(arciv, negotiator)

read_lib, edit_lib, reg_event = "Check library", "Edit library", "Register event"
action_selection = negotiator.listed_options(
    "Select action among:",
    [read_lib, edit_lib, reg_event])
option_list = list()
library = arciv.reader()

# Check library and quit, 
# or prepare function configurations for data collection
if action_selection == read_lib:
    review(library, file, object_type)
else:
    main(library, object_type, action_selection, event_term)




