import os, datetime
from utilities import Archivist, Negotiator
from config import PATHWAYS
from event_calculator import Mathematician



class Librarian:
    def __init__(self):
        pass
    


def enter_data(name, object_type, data_options):
    # data_options = arciv.reader(PATHWAYS["options"], join=True)
    new_object = dict()
    
    # Enter object details
    new_object[name] = negotiator.auto_options(f"\nEnter details for {name}", data_options[object_type])

    # Print entered data for review
    print(f"\nSummary for {name}:")
    for x, y in new_object[name].items():
        print(f"  {x:14} {y}")

    return new_object


def enter_event(name, data_options, misc_obj):
    try:
        object = arciv.reader(file)[name]
    except:
        print(f"\n{name} could not be found in library. Check library content or spelling.")
        quit()
        # object = arciv.reader(file)

    updated_object = dict()
    updated_object[name] = object
        

    # data_options = arciv.reader(PATHWAYS["options"], join=True)
    if misc_obj:
        event = data_options["Term"]["collection"]
        updated_object[name][event] = negotiator.listed_options(f"\nEnter details for {name} event", data_options[event])
    
    else:
        # Enter Event details
        event = data_options["Term"]["Event"]
        now = datetime.datetime.now()
        now = now.strftime("%y") + now.strftime("%m") + now.strftime("%d")
        while True:
            event_date = input(f"\nEnter event date as YYMMDD: ")
            try:
                date_validity = datetime.datetime(int("20"+event_date[0:2]), int(event_date[2:4]), int(event_date[4:6]))
                date_int = int(event_date)
            except ValueError as e:
                print(e)
                continue
            except Exception as e:
                print(e)

            if len(event_date) != 6:
                print("Incorrect date length")
            elif int(event_date) > int(now) or int(event_date) < 200927:
                print("Impossible date. Try again.")
            else:
                break


        # Check if previous 
        if not event in updated_object[name].keys():
            updated_object[name][event] = dict()
            event_count = 1
        else:
            event_count = 1+len(updated_object[name][event].keys())
        
        event_name = f"{event_date}-{event_count}"
        attempt_term = data_options["Term"]["Attempt"]
        
        # print
        event_options = data_options[event]
        attempt = False
        presets = dict()

        method_calc = f"Calculate {attempt_term}"
        method_enter = f"Enter {attempt_term}"
        method_skip = f"No {attempt_term} - skip"
        attempt_method = negotiator.listed_options("Select option", [method_calc, method_enter, method_skip]) 

        if attempt_method == method_calc:
            attempt = mathemate.calculate_attempts(negotiator, event_term=data_options["Term"]["Event"])
            # presets[attempt_term] = attempt
        elif attempt_method == method_enter:
            attempt = negotiator.request_numeral(f"\nEnter value for {attempt_term}: ", lower_limit=0, upper_limit=90)
            # attempt = input(f"\nEnter value for {attempt_term}: ")
        else:
            event_options[ data_options["Term"]["Event name"] ] = "enter preset"
            presets[ data_options["Term"]["Event name"] ] = data_options["Term"]["Gift"]
            
            event_options[ "State" ] = "enter preset"
            presets[ "State" ] = False

        presets[attempt_term] = attempt
        
        if not attempt_method == method_skip:
            state_preset = negotiator.listed_options(f"Was item received from {data_options["Term"]["Standard"]}?", ["Yes", "No"])
            if state_preset == "Yes":
                event_options[ "Source" ] = "enter preset"
                presets[ "Source" ] = data_options["Term"]["Standard"]

                event_options[ "State" ] = "enter preset"
                presets[ "State" ] = False
        # while True:
        
        updated_object[name][event][event_name] = negotiator.auto_options(f"\nEnter details for {name} event", data_options[event], preset_values=presets)


        # if updated_object[name][event][event_name][ data_options["Term"]["Event name"] ] == "Choice" and not attempt:
            # print(f"{data_options["Term"]["Event name"]} requires a value. Re-enter data.")
            # attempt = negotiator.request_numeral(f"\nEnter value for {attempt_term}: ", lower_limit=1, upper_limit=90)
            # updated_object[name][event][event_name][attempt_term] = attempt
        # elif 
            

            # if updated_object[name][event][event_date][attempt_term] not in range(1,91):
            #     print(f"Invalid {attempt_term}, enter data again.")
            # else:
            #     break

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
                # print()
                print(f"{"":{indent}}{"":{sub_indent}}{key:10}")
                reciter(info, indent=20, separation=1)
            else:
                print(f"{"":{indent}}{"":{sub_indent}}{key:10}{info}")



def main(object_type, data_options, reg_event):
    # Specify name, the main key for locating its data later.
    # Enter remove to remove previous entry.

    print("-"*50)
    name = input(f"Enter {terms[object_type].lower()} name: ")
    if name == "remove":
        new_object = None
    elif reg_event:
        new_object = enter_event(name, data_options, object_type=="Misc")
    else:
        # Request information about new object from user
        new_object= enter_data(name, object_type, data_options)

    # Backup interval 
    # Set number from lowest to smallest. This decides at which number of updates a backup is performed. E.g. [30, 10, 2] performs backups every 2nd, 10th, and 30th update. 
    BACKUP_FREQUENCY = [30, 10, 2]

    # Performing backup and joining data with library data before writing to file
    if arciv.backup(file, BACKUP_FREQUENCY, object_type): # Backup prior to file changes.
        updated_library = arciv.join_data(file, new_object, name, update=reg_event)

    if updated_library:
        arciv.writer(file, updated_library)
        print(f"\nLibrary updated with {name}!\n")



# Create call to file manager script set to data folder
arciv = Archivist(PATHWAYS["Directory"])
negotiator = Negotiator()
mathemate = Mathematician()
check_lib = "Check library"
update_lib = "Update library"
reg_event = "Register event"
data_options = arciv.reader(PATHWAYS["Options"], join=True)
terms = {
    "Character": data_options["Term"]["Character"],
    "Tool": data_options["Term"]["Tool"],
    "Misc": data_options["Term"]["Misc"]
}


# Select item type and action ==> Load options via configuration files
object_type = negotiator.listed_options("Select item type", [terms["Character"], terms["Tool"], terms["Misc"]])
action_selection = negotiator.listed_options("Select action among:", [check_lib, update_lib, reg_event])


# if object_type == "Character": filepath = PATHWAYS["Characters"]
# elif object_type == "Tool": filepath = PATHWAYS["Tools"]
for type_name, term in terms.items():
    if term == object_type:
        filepath = PATHWAYS[type_name] 
        object_type = type_name
file = os.path.join(PATHWAYS["Directory"], filepath)
# event = negotiator.listed_options("Select type of data:", ["Character details", "Event"])


if action_selection == check_lib:
    library = arciv.reader(file)
    reciter(library)

elif action_selection in [update_lib, reg_event]:
    main(object_type, data_options, action_selection==reg_event)




