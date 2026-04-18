import os
import json
import csv

from app import Administrator, Archivist, Librarian, Mathematician, Negotiator
# from settings.config import TERMS, DIRECTORIES, DATAPATH, SETTINGS

is_demo = True
if is_demo:
    from demo_settings.config import TERMS, DIRECTORIES, DATAPATH, SETTINGS
else:
    from settings.config import TERMS, DIRECTORIES, DATAPATH, SETTINGS



def initialize():
    if not os.path.exists(DIRECTORIES["DataFolder"]): os.makedirs(os.path.dirname(DIRECTORIES["DataFolder"]), exist_ok=True)
    for path in DATAPATH.keys():
        datafile = os.path.join(DIRECTORIES["DataFolder"], DATAPATH[path])
        if not os.path.exists(datafile):
            ext = os.path.splitext(datafile)[1]
            if ext == ".json":
                with open(datafile, "w", encoding="utf-8") as f:
                    json.dump({}, f, indent=4)
                print(f"{datafile} created.")
            elif ext == ".csv":
                with open(datafile, "w", newline="", encoding="utf-8") as f:
                    writer = csv.writer(f)
                    writer.writerow(["none"])
                print(f"{datafile} created")
    print("Initialized!\n")



def main(library, object_type, action_selection, event_term):
    """
    Call function for adding, deleting or updating entry.
    Calls functions for backup, to add updated info to previous data and to save file.
    """
    
    is_static_data = False
    data_option_key = object_type
    print("-"*50)
    # Specify keys for specifik actions:
    # - enter remove/rename/correct to perform action on database entry
    # - enter a unique name to create a new database entry
    msg_remove, msg_change, msg_correction = "Remove", "Rename", "Correct"
    if action_selection == "Register event":
        user_prompt = f"Enter name of {object_type} to register new {TERMS["Event"].lower()}"
    else:
        space = 15
        user_prompt = (f"Options for editing library\n"
                       f"\nTo edit existing {object_type.lower()}, type:"
                       f"\n  {msg_remove.lower():{space}} to remove an entry"
                       f"\n  {msg_change.lower():{space}} to edit entry name"
                       f"\n  {msg_correction.lower():{space}} to correct entry info\n"
                       f"\nTo add new: type the name of the new {object_type.lower()}.")
        
    # Specify modification action or name - the main key for locating its data later.
    while True:
        name = negotiator.request_word(user_prompt, "Enter selection").title()
        for_deletion, for_renaming, for_correction = [name == x for x in [msg_remove, msg_change, msg_correction]]
        if action_selection == "Register event":
            break
        elif name in library.keys(): 
            user_prompt += f"\n{name} is already in library."
        else:
            break
    # Specifications regarding object and details to edit
    if any([for_deletion, for_renaming, for_correction]):
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
    if for_correction:
        edit_selection = negotiator.listed_options(
            f"To edit details regarding {name} you need to re-enter part of the info.", 
            ["Basic info", event_term])
        data_option_key = event_term if edit_selection==event_term else object_type
    elif action_selection == "Register event": data_option_key = event_term
    data_options = librarian.collect_settings(data_option_key)

    # Data gathering
    # Switch between remove, enter new object, or add/change data to existing object
    if for_deletion or for_renaming:
        new_object = None
        if for_renaming:
            message = str()
            while True:
                for_renaming = negotiator.request_word(
                    f"Renaming {name}\n{message}", 
                    f"Enter NEW name").title()
                if for_renaming in library.keys():
                    message += f"\nThe name {for_renaming} is already taken."
                else:
                    break
    elif action_selection == "Register event":
        new_object = librarian.enter_event(name, data_options, object_type, event_term)
    else:
        # Option to change entry info without removing events
        if for_correction:
            new_object = librarian.edit_data(mathemate, name, library, object_type, data_options, edit_selection, event_term)
            is_static_data = True
        else: new_object = librarian.enter_data(mathemate, name, data_options)

    # Backup interval. E.g. [30, 10, 2] performs backups every 2nd, 10th, and 30th update.
    backup_frequency = [30, 10, 2]
    # Datalength not expected to change for adding event to object ==> set static for data validation
    if action_selection == "Register event" or for_correction: is_static_data = True
    
    # Performing backup and joining data with library data before writing to file
    if arciv.backup(negotiator, backup_frequency, object_type[:6]+"_data"): 
        updated_library, action_verification = arciv.join_data(new_object, name, for_deletion, for_renaming, is_static=is_static_data)
    if updated_library:
        arciv.writer(updated_library)
        print(f"\nLibrary updated, {action_verification}!\n")
    

# Library print/report generator
def review(library, file, object_type):
    """
    Generate readable print and report file, or generate CSV file for importing to other systems.
    """

    action_selection = negotiator.listed_options(
        f"Select view option for printing data:", 
        [f"By {object_type}", "By date"])
    report = librarian.reciter(library, object_type, action_selection, file)
    if action_selection == f"By {object_type}":
        report_name = f"{object_type} report"
        file_format = ".md"
    else:
        report_name = f"{object_type.replace(" ", "_")}_date"
        file_format = ".csv"
    arciv.save_report(report, report_name, file_format)
    quit()


#
def status_checker(object_type):
    """
    Track progress by registering/viewing data across different categories.
    """

    progress_data, updated_category, attempt, state = librarian.status(mathemate, object_type)
    arciv.writer(progress_data, other_file=DATAPATH["Progress"], join_path="data")
    print(
        f"\nCurrent {updated_category} {TERMS["Attempt"]}: {attempt}.", 
        f"\nNext {TERMS["Event"]} is {state}:"
    )
    quit()


#
def systems_update(admin, negotiator, arciv, filepath, review_switch=True):
    """
    ...
    """
    
    data_options = arciv.reader()
    data_validation = arciv.reader(other_file=SETTINGS["Validation"], join_path="settings")
    data_options = admin.edit_options(negotiator, data_options, data_validation)
    print()
    if review_switch:
        for x, y in data_options.items():
            if type(y) is dict:
                print(x)
                for v, w in y.items():
                    print(f"{" ":17}{v:17}{w}")
            else:
                print(f"{x:17}{y}")

            print(f"{"....."*25}")
    
    filename, extension = os.path.splitext(filepath)
    arciv.backup(negotiator, [10, 8, 6, 4, 2, 1], filename)
    arciv.writer(data_options)
    quit()


# Initialize system
# Class: Option displayer/collector
negotiator = Negotiator()
# Check database structure, create missing files
initialize()

# User input for program selection:
# Select object type and action 
# ==> Load settings and file via configuration data
char = TERMS["Character"]
tool = TERMS["Tool"]
misc = TERMS["Misc"]
types = [char, tool, misc]
object_type = negotiator.listed_options(
    "Select object type", 
    [char, misc, tool],
    allow_systems=True)
if not object_type == "systems":
    event_term = TERMS[f"{object_type} event"]
    filepath = DATAPATH[object_type]
    file = os.path.join(DIRECTORIES["DataFolder"], filepath)
else:
    admin = Administrator()
    filepath = SETTINGS["Options"]
    file = os.path.join(DIRECTORIES["SettingsFolder"], filepath)

# Class:
# File/backup management
arciv = Archivist(DIRECTORIES, DATAPATH, file)
# Information collection and management
librarian = Librarian(DATAPATH, SETTINGS, TERMS, arciv, negotiator)
# Calculations
mathemate = Mathematician()

if object_type == "systems": systems_update(admin, negotiator, arciv, filepath)
# Set options and selection, read library and run program: 
# - Read and print library 
# - Check and update progress data 
# - Update library
read_lib, edit_lib, reg_event, status_check = "Check library", "Edit library", "Register event", "Check status"
action_selection = negotiator.listed_options(
    "Select action among:",
    ["Check library", "Edit library", "Register event", "Check status"])
library = arciv.reader()
if action_selection == "Check library":
    review(library, file, object_type)
elif action_selection == "Check status":
    status_checker(object_type)
else:
    main(library, object_type, action_selection, event_term)




