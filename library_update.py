import os, keyboard, sys, msvcrt
from utilities import FileManager
from config import PATHWAYS




def enter_data(object_type):
    option_data = fim.reader(PATHWAYS["options"], join=True)
    new_object = dict()

    print()
    print("-"*50)


    name = input(f"Enter {object_type.lower()} name: ")
    if name == "remove":
        return None, name
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
            if msvcrt.kbhit():
                selection = msvcrt.getch().decode("ASCII")
                if selection in selectable_options.keys():
                    break
                else:
                    print("Enter valid key.")

        # while True:
        #     key_event = keyboard.read_event()
        #     if key_event.event_type == keyboard.KEY_DOWN:
        #         key = key_event.name
        #         if key in selectable_options.keys():
        #             break
        #         else:
        #             print("Enter valid key.")


        new_object[name][category.capitalize()] = selectable_options[selection]
        print()

    print(f"Object summary: {name}")
    for x, y in new_object[name].items():
        print(f"  {x:8} {y}")

    return new_object, name


def main():
    # Request information about new object from user
    new_object, name = enter_data(object_type)


    # Backup interval
    # Corrupted data can completely whipe a data file, so data is backup up for redundancy. 
    # Set number from lowest to smallest. This decides at which number of updates a backup is performed. E.g. [30, 10, 2] performs backups every 2nd, 10th, and 30th update. 
    BACKUP_FREQUENCY = [30, 10, 2]  

    # Perform backup and join data with library data
    if fim.backup(file, BACKUP_FREQUENCY, object_type): # Backup prior to file changes.
        # print("check")
        updated_library = fim.join_data(file, new_object, name)

    # Write updated library to file
    if updated_library:
        fim.writer(file, updated_library)
        print("\nLibrary updated!\n")



# Create call to file manager script set to data folder
fim = FileManager(PATHWAYS["data directory"])


# User selection for what type of data to collect
object_selection = 0
print("\nSelect category among:\n  1: Character\n  2: Tool")
while True:
    # key_event = keyboard.read_event()
    if msvcrt.kbhit():
        object_selection = msvcrt.getch().decode("ASCII")
        if object_selection in ("1", "2"):
            break
        else:
            sys.exit()
# while object_selection not in [1, 2]:
#     try:
#         object_selection = int(input("\nEnter category: "))
#     except:
#         print("Enter valid integer.")

if object_selection == "1":
    object_type = "Character"
    filepath = PATHWAYS["characters"]
    # file = os.path.join(DATA_PATH, "characters.json")
elif object_selection == "2":
    object_type = "Tool"
    filepath = PATHWAYS["tools"]

file = os.path.join(PATHWAYS["data directory"], filepath)


action_selection = 0
print("\nSelect action among:\n  1: Check library\n  2: Update library")
# while action_selection not in [1, 2]:
#     try:
#         action_selection = int(input("\nSelect action: "))
#     except:
#         print("Enter valid integer.")

# key = 0
while True:
    # key_event = keyboard.read_event()
    if msvcrt.kbhit():
        key = msvcrt.getch().decode("ASCII")
        if key in ("1", "2"):
            break
        else:
            sys.exit()

if key == "1":
    library = fim.reader(file)

    if type(library) is dict:
        library = dict(sorted(library.items()))
        for x in library:
            print(f"\n{x}")
            for y, z in library[x].items():
                print(f"  {y:10}{z}")
elif key == "2":
    main()




