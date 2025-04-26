import json

def load_data():
    """
    Load data from a JSON file.
    """
    with open('datas.json', 'r') as file:
        data = json.load(file)
    return data