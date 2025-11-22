# if 5 in range(1,6):
#     print(1)

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
                        print("Enter valid numeral")
            
            # print("Row must in between 1 and 5.")
            if data[x]["Row"] in range (1,6) and data[x]["Page"] > 0:
                break
            else:
                print("\nPage must be at least 1.\nRow must be between 1 and 5.\n")

    event = abs(5*(data["Previous event"]["Page"] - data["Current event"]["Page"]) + data["Previous event"]["Row"] - data["Current event"]["Row"])
    print()

    if event == 0:
        print("Event cannot be 0.")
        return False, event
    elif event > 90:
        print("Maximum value of event is 90.")
        return False, event
    elif data["Current event"]["Page"] > data["Previous event"]["Page"]:
        print("Previous event page cannot be smaller than the current.")
    else:
        return True, event

    # if data["Current event"]["Page"] < data["Previous event"]["Page"] or data["Current event"]["Page"] == data["Previous event"]["Page"]:
    #     return True, event
    # else:
    #     print("Previous event page cannot be smaller than the current.")


def main():
    collected = False
    while not collected:
        collected, event = collect_data()
        # collected = collect_data()

    print(f"Event occurred during attempt: {event}")

    return event

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