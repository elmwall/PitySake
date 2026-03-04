class DataValidationError(Exception):
    pass

def validate_dataset(data):
    if len(data) < 10:
        raise ValueError("Dataset suspiciously small")