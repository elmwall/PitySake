import sys, os
from utilities import Archivist, Negotiator

from settings.config import PATHWAYS



event = 0

# data = {
#     "Previous event": {
#         "Page": False,
#         "Row": False
#     },
#     "Current event": {
#         "Page": False,
#         "Row": False
#     }
# }

class Mathematician:
    def __init__(self):
        pass


    def calculate_attempts(self, negotiator, event_term="Win", calc_current=False, max_value=90):
        # event_term = data_options["Term"]["Event"]
        # Assist with calculating event occurrence depending on page and row, with 5 rows presented per page
        
        # Decide whether to calculate current estimate (current is Page 1, Row 1, then set previous), 
        # or distance between historical event (set both current and previous).
        if calc_current:
            max_value -= 1
            current_page, current_row = 1, 1
        else:
            print(f"\nWhen did the current {event_term} occur?")
            current_page = negotiator.request_numeral("Page", lower_limit=1)
            current_row = negotiator.request_numeral("Row", 1, 5)
        print(f"\nPage {current_page}, Row {current_row}")
        
        # Calculate maximum page considering 5 per page
        max_page = int(max_value/5 + current_page)
        print(f"\nWhen did the previous {event_term} occur?")

        # If the current event occupies the 5th and last row, the previous event must be on next page or higher 
        if current_row == 5:    
            previous_page = negotiator.request_numeral("Page", current_page+1, max_page)
        else: 
            previous_page = negotiator.request_numeral("Page", current_page, max_page)

        # If current is on row 4 on the same page as the previous, row 5 is the only option for the previous
        if current_page == previous_page:   
            previous_row = 5 if current_row == 4 else negotiator.request_numeral("Row", current_row+1, 5)

        # If the previous event occurred maximum possible page, row can at most be the same as current row, as to not exceed the limit value, which means 1 if current is 1
        elif previous_page == max_page and not calc_current: 
            previous_row = 1 if current_row == 1 else negotiator.request_numeral("Row", upper_limit=current_row)
        else:
            previous_row = negotiator.request_numeral("Row", 1, 5)
        print(f"\nPage {previous_page}, Row {previous_row}")

        event = 5*(previous_page - current_page) + previous_row - current_row

        print("\nSummary")
        print(f"  Previous event | Page: {previous_page:3} | Row: {previous_row}")
        if not calc_current: 
            print(f"  Current event  | Page: {current_page:3} | Row: {current_row}")
            print(f"  Attempts: {event}")
        else: 
            print(f"  Next attempt at: {event+1}")
        
        return event+1 if calc_current else event



def tracker(update, data, data_action):
    quit()

    previous_data = arciv.reader(file)
    selectable_options = dict()
    numeral = 1

    print("-"*50, f"\nSelect event among:")
    for option in data_options:
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
    
    if update == 1:
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
    elif update == 2:
        progress_name = "Previous event"
        output = data
    elif update == 3:
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


    updated_progress = arciv.join_data(file, progress, None, static=True)
    arciv.writer(file, updated_progress)

    return data


def main():
    quit()

    arciv = Archivist(PATHWAYS["Directory"])
    negotiator = Negotiator()
    file = os.path.join(PATHWAYS["Directory"], PATHWAYS["Progress"])
    data_options = arciv.reader(PATHWAYS["Options"], join="settings")
    attempt_term = data_options["Term"]["Attempt"]
    event_term = data_options["Term"]["Event"]


    opt_1 = f"Calculate {attempt_term}"
    opt_2 = f"Update current {attempt_term}/status"
    opt_3 = f"Show current {attempt_term}"

    action = negotiator.listed_options("Select action among", [opt_1, opt_2, opt_3])

    if action == opt_1:
        event = calculate_attempts()
        print(f"Result: {event}")
        quit()

    if action == opt_2:
        upd_opt_1 = "Add attempts"
        upd_opt_2 = f"Calculate {attempt_term} from last {event_term}"
        upd_opt_3 = "Update chance of next outcome"
        
        update = negotiator.listed_options("Update options:", [upd_opt_1, upd_opt_2, upd_opt_3])

        if update == upd_opt_3:
            value = negotiator.listed_options("Set status:", [data_options[event_term]["State"]])
        else:    
            negotiator.request_numeral("", 0, 90)
                
        tracker(update, value, update)


        


    report = arciv.reader(file)
    print("\nData report:")
    try:
        for x in report.keys():
            print(f"\n{x}")
            for y, z in report[x].items():
                print(f"   {y:16}{z}")
    except:
        print("No data to show.")
    print()


# negotiator = Negotiator()
# calc = Mathematician()
# calc.calculate_attempts(negotiator, calc_current=True)

