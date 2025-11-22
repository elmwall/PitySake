import json, os, shutil, tempfile

DATA_PATH = "./PitySake_Data"
CHARACTER_LIBRARY = DATA_PATH + "/character_data.json"
TOOL_LIBRARY = DATA_PATH + "/tool_data.json"
VERIFICATION_DATA = DATA_PATH + "/data_options.json"


def load_resource(file):
    if os.path.exists(file):
        with open(file, "r", encoding="utf-8") as f:
            return json.load(f)


def save_resource(file, update):
    try:
        current_count = len(load_resource(file))
    except:
        current_count = 0
    print("current count", current_count)

    backup_path = False

    if current_count > 0:
        if current_count % 30 == 0:
            backup_path = DATA_PATH + "/" + object_type + "_backup30.json"
        elif current_count % 10 == 0:
            backup_path = DATA_PATH + "/" + object_type + "_backup10.json"
        elif current_count % 2 == 0:
            backup_path = DATA_PATH + "/" + object_type + "_backup2.json"
        
    if backup_path:
        print("backup path", backup_path)

        if os.path.exists(backup_path):
            backup_count = len(load_resource(backup_path))
        else:
            backup_count = 0
        
        if backup_count > current_count:
            raise RuntimeError(
                f"\nError! Backup file contains more data than current file."
                f"\nCurrent length: {current_count}\nBackup length: {backup_count}"
            )
        else:
            shutil.copy(file, backup_path)
            print("Data backup performed.")

    try:
        with open(file, "w", encoding="utf-8") as f:
            json.dump(update, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print("Error occurred while attempting to write. Check file health and backups.")


def enter_data(object_type):
    verification_data = load_resource(VERIFICATION_DATA)

    object_data = dict()

    print()
    print("-"*50)

    name = input(f"Enter {object_type.lower()} name: ")
    print()

    object_data[name] = {}

    for category in verification_data[object_type].keys():
        options = dict()
        n = 1

        print("-"*50, f"\nSelect {category} among:")
        for option in verification_data[object_type][category]:
            options[str(n)] = option
            print(f"  {n}: {option}")
            n += 1

        while True:
            selection = input(f"\nEnter {category.capitalize()}: ")
            if selection in options.keys():
                break
            else:
                print("Enter valid numeral.")

        object_data[name][category.capitalize()] = options[selection]
        print()

    print("Object summary:")
    for x, y in object_data.items():
        print(f"  {x:8} {y}")
    
    return object_data, name


def registration(object, name, file):
    print("1")
    try:
        library = load_resource(file)
    except:
        library = {}
    # object_set = {}
    # object_set.update(object)
    original_length = len(library)
    print("2")

    if name in library.keys():
        print("\nObject not added - already exists in library.")
        return False
    else:
        library.update(object)
    print("3")
    # print(original_length, len(library))

    if len(library) != original_length + 1:
        print("\nError occurred!\n\nLibrary update aborted.")
    else:
        save_resource(file, library)
        print("4")
        return True


object_selection = 0
while object_selection not in [1, 2]:
    try:
        object_selection = int(input("\nSelect category among:\n  1: Character\n  2: Tool\n\nEnter category: "))
    except:
        print("Enter valid integer.")

if object_selection == 1:
    object_type = "Character"
    file = CHARACTER_LIBRARY
elif object_selection == 2:
    object_type = "Tool"
    file = TOOL_LIBRARY


entered_object, name = enter_data(object_type)
print(entered_object)

if registration(entered_object, name, file):
    print("\nLibrary updated!")




