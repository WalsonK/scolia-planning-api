import json
from pathlib import Path
import pandas as pd
from typing import Dict, List, Tuple
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def load_data():
    """
    Load data from a JSON file.
    """
    current_file_dir = Path(__file__).parent
    data_file_path = current_file_dir / 'datas.json'

    with open(data_file_path, 'r') as file:
        data = json.load(file)
    return data

def process_curriculum_data(df: pd.DataFrame) -> Dict[str, Dict]:
    """
    Traite les données du curriculum pour calculer les totaux d'heures par enseignant.
    
    Args:
        df: DataFrame contenant les données du curriculum
        
    Returns:
        Dict contenant les informations par enseignant avec leurs matières et totaux d'heures
    """
    # Colonnes des volumes horaires
    vh_columns = [
        'VH présentation', 'VH distanciel', 'VH autonomie', 
        'VH e-learning', 'VH t-book', 'VH examens en partiel'
    ]
    
    # Calculer le total VH pour chaque ligne
    df['Total_VH'] = df[vh_columns].fillna(0).sum(axis=1)
    
    # Dictionnaire pour stocker les résultats par enseignant
    teachers_data = {}
    
    # Traiter chaque ligne du DataFrame
    for index, row in df.iterrows():
        # Récupérer les enseignants (peut y en avoir 2)
        teachers = []
        if pd.notna(row.get('Enseignant 1')):
            teachers.append(row['Enseignant 1'])
        if pd.notna(row.get('Enseignant 2')):
            teachers.append(row['Enseignant 2'])
        
        # Pour chaque enseignant, ajouter les informations
        for teacher in teachers:
            if teacher not in teachers_data:
                teachers_data[teacher] = {
                    'name': teacher,
                    'subjects': [],
                    'total_hours': 0.0,
                    'total_opcu': 0.0,
                    'total_etudiant': 0.0,
                    'total_pro': 0.0
                }
            
            # Ajouter la matière
            subject_info = {
                'intitule': row.get('Intitulé matière', ''),
                'numero_bloc': row.get('numero bloc', ''),
                'ect': row.get('ECT coef', 0),
                'vh_présentation': row.get('VH présentation', 0),
                'vh_distanciel': row.get('VH distanciel', 0),
                'vh_autonomie': row.get('VH autonomie', 0),
                'vh_elearning': row.get('VH e-learning', 0),
                'vh_tbook': row.get('VH t-book', 0),
                'vh_examens': row.get('VH examens en partiel', 0),
                'total_vh': row.get('Total_VH', 0),
                'total_opcu': row.get('Total OPCU', 0),
                'total_etudiant': row.get('Total etudiant', 0),
                'total_pro': row.get('Total pro (ffp)', 0),
                'consignes': row.get('Consignes planification', ''),
                'option_filiere': row.get('option/fillière', ''),
                'commentaires': row.get('commentaires', '')
            }
            
            teachers_data[teacher]['subjects'].append(subject_info)
            
            # Calculer les totaux (diviser par le nombre d'enseignants s'il y en a plusieurs)
            divisor = len(teachers)
            teachers_data[teacher]['total_hours'] += row.get('Total_VH', 0) / divisor
            teachers_data[teacher]['total_opcu'] += row.get('Total OPCU', 0) / divisor
            teachers_data[teacher]['total_etudiant'] += row.get('Total etudiant', 0) / divisor
            teachers_data[teacher]['total_pro'] += row.get('Total pro (ffp)', 0) / divisor
    
    return teachers_data

def generate_teacher_summary(teachers_data: Dict[str, Dict], niveau: str = "L3") -> Dict[str, str]:
    """
    Génère un résumé formaté pour chaque enseignant selon le template demandé.
    
    Args:
        teachers_data: Données des enseignants
        niveau: Niveau de la classe (ex: L3, M1, M2)
        
    Returns:
        Dict contenant les résumés formatés par enseignant
    """
    summaries = {}
    
    for teacher_name, teacher_info in teachers_data.items():
        # Construction de la liste des cours
        cours_details = []
        total_heures_cours = 0
        total_heures_exam = 0
        
        for subject in teacher_info['subjects']:
            heures_cours = subject['vh_présentation'] + subject['vh_distanciel'] + subject['vh_autonomie'] + subject['vh_elearning'] + subject['vh_tbook']
            heures_exam = subject['vh_examens']
            
            total_heures_cours += heures_cours
            total_heures_exam += heures_exam
            
            if heures_cours > 0 or heures_exam > 0:
                cours_details.append(f"- {heures_cours:.1f}h de cours {subject['intitule']}" + 
                                   (f" et {heures_exam:.1f}h d'examen" if heures_exam > 0 else ""))
        
        total_heures = total_heures_cours + total_heures_exam
        
        # Construction du message selon le template
        summary = f"""Hello {teacher_name},

Comment vas-tu ?

Je t'écris car on m'a demandé de planifier plusieurs cours avec des classes de {niveau}:

{chr(10).join(cours_details)}

Ces {total_heures:.1f}h avec les {niveau} sur les semaines ci-dessous : X 
Pourrais-tu me donner tes disponibilités ou indisponibilités sur ces semaines stp? Ainsi je pourrai croiser avec les autres réponses d'intervenants, et proposer à chacun un planning adapté.

Merci d'avance,
Bonne journée"""
        
        summaries[teacher_name] = summary
    
    return summaries

def send_email_to_teacher(teacher_email: str, teacher_name: str, summary: str, 
                         smtp_server: str = "smtp.gmail.com", smtp_port: int = 587,
                         sender_email: str = "", sender_password: str = "") -> bool:
    """
    Envoie un email à un enseignant avec son résumé d'heures selon le template personnalisé.
    
    Args:
        teacher_email: Email de l'enseignant
        teacher_name: Nom de l'enseignant
        summary: Résumé formaté selon le template
        smtp_server: Serveur SMTP
        smtp_port: Port SMTP
        sender_email: Email expéditeur
        sender_password: Mot de passe expéditeur
        
    Returns:
        True si l'email a été envoyé avec succès, False sinon
    """
    try:
        # Création du message
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = teacher_email
        msg['Subject'] = f"Planification des cours - Demande de disponibilités"
        
        # Corps du message (le summary contient déjà le template formaté)
        body = summary
        
        msg.attach(MIMEText(body, 'plain'))
        
        # Connexion au serveur SMTP
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(sender_email, sender_password)
        
        # Envoi du message
        text = msg.as_string()
        server.sendmail(sender_email, teacher_email, text)
        server.quit()
        
        return True
        
    except Exception as e:
        print(f"Erreur lors de l'envoi de l'email à {teacher_name}: {e}")
        return False