import os
from utilities import Archivist
from config import PATHWAYS



def enter_data(object_type):
    option_data = arciv.reader(PATHWAYS["options"], True)
    new_object = dict()

    print()
    print("-"*50)

    name = input(f"Enter {object_type.lower()} name: ")
    print()

    new_object[name] = {}

    for category in option_data[object_type].keys():
        selectable_options = dict()
        numeral = 1

        print("-"*50, f"\nSelect {category} among:")
        for option in option_data[object_type][category]:
            selectable_options[str(numeral)] = option
            print(f"  {numeral}: {option}")
            numeral += 1

        while True:
            selection = input(f"\nEnter {category.capitalize()}: ")
            if selection in selectable_options.keys():
                break
            else:
                print("Enter valid numeral.")

        new_object[name][category.capitalize()] = selectable_options[selection]
        print()

    print(f"Object summary: {name}")
    for x, y in new_object[name].items():
        print(f"  {x:8} {y}")

    return new_object, name


# Create call to file manager script set to data folder
arciv = Archivist(PATHWAYS["data directory"])


# User selection for what type of data to collect
object_selection = 0
while object_selection not in [1, 2]:
    try:
        object_selection = int(input("\nSelect category among:\n  1: Character\n  2: Tool\n\nEnter category: "))
    except:
        print("Enter valid integer.")

if object_selection == 1:
    event_type = "Character Event"
    filepath = PATHWAYS["character_event"]
elif object_selection == 2:
    event_type = "Tool Event"
    filepath = PATHWAYS["tool_event"]

file = os.path.join(PATHWAYS["data directory"], filepath)


# Request information about new object from user
new_event, name = enter_data(event_type)


# Backup interval
# Corrupted data can completely whipe a data file, so data is backup up for redundancy. 
# Set number from lowest to smallest. This decides at which number of updates a backup is performed. E.g. [30, 10, 2] performs backups every 2nd, 10th, and 30th update. 
BACKUP_FREQUENCY = [30, 10, 2]  

# Perform backup and join data with library data
if arciv.backup(file, BACKUP_FREQUENCY, event_type): # Backup prior to file changes.
    updated_history = arciv.join_data(file, new_event, name)

# Write updated library to file
if updated_history:
    arciv.writer(file, updated_history)
    print("\nLibrary updated!\n")






