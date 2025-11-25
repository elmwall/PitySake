import sys, os
from utilities import FileManager
from config import PATHWAYS

event = 0

data = {
    "Previous event": {
        "Page": False,
        "Row": False
    },
    "Current event": {
        "Page": False,
        "Row": False
    }
}


def collect_data():
    for x in data.keys():
        print()
        while True:
            for y in data[x].keys():
                # print(f"{x}: {y}")
                data[x][y] = False
                while not data[x][y]:
                    try:
                        data[x][y] = int(input(f"{x}, {y}: "))
                    except:
                        print("\nEnter valid numeral.")
            
            # print("Row must in between 1 and 5.")
            if data[x]["Row"] in range (1,6) and data[x]["Page"] > 0:
                break
            else:
                print("\nPage must be at least 1.\nRow must be between 1 and 5.\n")

    event = abs(5*(data["Previous event"]["Page"] - data["Current event"]["Page"]) + data["Previous event"]["Row"] - data["Current event"]["Row"])
    print()

    if event == 0:
        print("\nEvent cannot be 0.")
        return False, event
    elif event > 90:
        print("\nMaximum value of event is 90.")
        return False, event
    elif data["Current event"]["Page"] > data["Previous event"]["Page"]:
        print("\nPrevious event page cannot be smaller than the current.")
    else:
        return event

    # if data["Current event"]["Page"] < data["Previous event"]["Page"] or data["Current event"]["Page"] == data["Previous event"]["Page"]:
    #     return True, event
    # else:
    #     print("Previous event page cannot be smaller than the current.")


def tracker(progress_type, data, data_action):
    previous_data = fim.reader(file)
    selectable_options = dict()
    numeral = 1

    print("-"*50, f"\nSelect event among:")
    for option in option_data:
        selectable_options[str(numeral)] = option
        print(f"  {numeral}: {option}")
        numeral += 1

    while True:
        selection = input(f"\nEnter event: ")
        if selection in selectable_options.keys():
            selected_event = selectable_options[selection]
            break
        else:
            print("Enter valid numeral.")
    
    if progress_type == 1:
        progress_name = "Current value"
        if data_action == 2:
            try:
                previous_value = previous_data[selected_event][progress_name]
            except:
                previous_value = 0
                print("No previous data")
        else:
            previous_value = 0
        output = data + previous_value
        while output not in range(1,91):
            print(f"\nNew value cannot exceed 90. Previous value: {previous_value}")
            try:
                data = int(input("Enter value to add: "))
            except:
                print("Enter valid integer.")            
            output = data + previous_value
    elif progress_type == 2:
        progress_name = "Previous event"
        output = data
    elif progress_type == 3:
        progress_name = "Status"
        output = data
    
    if previous_data is dict:
        progress = previous_data
    else:
        progress = dict()
    
    try:
        progress[selected_event] = previous_data[selected_event]
    except:
        progress[selected_event] = dict()
    
    progress[selected_event][progress_name] = output

    # progress_data = fim.reader(file)
    updated_progress = fim.join_data(file, progress, None, static=True)
    fim.writer(file, updated_progress)

    return data


fim = FileManager(PATHWAYS["data directory"])
file = os.path.join(PATHWAYS["data directory"], PATHWAYS["progress"])
option_data = fim.reader(PATHWAYS["options"], join=True)["Event"]
# object_selection = 0



action = 0
print("\nSelect action among:\n1: Calculate progress or occurrence\n2: Update data\n3: Show current progress")
while action not in [1, 2, 3]:
    try:
        action = int(input("\nSelect action: "))
    except:
        print("Enter valid integer.")

if action == 1:
    event = collect_data()
    print(f"Result: {event}")
    sys.exit()


if action == 2:
    progress_type = 0
    print("\nSelect action among:\n1: Track progress\n2: Register event occurrence\n3: Update chance of next outcome")
    while progress_type not in [1, 2, 3]:
        try:
            progress_type = int(input("\nSelect action: "))
        except:
            print("Enter valid integer.")

    data_action = 0
    if progress_type == 1:
        print("\nSelect action among:\n1: Enter progress value (clear previous)\n2: Add to previous value")
        while data_action not in [1, 2]:
            try:
                data_action = int(input("\nSelect action: "))
            except:
                print("Enter valid integer.")

    value = 0
    if progress_type == 3:
        print("\nSet status:\n1: 50-50\n2: Guaranteed")
        status_selection = 0
        while status_selection not in [1, 2]:
            try:
                status_selection = int(input("\nSelect action: "))
            except:
                print("Enter valid integer.")    
        if status_selection == 1:
            value = "50-50"
        elif status_selection == 2:
            value = "Guaranteed"
    else:    
        while value not in range (1,91):
            try:
                value = int(input("\nEnter progress value: "))
            except:
                print("Enter valid integer.")
            
    tracker(progress_type, value, data_action)


    


report = fim.reader(file)
print("\nData report:")
try:
    for x in report.keys():
        print(f"\n{x}")
        for y, z in report[x].items():
            print(f"   {y:16}{z}")
except:
    print("No data to show.")
print()



# print()
# event = abs(5*(data["Previous event"]["Page"] - data["Current event"]["Page"]) + data["Previous event"]["Row"] - data["Current event"]["Row"])

# if event > 90:
#     pass
# else:
#     print(f"Event occurred during turn: {event}")

# previous_page = input("Previous event page: ")
# previous_position = input("Previous event position: ")

# previous_page = input("Previous event page: ")
# previous_position = input("Previous event position: ")

# current_page = input("Current event page: ")
# current_position = input("Current event position: ")

# event = 5*(previous_page - current_page) + previous_position - current_position