import json, os, shutil, msvcrt



class Archivist:
    def __init__(self, data_directory:str, settings_directory:str):
        """
        File and data actions for JSON and dictionary data. 

        Functions: reader, writer, confirm_action, backup, join_data
        """
        self.data_directory = data_directory
        self.settings_directory = settings_directory

    def reader(self, file:str, join="none"):
        """
        Read and return JSON file.

        file : directory of file as string.
        join : set to string "data" or "settings", if *file* is a located within of *self.data_directory* or *self.settings_directory*.
        """

        if join == "data":
            file = os.path.join(self.data_directory, file)
        elif join == "settings":
            file = os.path.join(self.settings_directory, file)
        elif join != "none":
            print("Invalid value of pathway indicator 'join'.")

        if os.path.exists(file):
            try:
                with open(file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                print(f"\nFile at {file} could not be read:\n{e}")
                # sys.exit()



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



    def backup(self, file:str, backup_frequency:list[int], datatype:str):
        """
        Automated backup in multiple files.
        Returns: bool

        file : directory of file as string.  
        backup_frequency : list length sets the number of backup files; integers specifies number of edits between every backup.
        datatype : sets name prefix to specify identify of backup data.
        """
        
        # Call file containing edit count info for all files
        meta_file = os.path.join(self.data_directory, "meta.json")
        try:
            edit_meta = self.reader(meta_file)
        except:
            edit_meta = dict()

        try:    
            file_edit_count = edit_meta[file]
        except:
            file_edit_count = 0
            

        backup_file = False
        
        # Check backup frequencies and set backup file path if any frequency condition is met and update edit meta
        for value in backup_frequency:
            if file_edit_count > 0 and file_edit_count % value == 0:
                backup_file = os.path.join(self.data_directory, datatype.lower() + f"_backup_{value}.json")
                break        

        edit_meta[file] = file_edit_count + 1
        self.writer(meta_file, edit_meta)
        

        try:
            file_length = len(self.reader(file))
        except:
            file_length = 0

        if backup_file and os.path.exists(backup_file):
            backup_length = len(self.reader(backup_file))
        else:
            backup_length = 0


        # Compare contents of backup and current data
        if backup_length > file_length+2:
            confirm_backup = self.confirm_action("\nWARNING!\nBackup datalength is larger than that of current file.\nIf you have not removed data entries: abort and check data health.\nBackup anyway?\n")
        else:
            confirm_backup = True

        if not backup_file:
            return True
        elif confirm_backup:
            shutil.copy(file, backup_file)
            print("\nData backup performed.")
            return True
        else:
            return False
        


    def join_data(self, file:str, new_data:dict, name:str, update=False, static=False):
        """
        Update library with new or edited data. Returns: bool

        file : directory of file as string.  
        new_data : data to be included in file.  
        name : id of new data entry.  
        static : marks files that are not expected to increase in length.
        """

        data = self.reader(file)

        if type(data) is dict: 
            original_length = len(data) 
        else: 
            original_length = 0
            data = dict()

        if name == "Remove":
            print("\nRemoval requested. Enter name of item to remove.")
            name = input("Name: ")
            
            try:
                data.pop(name)
            except:
                return False
            
            if len(data) != original_length-1: 
                print("\nError occurred!\nLibrary update aborted.\n")
                return False
            
            return data
            

        # Add existing data to library
        if name in data.keys() and not static:
            # update = False
            # update = self.confirm_action("\nObject already exists in library.\nAdd anyway?")
            data.update(new_data)
            
            if len(data) != original_length and not update: 
                print("\nError occurred!\nLibrary update aborted.\n")
                return False
            # elif update:
            #     return data
        else:
            data.update(new_data)
        
        data = dict(sorted(data.items()))
        
        # Checking data validity depending on action. 
        if len(data) != original_length+1 and not update and not static:
            print("\nError occurred!\n\nLibrary update aborted.")
            return False
        else:
            return data
        

        
    def writer(self, file:str, data):
        """
        Write JSON to file. Returns: bool
        """
        try:
            with open(file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
                return True
        except Exception as e:
            print("Error occurred while attempting to write. Check file health and backups.")



class Negotiator:
    def __init__(self):
        """
        Functions for requesting and managing user input and listing options for checkpoints or data collection.

        Functions: request_key, listed_options, auto_options
        """

        self.quit_key = "q"
        self.separator = "-"*50
        self.indent = 3

    def request_key(self, options:list, enforced=False, return_string=False):
        """
        General function for recording input with checks against conditions. Returns: int or str

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

        
    def request_numeral(self, message:str, lower_limit=False, upper_limit=False):
        """
        Request a numerical value within limits (optional). Returns: int

        message : explanatory text
        lower_limit : lowest value allowed
        upper_limit : highest value allowed
        """
        # print()
        # print(message)
        lower_message, lower_switch = "", 0
        upper_message, upper_switch = "", 0
        if lower_limit: lower_message, lower_switch = " from ", 1
        if upper_limit: upper_message, upper_switch = " up to ", 1
        message = message + f"{lower_message}{lower_limit}"*lower_switch + f"{upper_message}{upper_limit}"*upper_switch

        while True:
            # print("Enter value: ")
            
            # print(f"Press {self.quit_key.upper()} to quit.")

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
        Cycles through categories and subcategories and requests input as value or alternative within list. Returns: dict 

        message : explanatory text
        collection : dict with format *{category_key: input_options}*, where *input_options* should be either the exact string: "enter numeral", or a list.
        """

        output = dict()
        print(message)
        for category in collection.keys():
            
            selectable_options = dict()

            # print(collection)
            numeral = True if collection[category] == "enter numeral" else False
            string = True if collection[category] == "enter string" else False
            preset = True if collection[category] == "enter preset" else False
            if preset and not preset_values:
                print(f"Preset value for {collection} {category} missing.")
            # if option == "enter numeral": print("Enter value:")
                # numeral = True
            # print(numeral, string, preset)
            if numeral: 
                selection = self.request_numeral(f"Enter value for {category}")
            elif string: 
                selection = input(f"Enter {category}: ")
            elif preset:
                selection = preset_values[category]
            # preset = True if collection[category] == "enter preset" else False
            # while numeral:
            #     print("Enter value:")
            #     try:
            #         selection = int(input())
            #         break
            #     except:
            #         print("Enter valid number.")

            if numeral or preset:
                output[category.capitalize()] = selection
            else:
            # if not numeral and not preset:
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
            # else:
            #     output[category.capitalize()] = selection
            # print(type(selection))

        return output
