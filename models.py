from pydantic import BaseModel
from typing import List

class Subject(BaseModel):
    name: str
    teacher: str
    hours_todo: float
    hours_total: float
    unavailable_periods: List[int]

    def create_empty(self):
        return Subject(name="empty", teacher="", hours_todo=0.0, hours_total=0.0, unavailable_periods=[])

class Room(BaseModel):
    name: str
    capacity: int

class Params(BaseModel):
    class_name: str
    slots_per_day: int
    days_per_week: int
    max_hours_per_week: int

class PlanningData(BaseModel):
    params: Params
    subjects: List[Subject]
    rooms: List[Room]