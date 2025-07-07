from typing import Union, List

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from libs.rustml_wrapper import Rustml
from db.session import *
import basic_function as fn, models


app = FastAPI()
rustml = Rustml()

data = fn.load_data()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)

@app.get("/")
def read_root():
    return {"Hello": "Hello World"}

@app.get("/teachers")
def get_teachers(db: Session = Depends(get_db)):
    datas = fn.get_teachers(db)
    return {
        "teachers": [
            {
                "first_name": teacher.first_name,
                "last_name": teacher.last_name,
                "email": teacher.email
            }
            for teacher in datas
        ],
        "data": datas
    }

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


@app.post("/generate_planning")
def generate_greedy_planning(planning_data: models.PlanningData):
    """
    Endpoint to generate a greedy planning.
    - planning_data: JSON object containing :
    - - params = class_name, slots_per_day, days_per_week, max_hours_per_week
    - - List of subjects = name, teacher, hours_todo, hours_total, unavailable_periods
    - - List of rooms  = name, capacity
    """
    # Prepare data for Rust function
    subject_dict = {index: subject for index, subject in enumerate(planning_data.subjects)}
    subject_dict[-1] = models.Subject.create_empty(models.Subject)

    total_slots = planning_data.params.slots_per_day * planning_data.params.days_per_week
    max_hours = planning_data.params.max_hours_per_week
    slot_minutes = 90
    subjects = list(subject_dict.keys())
    todo = [subject.hours_todo for subject in planning_data.subjects]
    unavailability = [subject.unavailable_periods for subject in planning_data.subjects]

    # Generate planning using Rust function
    resultat = rustml.generate_greedy_planning(
        total_slots=total_slots,
        max_hours=max_hours,
        slot_minutes=slot_minutes,
        subjects=subjects,
        todo=todo,
        unavailability=unavailability
    )

    # Pretify the result
    resultat = [subject_dict[i].name for i in resultat]
    resultat = [resultat[i:i + planning_data.params.slots_per_day] for i in range(0, len(resultat), planning_data.params.slots_per_day)]

    return {
        "message": "Planning generated successfully",
        "planning": resultat,
    }

@app.get("/get_planning/{week_number}/{class_name}")
def get_planning(week_number: int, class_name: str):
    """
    Endpoint to get the current planning.
    """
    # Here you would typically retrieve the planning from a database or a file.
    # For this example, we will return a static response.
    return {
        "message": f"Planning for week {week_number} and class {class_name} retrieved successfully",
        "planning": [
            ['Mathématiques', 'Physique', 'empty', 'Mathématiques', 'Chimie', 'empty'],
            ['Physique', 'Mathématiques', 'Chimie', 'empty', 'Physique', 'Mathématiques'],
            ['Chimie', 'empty', 'Mathématiques', 'Physique', 'empty', 'Chimie'],
            ['empty', 'Chimie', 'Physique', 'empty', 'Mathématiques', 'Physique'],
            ['Mathématiques', 'empty', 'empty', 'Chimie', 'Physique', 'empty'],
            ['empty', 'Physique', 'Mathématiques', 'empty', 'empty', 'Chimie']
        ]
    }
