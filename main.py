from typing import Union, List

from fastapi import FastAPI

from libs.rustml_wrapper import Rustml 
import basic_function as fn


app = FastAPI()
rustml = Rustml()

data = fn.load_data()

@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/info")
def read_info(category: str = None, name: str = None):
    """
    Endpoint to get information about the data.
    - category: Filter by category (e.g., 'teacher', 'class', 'subject').
    - name: Filter by specific name (e.g., teacher's name or subject name).
    """
    if category == "teacher":
        return {"teachers": [subject for subject in data["subjects"] if subject["teacher"] == name]} if name else {"teachers": [subject["teacher"] + " - " + subject["name"] for subject in data["subjects"]]}
    elif category == "class":
        return {"class": data["params"]}
    elif category == "subject":
        return {"subjects": [subject for subject in data["subjects"] if subject["name"] == name]} if name else {"subjects": data["subjects"]}
    elif category == "rooms":
        return {"rooms": [room for room in data["rooms"] if room["name"] == name]} if name else {"rooms": data["rooms"]}
    else:
        return {"error": "Invalid category. Use 'teacher', 'class', 'subject', or 'rooms'."}
    
@app.post("/edit")
def edit_info(category: str = None, operation: str = None, name: str = None):
    """
    Endpoint to edit information in the data.
    - category: The category to edit (e.g., 'subjects').
    - operation: The operation to perform (e.g., 'hours').
    - name: The name of the subject or teacher to edit.
    """
    if category == "subjects":
        if operation == "hours":
            if name:
                for subject in data["subjects"]:
                    if subject["name"] == name:
                        subject["hours_todo"] -= 1.5
            else:
                return {"error": "Name is required for 'hours' operation."}

@app.post("/unvailable")
def add_unvailable(name: str = None, slots: List[int] = []):
    """
    Endpoint to add unavailable periods for a subject or teacher.
    - name: The name of the subject or teacher to mark as unavailable.
    - slots: A list of time slots to mark as unavailable.
    """
    if name:
        for subject in data["subjects"]:
            if subject["name"] == name or subject["teacher"] == name:
                subject["unavailable_periods"].extend(slots)
    else:
        return {"error": "Name is required for 'unvailable' operation."}