import datetime

from settings.config import PATHWAYS, TERMS
from event_calculator import Mathematician


class Librarian:
    def __init__(self, arciv, negotiator):
        """
        Manager for collecting and organizing information for database.
        Functions: collect_settings, enter_data, enter_event, reciter

        arciv: class needed for file management
        negotiator: class needed for collecting user input
        """

        self.arciv = arciv
        self.negotiator = negotiator
        self.eventref = TERMS["Event"]
    

    def collect_settings(self, keywords):
        """
        Single reading of config file to return settings as list or single element.
        
        keywords : list of keys to locate settings.
        """
        data_options = self.arciv.reader(
            other_file=PATHWAYS["Options"], 
            join="settings")
        
        if keywords is list:
            settings = list()
            for key in keywords:
                settings.append(data_options[key])
            return settings
        else:
            return data_options[keywords]


    def enter_data(self, name:str, data_options):
        """
        Collect basic info about new library entry.  
        Returns: single-entry dictionary.

        name : str, identifier for object in library.
        """

        # Enter object details
        new_object = dict()
        new_object[name] = self.negotiator.auto_options(
            f"\nEnter details for {name}",
            data_options)
        
        # Print entered data for review
        print(f"\nSummary for {name}:")
        for x, y in new_object[name].items():
            print(f"  {x:14} {y}")

        return new_object


    def enter_event(self, name:str, event_options, object_type, event_term, updated_object=False):
        """
        Collect historical acquisition data for object in library.  
        Returns: single-entry dictionary with updated object.

        name : str, identifier for object in library.
        event_options : selectable opions as a list if simple object, or as a dict for detailed object.
        misc_object : switch for simple object (True) or detailed object (False).
        """

        if not updated_object:
            updated_object = dict()
            try:
                updated_object[name] = self.arciv.reader()[name]
            except:
                print(f"\n{name} must be added to library before registering event.",
                    "\nCheck library content or spelling.")
                quit()

        # Simple objects: 
        # Register single value and skip further collection
        if object_type==TERMS["Misc"]:
            # event = TERMS["collection"]
            updated_object[name][event_term] = self.negotiator.request_numeral(
                f"\nEnter {event_term} for {name}",
                lower_limit=0,
                upper_limit=6)

            return updated_object
        
        # Detailed objects:
        # Step 1: Registration and validation of date received
        now = datetime.datetime.now()
        now = now.strftime("%y") + now.strftime("%m") + now.strftime("%d")
        while True:
            event_date = input(f"\nEnter event date as YYMMDD: ")
            try:
                date_validity = datetime.datetime(
                    int("20"+event_date[0:2]),
                    int(event_date[2:4]), 
                    int(event_date[4:6]))
                # date_int = int(event_date)
            except ValueError as e:
                print(f"Invalid format, try again.\n{e}")
                continue
            except Exception as e:
                print(f"Invalid input, try again.\n{e}")
                continue

            if len(event_date) != 6:
                print("Incorrect date length")
            elif int(event_date) > int(now) or int(event_date) < 200927:
                print("Impossible date. Try again.")
            else:
                break

        # Step 2: Check content of previous data and create dict if needed
        # Create an event ID numeral
        if not self.eventref in updated_object[name].keys():
            updated_object[name][self.eventref] = dict()
            event_count = 0
        else:
            event_count = len(updated_object[name][self.eventref].keys())
        event_name = f"{event_date}-{event_count}"
        
        # Step 3: Determine attempts during event to reach acquisition
        # Calls calculator if needed
        # Adjust settings if no attempts (received through other means)
        attempt_term = TERMS["Attempt"]
        attempt = False
        presets = dict()

        method_calc = f"Calculate {attempt_term}"
        method_enter = f"Enter {attempt_term}"
        method_skip = f"No {attempt_term} - skip"
        attempt_method = self.negotiator.listed_options(
            "Select option", 
            [method_calc, method_enter, method_skip])

        if attempt_method == method_calc:
            # Calculation assistant class called only if needed
            mathemate = Mathematician()
            attempt = mathemate.calculate_attempts(
                self.negotiator, 
                event_term=self.eventref)
        elif attempt_method == method_enter:
            attempt = self.negotiator.request_numeral(
                f"\nEnter value for {attempt_term}: ", 
                lower_limit=0, 
                upper_limit=90)
        else:
            event_options[TERMS["Event name"]] = "enter preset"
            presets[TERMS["Event name"]] = TERMS["Gift"]
            event_options["State"] = "enter preset"
            presets["State"] = False

        presets[attempt_term] = attempt

        # Step 4: Define source
        # Adjust settings if standard event
        if not attempt_method == method_skip:
            state_preset = self.negotiator.listed_options(
                f"Was item received from {TERMS["Standard source"]}?",
                ["Yes", "No"])
            if state_preset == "Yes":
                event_options["Source"] = "enter preset"
                presets["Source"] = TERMS["Standard source"]
                event_options["State"] = "enter preset"
                presets["State"] = False
        
        # Step 5: Create dictionary entry from above settings
        updated_object[name][self.eventref][event_name] = self.negotiator.auto_options(
            f"\nEnter details for {name} {self.eventref}",
            event_options, 
            preset_values=presets)

        return updated_object
    

    def edit_data(self, name, library, object_type, data_options, action_selection, event_term):
        """
        ...
        """
        edited_object = {name: library[name]}
        # print(edited_object[name][self.eventref].keys())
        if action_selection == self.eventref:
            print(2)
            try:
                change_options = list(edited_object[name][self.eventref].keys())
            except:
                print(f"No {self.eventref}s registered for {name}.\nQuitting, good bye.\n")
                quit()
            event = self.negotiator.listed_options(f"Select among {self.eventref}s", change_options)
            event_change = self.negotiator.listed_options(f"What change to you wish to perform for {self.eventref}: {event}", ["Change", "Remove"])
            
            edited_object[name][self.eventref].pop(event)
            if event_change == "Change":
                edited_object = self.enter_event(name, data_options, object_type, event_term, updated_object=edited_object)
            print("check!")
        elif action_selection == "Basic info":
            print(edited_object)
            if self.eventref in edited_object[name].keys():
                event_data = edited_object[name][self.eventref]
            else:
                event_data = False
            edited_object = self.enter_data(name, data_options)
            # print(event_data)
            if event_data: edited_object[name][self.eventref] = event_data
            # print(edited_object)
            # quit()

        return edited_object


    def reciter(self, library:dict, object_type, action_selection, file, indent=0, separation=1):
        """
        Print contents of library.
        Returns: print and return string structured as table, formatted suitable for markdown view.
        """

        if not isinstance(library, dict):
            raise TypeError("Not dict.\nLibrarian.reciter: I cannot read that.\n")
            
        library = dict(sorted(library.items()))
        report = str()
        # Although some variation is adapted for, take into account that data may very in keys:value pairs present, and also format and order. 

        # Check point to create report from database by-date sorted string, otherwise continues with by-entry 
        if action_selection == "By date":
            library_datewise = dict()
            data = []
            n = 1
            row_indent = 0
            # Cycle through and collect nested dictionary data
            for entry in library.keys():
                title = str()
                if self.eventref in library[entry].keys():
                    events = library[entry][self.eventref]
                    for event, info in events.items():
                        title = str(event[:6])
                        details = str()
                        for detail in dict(sorted(info.items())).values():
                            if not detail: detail = "-"
                            if type(detail) is int: data.append(detail)
                            # space = 6 if len(str(detail)) < 5 else row_indent
                            space = 0
                            details += f",{detail:{space}}" 
                        # Re-structure info into new dictionary
                        library_datewise.update({f"{title}-{str(n)}": f"{entry:}{details}"})
                        n += 1
                else:
                    title = f"NoDate-{n}"
                    library_datewise.update({title: f"{entry:{row_indent}}"})
                    n += 1
            library_datewise = dict(sorted(library_datewise.items()))

            # Generate final report format and print
            cutaway = 70
            # report += f"```"
            report += f"\n{"Date"},{"Name"},{TERMS["Attempt"]},{"Source":{row_indent}},{"State"}"[:cutaway]
            for event in library_datewise.keys():
                report += f"\n{event[:6]},{library_datewise[event]}"[:cutaway]
            # report += f"\n```"
            print(report)
            # avg = sum(data)/len(data)
            # print(round(avg, 1))

            # report += f"\n\nFile source: {file}"
            
            return report  


        # Create report  from database sorted by entry
        report = f"# {object_type.capitalize()} library\n\n"
        sub_indent = 10
        for entry in library.keys():
            print(f"{"\n"*separation*2}{"":{indent}}{entry.upper():20}{"\n"*separation*0}")
            report += f"\n\n## {entry.capitalize()}\n\n"
            spacing = str()
            # Cycle through and collect/print nested dictionary data
            for key, info in library[entry].items():
                if not info:
                    continue
                if type(info) is dict:
                    info = dict(sorted(info.items()))
                    print(f"{"":{indent}}{"":{sub_indent}}{key:10}")
                    report += f"\n\n```\n"
                    event_data =str()
                    for event in info.keys():
                        new_event = f"{event[:6]}   "
                        for category, value in dict(sorted(info[event].items())).items():
                            if not value: value = f"{"-":5}"
                            space = 22 if len(str(value)) > 5 else 5
                            new_event += f"{category}: {str(value):{space}}"
                        print(f"{"":{indent+sub_indent*2}}{new_event}")
                        event_data += new_event+"\n"
                    report += event_data+"```"
                else:
                    print(f"{"":{indent}}{"":{sub_indent}}{key:10}{info}")
                    report += f"{spacing}{info}"
                    spacing = " | "
                    
        report += f"\n\nFile source: {file}"

        return report
    

    def status(self):
        pass