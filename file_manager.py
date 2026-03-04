import os
import shutil

import json
import msvcrt


class Archivist:
    def __init__(self, PATHWAYS:dict, file):
        """
        File and data actions for JSON and dictionary data. 
        Functions: reader, writer, confirm_action, backup, join_data

        file : directory of file as string
        PATHWAYS: dictionary with folder and file references
        """
        self.file = file
        self.data_directory = PATHWAYS["DataFolder"]
        self.settings_directory = PATHWAYS["SettingsFolder"]
        self.backup_directory = PATHWAYS["BackupFolder"]
        self.backup_meta = PATHWAYS["BackupMetaFile"]


    def reader(self, other_file=False, join="none"):
        """
        Read and return JSON file.

        join : set to string "data" or "settings", if *file* is located within *self.data_directory* or *self.settings_directory*.
        """

        read_file = self.file if not other_file else other_file

        if join == "data":
            read_file = os.path.join(self.data_directory, read_file)
        elif join == "settings":
            read_file = os.path.join(self.settings_directory, read_file)
        elif join != "none":
            print("Invalid value of pathway indicator 'join'.")

        try:
            with open(read_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"{read_file} not found.")
        except json.JSONDecodeError:
            raise json.JSONDecodeError(f"{read_file} could not be decoded as JSON.")
        except Exception as e:
            print(f"\nFile at {read_file} could not be read:\n{e}")
            raise


    def backup(self, negotiator, backup_frequency:list[int], datatype:str):
        """
        Automated backup in multiple files.  
        Returns: bool

        backup_frequency : list length sets the number of backup files; integers specifies number of edits between every backup.
        datatype : sets name prefix to specify identify of backup data.
        """
        
        # Call file containing edit count info for all files
        meta_file = os.path.join(self.settings_directory, self.backup_meta)
        try:
            edit_meta = self.reader(meta_file)
        except:
            edit_meta = dict()

        try:    
            file_edit_count = edit_meta[self.file]
        except:
            file_edit_count = 0   
        backup_file = False
        
        # Check backup frequencies and set backup file path if any frequency condition is met and update edit meta
        for value in backup_frequency:
            if file_edit_count > 0 and file_edit_count % value == 0:
                print(f"Performing backup for every {value} saves.")
                backup_file = os.path.join(
                    self.backup_directory, 
                    datatype.lower() + f"_backup_{value}.json")
                break
        edit_meta[self.file] = file_edit_count + 1
        self.writer(edit_meta, other_file=meta_file)       
        try:
            file_length = len(self.reader(self.file))
        except:
            file_length = 0

        if backup_file and os.path.exists(backup_file):
            backup_length = len(self.reader(backup_file))
        else:
            backup_length = 0

        # Compare contents of backup and current data
        if backup_length > file_length+2:
            confirm_backup = negotiator.confirm_action("\nWARNING!\nBackup datalength is larger than that of current file.\nIf you have not removed data entries: abort and check data health.\nBackup anyway?\n")
        else:
            confirm_backup = True

        if not backup_file:
            return True
        elif confirm_backup:
            shutil.copy(self.file, backup_file)
            print("Data backup done.")
            return True
        else:
            return False
        

    def join_data(self, new_data:dict, name:str, sort=True, update=False, static=False):
        """
        Update library with new or edited data.  
        Returns: bool

        new_data : data to be included in file.  
        name : id of new data entry.  
        static : marks files that are not expected to increase in length.
        """

        data = self.reader(self.file)
        if type(data) is dict: 
            original_length = len(data) 
        else: 
            original_length = 0
            data = dict()

        if name == "Remove":
            print("\nRemoval requested. Enter name of item to remove.")
            name = input("Name: ").title()
            
            try:
                data.pop(name)
            except KeyError:
                raise KeyError(f"{name} not in data.\nArchivist.join_data: Did you spell correct? Have you removed {name} already?")
            
            if len(data) != original_length-1: 
                print("\nError 1: Expected data length decrease.\nLibrary update aborted.\n")
                return False

            return data

        # Add existing data to library
        if name in data.keys() and not static:
            data.update(new_data)
            if len(data) != original_length and not update: 
                print("\nError 2: Unexpected altered data length.\nLibrary update aborted.\n")
                return False
        else:
            data.update(new_data)
        if sort: data = dict(sorted(data.items()))
        
        # Checking data validity depending on action. 
        if len(data) != original_length+1 and not update and not static:
            print("\nError 3: Expected data length increase.\nLibrary update aborted.")
            return False
        else:
            return data
        

    def writer(self, data, other_file=False):
        """
        Write JSON to file. Returns: bool
        """

        save_file = self.file if not other_file else other_file
        try:
            with open(save_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
                return True
        except json.JSONDecodeError:
            raise json.JSONDecodeError(f"Could not decode data to save in {save_file}.")
        except Exception as e:
            print(f"{e}\nError 4: occurred while attempting to write to {save_file}. Check file health and backups.")
            raise


    def save_report(self, data, report_name:str):
        """
        Write report as markdown

        data: information as string formatted for markdown
        report_name: string for file name without extension
        """
        file = os.path.join(self.data_directory, report_name+".md")
        try:
            with open(file, "w", encoding="utf-8") as f:
                f.write(data)
                return True
        except Exception as e:
            print(f"{e}\nError 5: occurred while attempting to write report {report_name} to {file}.")
            raise


