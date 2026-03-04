import msvcrt



class Negotiator:
    def __init__(self):
        """
        Functions for requesting and managing user input and listing options for checkpoints or data collection.

        Functions: request_key, listed_options, auto_options
        """

        self.quit_key = "q"
        self.separator = "-"*50
        self.indent = 3


    def confirm_action(self, message:str):
            """
            Checkpoint to verify action. Returns: bool

            message : text for clarification or warning,
            """
            
            print(message)
            print("  Any: No\n  Y:   Yes")
            while True:
                if msvcrt.kbhit():
                    selection = msvcrt.getch().decode("ASCII").lower()
                    if selection == "y":
                        return True
                    else:
                        print("\nAborted, good bye.\n")
                        quit()    


    def request_key(self, options:list, enforced=False, return_string=False):
        """
        General function for recording input with checks against conditions.  
        Returns: int or str

        options : list of conditions.
        enforced : set True to demand input for critical actions or preventing loss of data.
        return_string : set output type as int or str
        """

        # Record keyboard input. Input not inlcuded among valid options will quit the script unless enforced, for critical options. 
        quitting = self.quit_key.upper()
        if not enforced: print(f"\n{" ":3}{quitting:2} Quit")
        while True:
            if msvcrt.kbhit():
                try:
                    key = msvcrt.getch().decode("ASCII")
                except:
                    key = "none"
                    
                if key in options:
                    # Depending on whether output is to be used as a key or index its type can be adjusted.
                    return key if return_string else int(key)

                elif not enforced and key.lower() == self.quit_key:
                    print("\nQuitting, good bye.\n")
                    quit()

        
    def request_numeral(self, message:str, lower_limit=None, upper_limit=None):
        """
        Request a numerical value within limits (optional).  
        Returns: int

        message : explanatory text
        lower_limit : lowest value allowed
        upper_limit : highest value allowed
        """

        lower_message, lower_switch = "", 0
        upper_message, upper_switch = "", 0
        if lower_limit is not None: lower_message, lower_switch = " from ", 1
        if upper_limit is not None: upper_message, upper_switch = " up to ", 1
        message = message + f"\n{lower_message}{lower_limit}"*lower_switch + f"{upper_message}{upper_limit}"*upper_switch

        while True:
            value = input(f"{message}: ")
            if value == self.quit_key.lower():
                print("\nQuitting, good bye.\n")
                quit()

            try:
                value = int(value)
            except:
                print("Enter valid number.")
                continue
            
            if not lower_limit and not upper_limit:
                return value
            
            if type(lower_limit) == int and type(upper_limit) == int:
                if lower_limit >= upper_limit:
                    print("Lower limit value must be smaller than upper limit value.")
                    continue

            if type(lower_limit) == int:
                if value < lower_limit:
                    print(f"\nValue must be at least {lower_limit}.")
                    continue

            if type(upper_limit) == int:
                if value > upper_limit: 
                    print(f"\nValue cannot be higher than {upper_limit}.")
                    continue
            
            return value


    def listed_options(self, message:str, options:list):
        """
        Lists options and returns corresponding value.

        message : explanatory text
        options : listed as option and also returned as values
        """
        
        print(f"\n{self.separator}")
        print(message)
        counter = 1
        for alternative in options:
            print(f"{" ":3}{str(counter):2} {alternative}")
            counter += 1
        string_selectors = [str(num) for num in range(1,len(options)+1)]
        selection = self.request_key(string_selectors)-1

        return options[selection]


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
            numeral = True if collection[category] == "enter numeral" else False
            string = True if collection[category] == "enter string" else False
            preset = True if collection[category] == "enter preset" else False
            if preset and not preset_values:
                print(f"Preset value for {collection} {category} missing.")
                quit()

            if numeral: 
                selection = self.request_numeral(f"Enter value for {category}")
            elif string: 
                selection = input(f"Enter {category}: ")
            elif preset:
                selection = preset_values[category]

            if numeral or preset:
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