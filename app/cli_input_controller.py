import msvcrt

import streamlit as st



class Negotiator:
    def __init__(self):
        """
        Requesting, validating and returning user input.

        | Name            |  Application                      |
        |:----------------|:----------------------------------|
        | confirm_action  |: user input checkpoint            |
        | request_key     |: require single key confirmation  |
        | request_word    |: input text with valid symbols    |
        | request_numeral |: input numerical within limits    |
        | listed_options  |: select among numerical options   |
        | auto_options    |: generate dictionary from options |
        """

        self.quit_key = "q"
        self.systems_key = "s"
        self.separator = "-"*50
        self.indent = 3



    def request_key(self, options:list, is_enforced=False, needs_int=False, return_string=False, show_systems=False):
        """
        General function for recording input with checks against conditions.  
        Returns: int or str

        options : list of conditions.
        is_enforced : set True to demand input for critical actions or preventing loss of data.
        return_string : set output type as int or str
        """

        # Validation
        if needs_int:
            for x in options:
                if type(x) is not int: 
                    print("ERROR not numeral")                
                    quit()
                
        # Record keyboard input. Input not inlcuded among valid options will quit the script unless enforced, for critical options. 
        print()
        if show_systems: print(f"{" ":3}{self.systems_key.upper():2} Systems")
        if not is_enforced: print(f"{" ":3}{self.quit_key.upper():2} Quit\n")
        while True:
            if msvcrt.kbhit():
                try:
                    key = msvcrt.getch().decode("ASCII")
                except:
                    key = "none"

                if not is_enforced and key.lower() == self.quit_key:
                    print("\nQuitting, good bye.\n")
                    quit()
                elif show_systems and key.lower() == self.systems_key:
                    return "systems"
                
                if needs_int: key = self._return_numeral(key)

                if key in options:
                    # Depending on whether output is to be used as a key or index its type can be adjusted.
                    return key if return_string else self._return_numeral(key)
        

    def _return_numeral(self, input):
        try:
            output = int(input)
            return output
        except:
            print("Enter valid number.")
            return False



    def confirm_action(self, message:str, is_enforced=False):
            """
            Yes/No selection to verify critical action. Returns: bool or quits

            message : text for clarification or warning
            is_enforced : set True to quit if negatory
            """
            
            while True:
                print(message, "\n  N: No\n  Y: Yes")
                selection = self.request_key(["n", "N", "y", "Y"], is_enforced=True, return_string=True)
                if selection.lower() == "y":
                    return True
                elif not is_enforced and selection.lower() == "n":
                    print("\nAborted, good bye.\n")
                    quit()
                elif selection.lower() == "n":
                    return False
                else:
                    print("Select one.")


    def request_word(self, message:str, user_prompt:str, is_enforced=False):
        """
        Function for recording typed user input, checking for special characters or incorrect format.

        message : explanatory text
        user_prompt : user instructions, e.g. 'Enter key:'
        """

        print(f"\n{self.separator}")
        print(f"\n{message}")
        if not is_enforced: print(f"\n{self.quit_key.upper():2} Quit\n")
        while True:
            user_input = input(f"{user_prompt}: ")
            if not user_input.isalnum():
                for symbol in user_input:
                    if not symbol.isalnum() and symbol not in ("-", " "): 
                        print("Invalid characters detected.")
                        user_input = False
                        break
            if len(user_input) == 0:
                print("Cannot be empty.")
                continue
            
            if not is_enforced and user_input.lower() == self.quit_key:
                print("\nQuitting, good bye.\n")
                quit()
            elif "  " in user_input:
                print("Multiple whitespaces in a row.")
            elif len(user_input) > 40 or len(user_input) < 3 or len(set(user_input)) == 1:
                print("Invalid format.")
            else:
                return user_input

        
    def request_numeral(self, message:str, lower_limit:int=None, upper_limit:int=None):
        """
        Request a numerical value within limits (optional).  
        Returns: int

        message : explanatory text
        lower_limit : lowest value allowed
        upper_limit : highest value allowed
        """
        
        lower_message, lower_switch = "", 0
        upper_message, upper_switch = "", 0
        if lower_limit: lower_message, lower_switch = "From ", 1
        if upper_limit: upper_message, upper_switch = " up to ", 1
        message = message + f" ({self.quit_key.upper()} to quit)" + f"\n{lower_message}{lower_limit}"*lower_switch + f"{upper_message}{upper_limit}"*upper_switch

        while True:
            user_input = input(f"{message}: ")
            if user_input == self.quit_key.lower():
                print("\nQuitting, good bye.\n")
                quit()

            try:
                user_input = int(user_input)
            except:
                print("Enter valid number.")
                continue
            
            if not lower_limit and not upper_limit:
                return user_input
            
            if type(lower_limit) == int and type(upper_limit) == int:
                if lower_limit >= upper_limit:
                    print("Lower limit value must be smaller than upper limit value.")
                    continue

            if type(lower_limit) == int:
                if user_input < lower_limit:
                    print(f"\nValue must be at least {lower_limit}.")
                    continue

            if type(upper_limit) == int:
                if user_input > upper_limit: 
                    print(f"\nValue cannot be higher than {upper_limit}.")
                    continue
            
            return user_input


    def listed_options(self, message:str, options:list, allow_systems=False):
        """
        Lists options and returns corresponding value.

        message : explanatory text
        options : listed as option and also returned as values
        """
        
        print(f"{self.separator}")
        print(message)
        counter = 1
        for alternative in options:
            print(f"{" ":3}{str(counter):2} {alternative}")
            counter += 1
        string_selectors = [str(num) for num in range(1,len(options)+1)]
        selection = self.request_key(string_selectors, show_systems=allow_systems)

        return options[selection-1] if not selection == "systems" else selection


    def auto_options(self, message:str, collection:dict, preset_values:dict=False):
        """
        Cycles through categories and subcategories and requests input as value or alternative within list.  
        Returns: dict 

        message : explanatory text
        collection : dict with format *{category_key: input_options}*, where *input_options* should be either the exact string: "enter numeral", or a list.
        """

        output = dict()
        print(message)
        for category in collection.keys():
            selectable_options = dict()
            needs_numeral = True if "enter numeral" in collection[category] else False
            needs_string = True if collection[category] == "enter string" else False
            needs_preset = True if collection[category] == "enter preset" else False
            if needs_preset and not preset_values:
                print(f"Preset value for {collection} {category} missing.")
                quit()

            if needs_numeral: 
                limits = collection[category].split("|")
                try:
                    min_value, max_value = int(limits[1]), int(limits[2])
                except ValueError:
                    raise ValueError(f"Could not convert string limit number to integer. Check data options file.")
                selection = self.request_numeral(
                    f"Enter value for {category}",
                    lower_limit=min_value, upper_limit=max_value)
            elif needs_string: 
                selection = input(f"Enter {category}: ")
            elif needs_preset:
                selection = preset_values[category]

            if needs_numeral or needs_preset:
                output[category.capitalize()] = selection
            else:
                print(f"\n{self.separator}")
                print(f"Select {category} among:")
                counter = 1
                for option in collection[category]:
                    selectable_options[str(counter)] = option
                    print(f"{" ":3}{str(counter):2} {option}")
                    counter += 1
                selection = self.request_key(selectable_options.keys(), return_string=True)
                output[category.capitalize()] = selectable_options[selection]
                print(f"\nSelection: {selectable_options[selection]}")

        return output
    

