import json

DATA_PATH = "./PitySake_Data"
CHARACTER_LIBRARY = DATA_PATH + "/character_data.json"
TOOL_LIBRARY = DATA_PATH + "/tool_data.json"
VERIFICATION_DATA = DATA_PATH + "/data_options.json"

def load_resource(file):
    with open(file, "r") as f:
        return json.load(f)
    

def registration(object_type):
    verification_data = load_resource(VERIFICATION_DATA)

    name = input("Name: ")
    rarity = input("Rarity: ")
    region = input("Region: ")
    
    if object_type == "Character":
        element = input("Element: ")
        tool = input("Tool: ")
        return {
            "Name": name,
            "Rarity": rarity,
            "Region": region,
            "Element": element,
            "Tool": tool
        }
    elif object_type == "Tool":
        tool_type = input("Tool type: ")
        return {
            "Name": name,
            "Rarity": rarity,
            "Region": region,
            "Type": tool_type
        }

    

object_selection = 0
while object_selection not in [1, 2]:
    try:
        object_selection = int(input("Character: 1\nTool: 2\nSelection: "))
    except:
        print("Enter valid integer")

if object_selection == 1:
    object_type = "Character"
elif object_selection == 2:
    object_type = "Tool"

registered_obj = registration(object_type)
print(registered_obj)



