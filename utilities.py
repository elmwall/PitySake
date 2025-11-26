import json, os, shutil, msvcrt



class Archivist:
    def __init__(self, directory:str):
        """
        File and data actions for JSON and dictionary data. 

        Functions: reader, writer, confirm_action, backup, join_data
        """
        self.directory = directory
        # self.file = os.path.join(self.directory, filepath)

    def reader(self, file:str, join=False):
        """
        Read and return JSON file.

        file : directory of file as string.
        join : set True if **file** is a child directory of **self.directory** to join paths.
        """

        if join:
            file = os.path.join(self.directory, file)

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
            print("Any: No\nY:   Yes")
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
        meta_file = os.path.join(self.directory, "meta.json")
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
                backup_file = os.path.join(self.directory, datatype.lower() + f"_backup_{value}.json")
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
            return self.confirm_action("WARNING!\nBackup datalength is larger than that of current file.\nIf you have not removed data entries: abort and check data health.\nProceed anyway?")
        elif not backup_file:
            return True
        else:
            shutil.copy(file, backup_file)
            print("Data backup performed.")
            return True
        


    def join_data(self, file:str, new_data:dict, name:str, static=False):
        """
        Update library with new or edited data. Returns: bool

        file : directory of file as string.  
        new_data : data to be included in file.  
        name : id of new data entry.  
        static : for data validation check to mark files that are not expected to increase in length.
        """

        data = self.reader(file)

        if type(data) is dict: 
            original_length = len(data) 
        else: 
            original_length = 0
            data = dict()

        if name == "remove":
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
            update = False
            update = self.confirm_action("Object not added - already exists in library.\nAdd anyway?")
            data.update(new_data)
            if len(data) != original_length: 
                print("\nError occurred!\nLibrary update aborted.\n")
                return False
        else:
            data.update(new_data)


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

        Functions: request_input, listed_options, auto_options
        """

        self.quit_key = "q"
        self.separator = "-"*50
        self.indent = 3

    def request_input(self, options:list, enforced=False, return_string=False):
        """
        General function for recording input with checks against conditions. Returns: int or str

        options : list of conditions.
        enforced : set True to demand input for critical actions or preventing loss of data.
        return_string : set true to return keyboard input as string.
        """

        # Record keyboard input. Input not inlcuded among valid options will quit the script unless enforced, for critical options. 
        if not enforced: print(f"  {self.quit_key.upper()}: Quit")
        while True:
            if msvcrt.kbhit():
                try:
                    key = msvcrt.getch().decode("ASCII")
                except:
                    key = "none"
                    
                if key in options:
                    if return_string: return key
                    return int(key)
                elif not enforced and key.lower() == self.quit_key:
                    print("\nQuitting, good bye.\n")
                    quit()


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
            print(f"  {counter}: {alternative}")
            counter += 1

        string_selectors = [str(num) for num in range(1,len(options)+1)]

        selection = self.request_input(string_selectors)-1

        return options[selection]


    def auto_options(self, message:str, collection:dict[any, list]):
        """
        Cycles through keys and displays lists as selectable options, and pairs keys with corresponding selection. Returns: dict 

        message : explanatory text
        collection : dict of data to be reviewed
        """

        output = dict()
        print(message)
        for category in collection.keys():
            print(f"\n{self.separator}")
            selectable_options = dict()

            print(f"Select {category} among:")
            counter = 1
            for option in collection[category]:
                selectable_options[str(counter)] = option
                print(f"  {counter} {option}")
                counter += 1

            selection = self.request_input(selectable_options.keys(), return_string=True)
            print(type(selection))
            output[category.capitalize()] = selectable_options[selection]

        return output
