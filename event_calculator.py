


# event = 0

class Mathematician:
    def __init__(self):
        pass


    def calculate_attempts(self, negotiator, max_value, event_term="Win", calc_current=False):
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


    def statistician(self):
        pass


