import msvcrt
import re



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
        self.separator = "-"*50
        self.indent = 3



    def request_key(self, options:list, enforced=False, return_string=False):
        """
        General function for recording input with checks against conditions.  
        Returns: int or str

        options : list of conditions.
        enforced : set True to demand input for critical actions or preventing loss of data.
        return_string : set output type as int or str
        """

        # Record keyboard input. Input not inlcuded among valid options will quit the script unless enforced, for critical options. 
        if not enforced: print(f"\n{" ":3}{self.quit_key.upper():2} Quit\n")
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


    def confirm_action(self, message:str, abort=True):
            """
            Yes/No selection to verify critical action. Returns: bool or quits

            message : text for clarification or warning
            abort : set True to quit if negatory
            """
            
            print(message, "\n  N: No\n  Y: Yes")
            selection = self.request_key(["n", "N", "y", "Y"], enforced=True, return_string=True)
            if selection.lower() == "y":
                return True
            elif abort:
                print("\nAborted, good bye.\n")
                quit()
            else:
                return False


    def request_word(self, message:str, prompt:str, enforced=False):
        """
        Function for recording typed user input, checking for special characters or incorrect format.

        message : explanatory text
        prompt : user promt text, e.g. 'Enter key:'
        """

        print(f"\n{self.separator}")
        print(f"\n{message}")
        if not enforced: print(f"\n{self.quit_key.upper():2} Quit\n")
        while True:
            word = input(f"{prompt}: ")
            if not word.isalnum():
                for symbol in word:
                    if not symbol.isalnum() and symbol not in ("-", " "): 
                        print("Invalid characters detected.")
                        word = False
                        break
            if not word: continue
            
            if not enforced and word.lower() == self.quit_key:
                print("\nQuitting, good bye.\n")
                quit()
            elif "  " in word:
                print("Multiple whitespaces in a row.")
            elif len(word) > 40 or len(word) < 3 or len(set(word)) == 1:
                print("Invalid format.")
            else:
                return word

        
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
            numeral = True if "enter numeral" in collection[category] else False
            string = True if collection[category] == "enter string" else False
            preset = True if collection[category] == "enter preset" else False
            if preset and not preset_values:
                print(f"Preset value for {collection} {category} missing.")
                quit()

            if numeral: 
                limits = collection[category].split("|")
                try:
                    min_value, max_value = int(limits[1]), int(limits[2])
                except ValueError:
                    raise ValueError(f"Could not convert string limit number to integer. Check data options file.")
                selection = self.request_numeral(
                    f"Enter value for {category}",
                    lower_limit=min_value, upper_limit=max_value)
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