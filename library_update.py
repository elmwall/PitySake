import os, datetime
from utilities import Archivist, Negotiator

from settings.config import PATHWAYS, TERMS

from event_calculator import Mathematician





class Librarian:
    def __init__(self):
        pass
    

def collect_settings(keywords):
    data_options = arciv.reader(PATHWAYS["Options"], join="settings")
    settings = list()
    for key in keywords:
        settings.append(data_options[key])

    return settings if len(settings) > 1 else settings[0]


def enter_data(name:str, object_type:str, data_options):
    """
    Collect data for new library entry.
    """

    new_object = dict()
    
    # Enter object details
    new_object[name] = negotiator.auto_options(f"\nEnter details for {name}", data_options)

    # Print entered data for review
    print(f"\nSummary for {name}:")
    for x, y in new_object[name].items():
        print(f"  {x:14} {y}")

    return new_object


def enter_event(name, event_options, misc_obj):
    """
    Collect/update data about multiples of an object in library.
    """

    updated_object = dict()
    try:
        updated_object[name] = arciv.reader(file)[name]
    except:
        print(f"\n{name} could not be found in library. Check library content or spelling.")
        quit()


    # LESSER OBJECTS: collect single value
    if misc_obj:
        # event = TERMS["collection"]
        updated_object[name][ TERMS["Collection"] ] = negotiator.listed_options(f"\nEnter {TERMS["Collection"]} for {name}.", event_options)

        return updated_object
    

    # ESSENTIAL OBJECTS: registration and validation of date received
    now = datetime.datetime.now()
    now = now.strftime("%y") + now.strftime("%m") + now.strftime("%d")
    while True:
        event_date = input(f"\nEnter event date as YYMMDD: ")
        try:
            date_validity = datetime.datetime(int("20"+event_date[0:2]), int(event_date[2:4]), int(event_date[4:6]))
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


    # CHECK EVENT HISTORY and create dict if needed
    # Create an event ID numeral
    if not TERMS["Event"] in updated_object[name].keys():
        updated_object[name][ TERMS["Event"] ] = dict()
        event_count = 0
    else:
        event_count = len(updated_object[name][ TERMS["Event"] ].keys())
    event_name = f"{event_date}-{event_count}"
    

    # DETERMINE ATTEMPTS, call calculator if needed, and adjust settings if non-applicable
    attempt_term = TERMS["Attempt"]
    attempt = False
    presets = dict()

    method_calc = f"Calculate {attempt_term}"
    method_enter = f"Enter {attempt_term}"
    method_skip = f"No {attempt_term} - skip"
    attempt_method = negotiator.listed_options("Select option", [method_calc, method_enter, method_skip]) 

    if attempt_method == method_calc:
        mathemate = Mathematician()                 # Calculation assistant class
        attempt = mathemate.calculate_attempts(negotiator, event_term=TERMS["Event"])
    elif attempt_method == method_enter:
        attempt = negotiator.request_numeral(f"\nEnter value for {attempt_term}: ", lower_limit=0, upper_limit=90)
    else:
        event_options[ TERMS["Event name"] ] = "enter preset"
        presets[ TERMS["Event name"] ] = TERMS["Gift"]
        
        event_options[ "State" ] = "enter preset"
        presets[ "State" ] = False

    presets[attempt_term] = attempt

    
    # DEFINE SOURCE and adjust settings if non-applicable
    if not attempt_method == method_skip:
        state_preset = negotiator.listed_options(f"Was item received from {TERMS["Standard source"]}?", ["Yes", "No"])
        if state_preset == "Yes":
            event_options[ "Source" ] = "enter preset"
            presets[ "Source" ] = TERMS["Standard source"]

            event_options[ "State" ] = "enter preset"
            presets[ "State" ] = False
    

    # CREATE DICTIONARY ENTRY from above settings
    updated_object[name][TERMS["Event"]][event_name] = negotiator.auto_options(f"\nEnter details for {name} {TERMS["Event"]}", event_options, preset_values=presets)

    return updated_object


def reciter(library:dict, indent=0, separation=1):
    if type(library) is not dict:
        print("\nI cannot read that.\n")
        quit()
        
    library = dict(sorted(library.items()))
    sub_indent = 10
    for entry in library:
        print(f"{"\n"*separation*2}{"":{indent}}{entry.upper():20}{entry}{"\n"*separation*0}")
        for key, info in library[entry].items():
            if not info:
                continue
            if type(info) is dict:
                print(f"{"":{indent}}{"":{sub_indent}}{key:10}")
                reciter(info, indent=20, separation=1)
            else:
                print(f"{"":{indent}}{"":{sub_indent}}{key:10}{info}")



def main(object_type, datatype, data_options, reg_event):
    print("-"*50)

    # Specify name, the main key for locating its data later.
    # Enter "remove" to delete previous entry.
    name = input(f"Enter {object_type.lower()} name: ").capitalize()

    # Switch between remove, enter new object, or add data to existing object
    if name == "Remove":
        new_object = None
    elif reg_event:
        new_object = enter_event(name, data_options, object_type==TERMS["Misc"])
    else:
        new_object= enter_data(name, object_type, data_options)

    # Backup interval 
    # Number from biggest to smallest interval. Decides at which update interval backup is performed. E.g. [30, 10, 2] performs backups every 2nd, 10th, and 30th update. 
    backup_frequency = [30, 10, 2]

    # Performing backup and joining data with library data before writing to file
    if arciv.backup(file, backup_frequency, datatype): # Backup prior to file changes.
        updated_library = arciv.join_data(file, new_object, name, update=reg_event)
    if updated_library:
        arciv.writer(file, updated_library)
        print(f"\nLibrary updated with {name}!\n")



# CLASSES
# File/backup management
arciv = Archivist(PATHWAYS["Datafolder"], PATHWAYS["Settingsfolder"])    
# Option displayer/collector
negotiator = Negotiator()                                                


# USER INPUT
# Select object type and action ==> Load settings and file via configuration data
char = "Character"
tool = "Tool"
misc = "Misc"
types = [char, tool, misc]
object_type = negotiator.listed_options("Select object type", [TERMS[char], TERMS[misc], TERMS[tool]])
for x in types:
    if object_type == TERMS[x]: 
        filepath = PATHWAYS[x]
        datatype = x + "_data"
file = os.path.join(PATHWAYS["Datafolder"], filepath)

# Options
check_lib = "Check library"
update_lib = "Update library"
reg_event = "Register event"
action_selection = negotiator.listed_options("Select action among:", [check_lib, update_lib, reg_event])
option_list = list()


# MAIN ACTION
if action_selection == check_lib:
    library = arciv.reader(file)
    reciter(library)
    quit()
# elif action_selection in [update_lib, reg_event]:
elif action_selection == update_lib:
    option_list.append(object_type)
elif action_selection == reg_event:
    option_list.append(TERMS["Event"]) if object_type != TERMS[misc] else option_list.append(TERMS["Collection"])

event_options = collect_settings(option_list)
main(object_type, datatype, event_options, action_selection==reg_event)




