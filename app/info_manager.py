import datetime


class Librarian:
    def __init__(self, DATAPATH, SETTINGS, TERMS, arciv, negotiator):
        """
        Manager for collecting and organizing information for database.
        Functions: collect_settings, enter_data, enter_event, reciter

        arciv: class needed for file management
        negotiator: class needed for collecting user input
        """

        self.datapath = DATAPATH
        self.settings = SETTINGS
        self.terms = TERMS
        self.arciv = arciv
        self.negotiator = negotiator
        
        self.eventref = self.terms["Event"]
    

    def collect_settings(self, keywords):
        """
        Single reading of config file to return settings as list or single element.
        
        keywords : list of keys to locate settings.
        """
        data_options = self.arciv.reader(
            other_file=self.settings["Options"], 
            join_path="settings")

        if type(keywords) is list:
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


    def enter_event(self, mathemate, name:str, event_options:list, object_type, event_term, updated_object=False):
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
        if object_type == self.terms["Misc"]:
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
        
        # Step 3: Determine source and attempts during event to reach acquisition
        # Calls calculator if needed
        # Adjust settings if no attempts (received through other means)
        attempt_term = self.terms["Attempt"]
        attempt = False
        presets = dict()

        method_calc = f"Calculate {attempt_term}"
        method_enter = f"Enter {attempt_term}"
        method_skip = f"No {attempt_term} - skip"
        attempt_method = self.negotiator.listed_options(
            "Select option", 
            [method_calc, method_enter, method_skip])

        # Define source
        # Adjust settings if standard event
        if not attempt_method == method_skip:
            limit_data, source_options = self.collect_settings(["Limit", "Source"])
            state_preset = self.negotiator.listed_options(
                f"Was item received from {self.terms["Standard source"]}?",
                ["Yes", "No"])
            if state_preset == "Yes":
                # event_options["Source"] = "enter preset"
                presets["Source"] = self.terms["Standard source"]
                event_options["State"] = "enter preset"
                presets["State"] = False
                limit = limit_data["Standard"]
            else:
                presets["Source"] = self.negotiator.listed_options("Select source", source_options)
                limit = limit_data[object_type][presets["Source"]]

        # Define attempts
        if attempt_method == method_calc:
            # Calculation assistant class called only if needed
            attempt = mathemate.calculate_attempts(self.negotiator, max_value=limit, event_term=self.eventref)
        elif attempt_method == method_enter:
            attempt = self.negotiator.request_numeral(
                f"\nEnter value for {attempt_term}: ", 
                lower_limit=0, 
                upper_limit=limit)
        elif attempt_method == method_skip:
            # event_options["Source"] = "enter preset"
            presets["Source"] = self.terms["Gift"]
            event_options["State"] = "enter preset"
            presets["State"] = False

        presets[attempt_term] = attempt

        # Step 4: Create dictionary entry from above settings
        updated_object[name][self.eventref][event_name] = self.negotiator.auto_options(
            f"\nEnter details for {name} {self.eventref}",
            event_options, 
            preset_values=presets)

        return updated_object
    

    def edit_data(self, mathemate:classmethod, name:str, library:dict, object_type:str, data_options:dict, action_selection:str, event_term:str):
        """
        ...
        """

        edited_object = {name: library[name]}
        if action_selection == self.eventref:
            try:
                change_options = list(edited_object[name][self.eventref].keys())
            except:
                print(f"No {self.eventref}s registered for {name}.\nQuitting, good bye.\n")
                quit()
            event = self.negotiator.listed_options(f"Select among {self.eventref}s", change_options)
            event_change = self.negotiator.listed_options(f"What change to you wish to perform for {self.eventref}: {event}", ["Change", "Remove"])
            
            edited_object[name][self.eventref].pop(event)
            if event_change == "Change":
                edited_object = self.enter_event(mathemate, name, data_options, object_type, event_term, updated_object=edited_object)
        elif action_selection == "Basic info":
            if self.eventref in edited_object[name].keys():
                event_data = edited_object[name][self.eventref]
            else:
                event_data = False
            edited_object = self.enter_data(name, data_options)

            if event_data: edited_object[name][self.eventref] = event_data

        return edited_object


    def reciter(self, library:dict, object_type:str, action_selection:str, file:str, indent:int=0, separation:int=1):
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
            space = 0
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
                            
                            details += f",{detail:<{space}}" 
                        # Re-structure info into new dictionary
                        library_datewise.update({f"{title}-{str(n)}": f"{entry:<{row_indent}}{details}"})
                        n += 1
                else:
                    title = f"NoDate-{n}"
                    library_datewise.update({title: f"{entry:<{row_indent}}"})
                    n += 1
            library_datewise = dict(sorted(library_datewise.items()))

            # Generate final report format and print
            cutaway = 70
            row_indent = 20
            # report += f"```"
            report += f"\n{"Date":6},{"Name":<{space}}, {self.terms["Attempt"]:<{space}}, {"Source":<{space}}, {"State"}"
            for event in library_datewise.keys():
                report += f"\n{event[:6]},{library_datewise[event]}"
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
    

    def status(self, mathemate, object_type:str):
        """
        Check and update progress data, with assistant systems for calculation and keeping progress within limits.
        """

        # Collect progress data and options
        progress_data = self.arciv.reader(other_file=self.datapath["Progress"], join_path="data", allow_missing=True)
        limit_data, source_options, state_options = self.collect_settings(["Limit", "Source", "Current state"])

        # Display previous progress data
        if not progress_data or len(progress_data) == 0: 
            progress_data = dict()
            print("No previous data.")
        else:
            print(f"{self.terms["Source"]:25}{self.terms["Attempt"]:6}State")
            for title, info in progress_data.items():
                output = f"{title:25}"
                for detail in info.values():
                    if detail:
                        output += f"{detail:<6}"
                    else:
                        output += str(detail)
                print(output)
        
        # User input to choose source
        # Adapt settings depending on choice
        source_options.append("Standard")
        updated_category = self.negotiator.listed_options(
            f"To update status, select {self.terms["Source"]}:",
            source_options
        )
        if updated_category == "Standard":
            limit = limit_data["Standard"]
        else:
            limit = limit_data[object_type][updated_category]
            if updated_category == self.terms["Temp"]:
                updated_category = f"Character {updated_category}" if object_type==self.terms["Character"] else f"{self.terms["Tool"]} {updated_category}"
        attempt_term = self.terms["Attempt"]

        # Define selectable editing options
        low_value, high_value = 1, 10
        method_calc, method_enter, add_low, add_high = f"Calculate {attempt_term}", f"Enter {attempt_term}", f"Add {low_value}", f"Add {high_value}"
        if updated_category in progress_data.keys():
            option_list = [method_calc, method_enter, add_low, add_high]
        else:
            option_list = [method_calc, method_enter]

        # Select editing option
        # Call methods for collecting data within set limit
        attempt_method = self.negotiator.listed_options(
            "Select option", 
            option_list)
        # Use calculator
        if attempt_method == method_calc:
            attempt = mathemate.calculate_attempts(self.negotiator, max_value=limit, event_term=self.eventref, calc_current=True)
        # Enter numeral directly
        elif attempt_method == method_enter:
            attempt = self.negotiator.request_numeral(
                f"\nEnter value for {attempt_term}: ", 
                lower_limit=0, 
                upper_limit=limit)
        # Add a predefined number one or more times
        elif attempt_method == add_low or attempt_method == add_high:
            added_value = low_value if attempt_method == add_low else high_value
            attempt = progress_data[updated_category][self.terms["Attempt"]]
            repeat = True
            while repeat:
                attempt += added_value
                # When close to limit
                if attempt + added_value > limit:
                    # Decrease increment...
                    if added_value == high_value:
                        added_value = low_value
                        print(f"Can't add more {high_value}s.")
                    # ... or break when limit reached
                    elif added_value == low_value:
                        break
                repeat = self.negotiator.confirm_action(f"\nCurrent {self.terms["Attempt"]}: {attempt}\nAdd another {added_value}?", is_enforced=True)

        # Organize data, create dictionary if there is none
        if not updated_category in progress_data.keys():
                progress_data[updated_category] = dict()
        progress_data[updated_category][self.terms["Attempt"]] = attempt
        if attempt_method == method_calc or attempt_method == method_enter and updated_category != "Standard":
            progress_data[updated_category]["State"] = self.negotiator.listed_options("Set current state", state_options)
        elif updated_category == "Standard":
            progress_data[updated_category]["State"] = None

        return progress_data, updated_category, progress_data[updated_category][self.terms["Attempt"]], progress_data[updated_category]["State"]
   