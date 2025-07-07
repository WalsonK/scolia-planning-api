import json
from sqlalchemy.orm import Session
from models import Teacher

def load_data():
    """
    Load data from a JSON file.
    """
    with open('datas.json', 'r') as file:
        data = json.load(file)
    return data


def get_teachers(db: Session):
    """
    Get the list of teachers from the bdd.
    """
    data = db.query(Teacher).all()  # Assuming you want to fetch all teachers
    return data