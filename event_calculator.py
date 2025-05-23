# if 5 in range(1,6):
#     print(1)

collected = False
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
            if data[x]["Row"] in range (1,6):
                break
            else:
                print("Row must in between 1 and 5.\n")

    if data["Current event"]["Page"] < data["Previous event"]["Page"] or data["Current event"]["Page"] == data["Previous event"]["Page"]:
        return True
    else:
        print("Previous event page cannot be smaller than the current.")


while not collected:
    collected = collect_data()
    # collected = collect_data()


print()
event = abs(5*(data["Previous event"]["Page"] - data["Current event"]["Page"]) + data["Previous event"]["Row"] - data["Current event"]["Row"])
print(f"Event occurred during turn: {event}")

# previous_page = input("Previous event page: ")
# previous_position = input("Previous event position: ")

# previous_page = input("Previous event page: ")
# previous_position = input("Previous event position: ")

# current_page = input("Current event page: ")
# current_position = input("Current event position: ")

# event = 5*(previous_page - current_page) + previous_position - current_position