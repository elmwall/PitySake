import os
import shutil

import json


class Archivist:
    def __init__(self, DIRECTORIES, DATAPATH, file):
        """
        File and data actions for JSON and dictionary data. 
        Functions: reader, writer, backup, join_data

        file : directory of file as string
        """
        self.file = file
        self.data_directory = DIRECTORIES["DataFolder"]
        self.settings_directory = DIRECTORIES["SettingsFolder"]
        self.backup_directory = DIRECTORIES["BackupFolder"]
        self.backup_meta = DATAPATH["BackupMetaFile"]


    def reader(self, other_file=False, join_path="none", is_json=True, allow_missing=False, allow_empty=False):
        """
        Read and return JSON file.

        join_path : set to string "data" or "settings", if *file* is located within *self.data_directory* or *self.settings_directory*.
        """
        
        read_file = self.file if not other_file else other_file

        if join_path == "data":
            read_file = os.path.join(self.data_directory, read_file)
        elif join_path == "settings":
            read_file = os.path.join(self.settings_directory, read_file)
        elif join_path != "none":
            print("Invalid value of pathway indicator 'join_path'.")

        if is_json:
            try:
                with open(read_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except FileNotFoundError:
                if allow_missing:
                    return None
                raise FileNotFoundError(f"{read_file} not found.")
            except json.JSONDecodeError:
                if allow_empty:
                    return None
                raise json.JSONDecodeError(f"{read_file} could not be decoded as JSON.")
            except Exception as e:
                print(f"\nFile at {read_file} could not be read:\n{e}")
                raise
        else:
            try:
                with open(read_file, "r", encoding="utf-8") as f:
                    return f.read()
            except FileNotFoundError:
                if allow_missing:
                    return None
            except Exception as e:
                print(f"\nFile at {read_file} could not be read:\n{e}")
                raise


    def backup(self, negotiator, backup_frequency:list[int], object_type:str, other_file=False):
        """
        Automated backup in multiple files.  
        Returns: bool

        backup_frequency : list of integers largest-to-smallest; list length sets the number of backup files; integers specifies number of edits between every backup.
        object_type : sets name prefix to specify identify of backup data.
        """

        if not other_file:
            file = self.file 
        else:
            file = os.path.join(self.data_directory, other_file)

        # Call file containing edit count info for all files
        meta_file = os.path.join(self.data_directory, self.backup_meta)
        edit_meta = self.reader(meta_file)
        if file in edit_meta.keys():
            file_edit_count = edit_meta[file]
        else:
            file_edit_count = 0 
        backup_file = False
        
        # Check backup frequencies and set backup file path if any frequency condition is met and update edit meta
        for value in backup_frequency:
            if file_edit_count > 0 and file_edit_count % value == 0:
                print(f"Performing backup for every {value} saves.")
                backup_file = os.path.join(
                    self.backup_directory, 
                    object_type.lower() + f"_backup_{value}.json")
                break
        edit_meta[file] = file_edit_count + 1
        self.writer(edit_meta, other_file=meta_file)     
        
        data = self.reader(file, allow_missing=True, allow_empty=True)
        if data:
            file_length = len(data)
        else:
            if negotiator.confirm_action(f"{file} subject for backup does not return previous data. Do you wish to proceed?"):
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
            shutil.copy(file, backup_file)
            print("Data backup done.")
            return True
        else:
            return False
        

    def join_data(self, new_data:dict, name:str, for_deletion, for_renaming, need_sorting=True, is_static=False):
        """
        Update library with new or edited data.  
        Returns: bool

        new_data : data to be included in file.  
        name : id of new data entry.  
        is_static : marks files that are not expected to increase in length.
        """


        data = self.reader(self.file)
        if type(data) is dict: 
            original_length = len(data) 
        else: 
            original_length = 0
            data = dict()

        if for_renaming:
            new_data = dict()
            try:
                new_data[for_renaming] = data[name]
                is_static = for_deletion = True
            except:
                raise KeyError(f"Key '{name}' is absent from data. Check spelling and database content.")

        if for_deletion:          
            try:
                data.pop(name)
            except KeyError:
                raise KeyError(f"Key '{name}' is absent from data. Check spelling and database content.")
            except TypeError:
                raise TypeError(f"Unable to remove {name}. Check format.")
            
            if len(data) != original_length-1: 
                raise ValueError(f"Expected a data length decrease after removing {name}.")
            
            if not for_renaming:
                return data, f"{name} was removed"
            else:
                name = for_renaming

        # Add existing data to library
        if name in data.keys() and not is_static:
            data.update(new_data)
            action_verification = f"{name} was updated"
            if len(data) != original_length and is_static: 
                raise ValueError(f"Data length was altered unexpectedly. Library update aborted.")
        else:
            try:
                data.update(new_data)
            except ValueError:
                raise ValueError(f"Unable to update")
            action_verification = f"{name} was added"
        if need_sorting: data = dict(sorted(data.items()))
        is_static

        # Checking data validity depending on previous action. 
        if name not in data.keys():
            raise KeyError(f"Key '{name}' is absent from data. Check database content.")
        elif len(data) != original_length+1 and not is_static:
            raise ValueError(f"Expected data length increase. Library update aborted.")
        else:
            return data, action_verification
        

    def writer(self, data, other_file=False, join_path="none"):
        """
        Write JSON to file. Returns: bool
        """

        save_file = self.file if not other_file else other_file

        if join_path == "data":
            save_file = os.path.join(self.data_directory, other_file)
        elif join_path == "settings":
            save_file = os.path.join(self.settings_directory, other_file)
        elif join_path != "none":
            print(f"Invalid value of pathway switch 'join_path': {join_path}")

        try:
            with open(save_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
                return True
        except json.JSONDecodeError:
            raise json.JSONDecodeError(f"Could not decode data to save in {save_file}.")
        except Exception as e:
            raise RuntimeError(f"Error from {e} occurred while attempting to write to {save_file}. Check file health and backups.")


    def save_report(self, data, report_name:str, format:str):
        """
        Write report as csv

        data: information as string formatted as csv table
        report_name: string for file name without extension
        format: define file type
        """

        file = os.path.join(self.data_directory, report_name+format)
        try:
            with open(file, "w", encoding="utf-8") as f:
                f.write(data)
                return True
        except Exception as e:
            raise RuntimeError(f"Error from {e} occurredwhile attempting to write report {report_name} to {file}.")


