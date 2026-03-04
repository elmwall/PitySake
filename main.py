import os
import datetime

from utilities import Archivist, Negotiator
from settings.config import PATHWAYS, TERMS
from event_calculator import Mathematician


# TODO move updated functions to Librarian in info_manager.py
def collect_settings(keywords:list):
    """
    Single reading of config file to return settings as list or single element.
    
    keywords : list of keys to locate settings.
    """
    data_options = arciv.reader(
        other_file=PATHWAYS["Options"], join="settings")
    settings = list()
    for key in keywords:
        settings.append(data_options[key])

    return settings if len(settings) > 1 else settings[0]


def enter_data(name:str, data_options):
    """
    Collect basic info about new library entry.  
    Returns: single-entry dictionary.

    name : str, identifier for object in library.
    """

    # Enter object details
    new_object = dict()
    new_object[name] = negotiator.auto_options(
        f"\nEnter details for {name}",
        data_options)
    
    # Print entered data for review
    print(f"\nSummary for {name}:")
    for x, y in new_object[name].items():
        print(f"  {x:14} {y}")

    return new_object


def enter_event(name:str, event_options, misc_obj:bool):
    """
    Collect historical acquisition data for object in library.  
    Returns: single-entry dictionary with updated object.

    name : str, identifier for object in library.
    event_options : selectable opions as a list if simple object, or as a dict for detailed object.
    misc_object : switch for simple object (True) or detailed object (False).
    """
    
    updated_object = dict()
    try:
        updated_object[name] = arciv.reader()[name]
    except:
        print(f"\n{name} must be added to library before registering event.\n",
              "Check library content or spelling.")
        quit()

    # Simple objects: 
    # Register single value and skip further collection
    if misc_obj:
        # event = TERMS["collection"]
        updated_object[name][TERMS["Collection"]] = negotiator.request_numeral(
            f"\nEnter {TERMS["Collection"]} for {name}",
            lower_limit=0,
            upper_limit=6)

        return updated_object
    
    # Detailed objects:
    # Step 1: Registration and validation of date received
    now = datetime.datetime.now()
    now = now.strftime("%y") + now.strftime("%m") + now.strftime("%d")
    while True:
        event_date = input(f"\nEnter event date as YYMMDD: ")
        try:
            date_validity = datetime.datetime(
                int("20"+event_date[0:2]),
                int(event_date[2:4]), 
                int(event_date[4:6]))
            # date_int = int(event_date)
        except ValueError as e:
            print(f"Invalid format, try again.\n{e}")
            continue
        except Exception as e:
            print(f"Invalid input, try again.\n{e}")
            continue

        if len(event_date) != 6:
            print("Incorrect date length")
        elif int(event_date) > int(now) or int(event_date) < 200927:
            print("Impossible date. Try again.")
        else:
            break

    # Step 2: Check content of previous data and create dict if needed
    # Create an event ID numeral
    if not TERMS["Event"] in updated_object[name].keys():
        updated_object[name][TERMS["Event"]] = dict()
        event_count = 0
    else:
        event_count = len(updated_object[name][TERMS["Event"]].keys())
    event_name = f"{event_date}-{event_count}"
    
    # Step 3: Determine attempts during event to reach acquisition
    # Calls calculator if needed
    # Adjust settings if no attempts (received through other means)
    attempt_term = TERMS["Attempt"]
    attempt = False
    presets = dict()

    method_calc = f"Calculate {attempt_term}"
    method_enter = f"Enter {attempt_term}"
    method_skip = f"No {attempt_term} - skip"
    attempt_method = negotiator.listed_options(
        "Select option", 
        [method_calc, method_enter, method_skip])

    if attempt_method == method_calc:
        # Calculation assistant class called only if needed
        mathemate = Mathematician()
        attempt = mathemate.calculate_attempts(
            negotiator, 
            event_term=TERMS["Event"])
    elif attempt_method == method_enter:
        attempt = negotiator.request_numeral(
            f"\nEnter value for {attempt_term}: ", 
            lower_limit=0, 
            upper_limit=90)
    else:
        event_options[TERMS["Event name"]] = "enter preset"
        presets[TERMS["Event name"]] = TERMS["Gift"]
        event_options["State"] = "enter preset"
        presets["State"] = False

    presets[attempt_term] = attempt

    # Step 4: Define source
    # Adjust settings if standard event
    if not attempt_method == method_skip:
        state_preset = negotiator.listed_options(
            f"Was item received from {TERMS["Standard source"]}?",
            ["Yes", "No"])
        if state_preset == "Yes":
            event_options["Source"] = "enter preset"
            presets["Source"] = TERMS["Standard source"]
            event_options["State"] = "enter preset"
            presets["State"] = False
    
    # Step 5: Create dictionary entry from above settings
    updated_object[name][TERMS["Event"]][event_name] = negotiator.auto_options(
        f"\nEnter details for {name} {TERMS["Event"]}",
        event_options, 
        preset_values=presets)

    return updated_object


def reciter(library:dict, object_type, action_selection, indent=0, separation=1):
    """
    Print contents of library.
    Returns: print and return string structured as table, formatted suitable for markdown view.
    """

    if type(library) is not dict:
        print("\nI cannot read that.\n")
        quit()
        
    library = dict(sorted(library.items()))
    report = str()
    # Although some variation is adapted for, take into account that data may very in keys:value pairs present, and also format and order. 

    # Check point to create report from database by-date sorted string, otherwise continues with by-entry 
    if action_selection == "By date":
        library_datewise = dict()
        data = []
        n = 1
        row_indent = 22
        # Cycle through and collect nested dictionary data
        for entry in library.keys():
            title = str()
            if TERMS["Event"] in library[entry].keys():
                events = library[entry][TERMS["Event"]]
                for event, info in events.items():
                    title = str(event[:6])
                    details = str()
                    for detail in dict(sorted(info.items())).values():
                        if not detail: detail = "-"
                        if type(detail) is int: data.append(detail)
                        space = 6 if len(str(detail)) < 5 else row_indent
                        details += f"{str(detail):{space}}" 
                    # Re-structure info into new dictionary
                    library_datewise.update({f"{title}-{str(n)}": f"{entry:{20}}{details}"})
                    n += 1
            else:
                title = f"NoDate-{n}"
                library_datewise.update({title[:6]: f"{entry:{row_indent}}"})
        library_datewise = dict(sorted(library_datewise.items()))

        # Generate final report format and print
        cutaway = 70
        report += f"```"
        report += f"\n{"Date":9}{"Name":{20}}{TERMS["Attempt"]:6}{"Source":{row_indent}}{"State"}\n"[:cutaway]
        for event in library_datewise.keys():
            report += f"\n{event[:6]:9}{library_datewise[event]}"[:cutaway]
        report += f"\n```"
        print(report)
        avg = sum(data)/len(data)
        print(round(avg, 1))
        
        return report
            

    report = f"# {object_type.capitalize()} library\n\n"
    sub_indent = 10
    # Create report  from database sorted by entry
    for entry in library.keys():
        print(f"{"\n"*separation*2}{"":{indent}}{entry.upper():20}{"\n"*separation*0}")
        report += f"\n\n## {entry.capitalize()}\n\n"
        # spacing = str()
        # Cycle through and collect/print nested dictionary data
        for key, info in library[entry].items():
            if not info:
                continue
            if type(info) is dict:
                info = dict(sorted(info.items()))
                print(f"{"":{indent}}{"":{sub_indent}}{key:10}")
                report += f"\n\n```\n"
                event_data =str()
                for event in info.keys():
                    new_event = f"{event[:6]}   "
                    for category, value in dict(sorted(info[event].items())).items():
                        if not value: value = f"{"-":5}"
                        space = 22 if len(str(value)) > 5 else 5
                        new_event += f"{category}: {str(value):{space}}"
                    print(f"{"":{indent+sub_indent*2}}{new_event}")
                    event_data += new_event+"\n"
                report += event_data+"```"
            else:
                print(f"{"":{indent}}{"":{sub_indent}}{key:10}{info}")
                # report += f"{spacing}{info}"
                spacing = " | "

    return report


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
        new_object = enter_event(name, data_options, object_type==TERMS["Misc"])
    else:
        library = arciv.reader()
        # Option to change entry info without removing events
        if name in library.keys():
            update_check = negotiator.listed_options(
                f"{name} is already in library.\nDo you wish to update details for {name}?", 
                ["Yes"])
            new_object = {name: library[name]}
            new_object[name].update(enter_data(name, data_options)[name])
        else:
            new_object = enter_data(name, data_options)

    # Backup interval 
    # Number from biggest to smallest interval. Decides at which update interval backup is performed. E.g. [30, 10, 2] performs backups every 2nd, 10th, and 30th update.
    backup_frequency = [30, 10, 2]

    # Performing backup and joining data with library data before writing to file
    if arciv.backup(backup_frequency, datatype): # Backup prior to file changes.
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
    report = reciter(library, object_type, action_selection)
    if action_selection == f"By {object_type}":
        report_name = f"{object_type} report"
    else:
        f"{object_type} report date"
    # report_name = f"{object_type} report" if action_selection == f"By {object_type}" else f"{object_type} report date"
    arciv.save_report(report, report_name)
    quit()
elif action_selection == update_lib:
    option_list.append(object_type)
elif action_selection == update_check:
    if object_type != TERMS[misc]:
        option_list.append(TERMS["Event"])
    else:
        option_list.append(TERMS["Collection"])
event_options = collect_settings(option_list)

main(object_type, datatype, event_options, action_selection==update_check)




