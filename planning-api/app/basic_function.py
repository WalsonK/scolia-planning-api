import json
from pathlib import Path
from sqlalchemy.orm import Session
import models

def load_data():
    """
    Load data from a JSON file.
    """
    current_file_dir = Path(__file__).parent
    data_file_path = current_file_dir / 'datas.json'

    with open(data_file_path, 'r') as file:
        data = json.load(file)
    return data


def get_teachers(db: Session):
    """
    Get the list of teachers from the bdd.
    """
    data = db.query(models.Teacher).all()  # Assuming you want to fetch all teachers
    return data