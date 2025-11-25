import json, os, shutil, sys



class FileManager:
    def __init__(self, directory):
        self.directory = directory
        # self.file = os.path.join(self.directory, filepath)

    def reader(self, file, join=False):
        if join:
            file = os.path.join(self.directory, file)

        if os.path.exists(file):
            try:
                with open(file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                print(f"\nFile at {file} could not be read:\n{e}")
                # sys.exit()


    def backup(self, file, backup_frequency, datatype):
        try:
            file_length = len(self.reader(file))
        except:
            file_length = 0


        backup_file = False

        for value in backup_frequency:
            if file_length > 0 and file_length % value == 0:
                backup_file = os.path.join(self.directory, datatype.lower() + f"_backup_{value}.json")
                break

        if backup_file and os.path.exists(backup_file):
            backup_length = len(self.reader(backup_file))
        else:
            backup_length = 0


        if backup_length > file_length:
            raise RuntimeError(
                f"\nError! Backup file contains more data than current file."
                f"\n\nData file: {file}\nLength: {file_length}\n\nBackup file: {backup_file}\nLength: {backup_length}"
                f"\n\nData not updated. Check data health."
            )
        elif not backup_file:
            return True
        else:
            shutil.copy(file, backup_file)
            print("Data backup performed.")
            return True
        

    def join_data(self, file, new_data, name, static=False):

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
                return data
            except:
                return False
            

        if name in data.keys() and not static:
            print("\nObject not added - already exists in library. Add anyway?\n1 or any key: No\n2: Yes")
            selection = input("Enter selection: ")
            if selection == "2":
                data.update(new_data)
            else:
                print("Aborted.")
                return False
        else:
            data.update(new_data)


        if len(data) != original_length + 1 and selection != "2" and not static:
            print("\nError occurred!\n\nLibrary update aborted.")
            return False
        else:
            return data
            
    
    def edit_data():
        pass

        
    def writer(self, file, data):
        try:
            with open(file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print("Error occurred while attempting to write. Check file health and backups.")