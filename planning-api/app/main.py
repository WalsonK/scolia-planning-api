from typing import Union, List

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware

import pandas as pd
from .libs.rustml_wrapper import Rustml 
from . import basic_function as fn
from .models import PlanningData, Subject
from io import BytesIO, StringIO
import os


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
def generate_greedy_planning(planning_data: PlanningData):
    """
    Endpoint to generate a greedy planning.
    - planning_data: JSON object containing :
    - - params = class_name, slots_per_day, days_per_week, max_hours_per_week
    - - List of subjects = name, teacher, hours_todo, hours_total, unavailable_periods
    - - List of rooms  = name, capacity
    """
    # Prepare data for Rust function
    subject_dict = {index: subject for index, subject in enumerate(planning_data.subjects)}
    subject_dict[-1] = Subject.create_empty(Subject)

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

@app.post("/send_curriculum")
async def send_curriculum(
    file: UploadFile = File(...), # Le fichier, comme avant [2]
    filiere: str = Form(...),    # Champ 'filiere' du formulaire [0, 4]
    niveau: str = Form(...),     # Champ 'niveau' du formulaire [0, 4]
    annee: str = Form(...),      # Champ 'annee' du formulaire [0, 4]
    dateFormat: str = Form(...), # Champ 'dateFormat' du formulaire [0, 4]
    separator: str = Form(...)   # Champ 'separator' du formulaire [0, 4]
    ):
    if not file.filename:
        raise HTTPException(status_code=400, detail="Aucun fichier n'a été envoyé.")
    
    file_extension = os.path.splitext(file.filename)[1].lower()

    try:
        contents = await file.read() # Lecture asynchrone du contenu du fichier [1]
        df = pd.DataFrame() # Initialiser df pour éviter ReferenceError en cas d'erreur
        message = ""

        if file_extension in [".xlsx", ".xls"]:
            # Process Excel file
            df = pd.read_excel(BytesIO(contents))
            print(f"Fichier Excel traité avec {len(df)} lignes")
            
            # Traitement des données
            teachers_data = fn.process_curriculum_data(df)
            
            # Génération des résumés pour chaque enseignant
            teacher_summaries = fn.generate_teacher_summary(teachers_data, niveau)
            print(teacher_summaries)
            
            """# Préparation des données pour l'envoi d'emails
            email_results = []
            for teacher_name, summary in teacher_summaries.items():
                # Pour le moment, on stocke les résumés sans envoyer d'emails
                # L'envoi d'email nécessiterait une configuration SMTP
                email_results.append({
                    "teacher": teacher_name,
                    "total_hours": teachers_data[teacher_name]['total_hours'],
                    "subjects_count": len(teachers_data[teacher_name]['subjects']),
                    "summary": summary
                })"""
            
            message = f"La maquette a été importée avec succès! {len(teachers_data)} enseignants identifiés."
            
            return {"message": message}
        
        """elif file_extension == ".csv":
            # Process CSV file
            df = pd.read_csv(StringIO(contents.decode('utf-8')), separator=separator)
            print(f"Fichier CSV traité avec {len(df)} lignes")
            
            # Traitement des données (même logique que pour Excel)
            teachers_data = fn.process_curriculum_data(df)
            teacher_summaries = fn.generate_teacher_summary(teachers_data)
            
            email_results = []
            for teacher_name, summary in teacher_summaries.items():
                email_results.append({
                    "teacher": teacher_name,
                    "total_hours": teachers_data[teacher_name]['total_hours'],
                    "subjects_count": len(teachers_data[teacher_name]['subjects']),
                    "summary": summary
                })
            
            message = f"Curriculum CSV traité avec succès. {len(teachers_data)} enseignants identifiés."
            
            return {
                "message": message,
                "filiere": filiere,
                "niveau": niveau,
                "annee": annee,
                "teachers_count": len(teachers_data),
                "teachers_data": teachers_data,
                "email_summaries": email_results
            }
        
        else:
            raise HTTPException(status_code=400, detail="Format de fichier non supporté. Utilisez .xlsx, .xls ou .csv")
        """
    except Exception as e:
        print(f"Erreur lors du traitement du fichier: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur lors du traitement du fichier: {str(e)}")
    
@app.post("/send_teacher_emails")
async def send_teacher_emails(
    teacher_emails: dict = Form(...),  # Dict mapping teacher names to email addresses
    smtp_server: str = Form("smtp.gmail.com"),
    smtp_port: int = Form(587),
    sender_email: str = Form(...),
    sender_password: str = Form(...),
    teachers_data: dict = Form(...)  # Les données des enseignants depuis send_curriculum
):
    """
    Envoie des emails aux enseignants avec leurs résumés d'heures.
    
    Args:
        teacher_emails: Dictionnaire associant nom d'enseignant à email
        smtp_server: Serveur SMTP
        smtp_port: Port SMTP
        sender_email: Email expéditeur
        sender_password: Mot de passe expéditeur
        teachers_data: Données des enseignants
    """
    try:
        # Génération des résumés
        teacher_summaries = fn.generate_teacher_summary(teachers_data)
        
        # Envoi des emails
        email_results = []
        for teacher_name, summary in teacher_summaries.items():
            if teacher_name in teacher_emails:
                success = fn.send_email_to_teacher(
                    teacher_emails[teacher_name],
                    teacher_name,
                    summary,
                    smtp_server,
                    smtp_port,
                    sender_email,
                    sender_password
                )
                email_results.append({
                    "teacher": teacher_name,
                    "email": teacher_emails[teacher_name],
                    "sent": success
                })
            else:
                email_results.append({
                    "teacher": teacher_name,
                    "email": "Non fourni",
                    "sent": False,
                    "error": "Email non fourni"
                })
        
        sent_count = sum(1 for result in email_results if result["sent"])
        
        return {
            "message": f"Emails envoyés à {sent_count}/{len(email_results)} enseignants",
            "results": email_results
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de l'envoi des emails: {str(e)}")

@app.get("/teacher_summary/{teacher_name}")
def get_teacher_summary(teacher_name: str):
    """
    Récupère le résumé d'un enseignant spécifique.
    Note: Cette route nécessite que les données aient été préalablement traitées.
    """
    # Cette route pourrait être améliorée en stockant les données dans une base de données
    return {"message": "Fonctionnalité à implémenter avec stockage des données"}