import os

from settings.config import PATHWAYS


class Doctor:
    def __init__(self):
        pass

    def file_health_check(self):
        files = [file for file in PATHWAYS.values() if ".json" in file]
        file_checkup = dict()
        for file in files:
            file = os.path.join(PATHWAYS["DataFolder"], file)
            file_checkup[file] = os.path.exists(file)

        for x, y in file_checkup.items():
            print(f"{x:30}{y}")


    def restore_from_backup():
        pass


class Validator:
    def __init__(self):
        pass

    def validate_dataset(data):
        if len(data) < 10:
            raise ValueError("Dataset suspiciously small")


class Errorer:
    def __init__(self):
        pass



class Debugger:
    def __init__(self):
        pass

    def checkpoint(value, stop=True):
        print()
        print("Testvalue:")
        print(value)
        if stop: quit()