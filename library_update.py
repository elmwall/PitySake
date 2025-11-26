import os
from utilities import Archivist, Negotiator
from config import PATHWAYS



class Librarian:
    def __init__(self):
        pass
    


def enter_data(object_type):
    option_data = arciv.reader(PATHWAYS["options"], join=True)
    new_object = dict()

    print()
    print("-"*50)

    # Specify name, the main key for locating its data later.
    # Enter remove to remove previous entry.
    name = input(f"Enter {object_type.lower()} name: ")
    if name == "remove":
        return None, name
    print()

    # Enter object details
    new_object[name] = negotiator.auto_options(f"Enter details for {name}", option_data[object_type])

    # Print entered data for review
    print(f"Object summary: {name}")
    for x, y in new_object[name].items():
        print(f"  {x:8} {y}")

    return new_object, name


def reciter(library:dict, indent=0):
    if type(library) is not dict:
        print("\nI cannot read that.\n")
        quit()
        
    library = dict(sorted(library.items()))

    for entry in library:
        print(f"\n{" "*indent}{entry}")
        for key, info in library[entry].items():
            if type(info) is dict:
                print()
                print(f"  {" "*indent}{key:10}")
                reciter(info, indent=12)
            else:
                print(f"  {" "*indent}{key:10}{info}")



def main(object_type):
    # Request information about new object from user
    new_object, name = enter_data(object_type)

    # Backup interval
    # Corrupted data can completely whipe a data file, so data is backup up for redundancy. 
    # Set number from lowest to smallest. This decides at which number of updates a backup is performed. E.g. [30, 10, 2] performs backups every 2nd, 10th, and 30th update. 
    BACKUP_FREQUENCY = [30, 10, 2]  

    # Performing backup and joining data with library data before writing to file
    if arciv.backup(file, BACKUP_FREQUENCY, object_type): # Backup prior to file changes.
        updated_library = arciv.join_data(file, new_object, name)

    if updated_library:
        arciv.writer(file, updated_library)
        print("\nLibrary updated!\n")



# Create call to file manager script set to data folder
arciv = Archivist(PATHWAYS["data directory"])
negotiator = Negotiator()


# Select item type ==> Load options for the specific type via configuration files
object_type = negotiator.listed_options("Select item type", ["Character", "Tool"])
if object_type == "Character": filepath = PATHWAYS["characters"]
elif object_type == "Tool": filepath = PATHWAYS["tools"]
file = os.path.join(PATHWAYS["data directory"], filepath)


action_selection = negotiator.listed_options("Select action among:", ["Check library", "Update library"])


if action_selection == "Check library":
    library = arciv.reader(file)
    reciter(library)

elif action_selection == "Update library":
    main(object_type)




