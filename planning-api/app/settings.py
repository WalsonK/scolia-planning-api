import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """
    Classe de configuration qui charge les variables d'environnement.
    Utilise Pydantic pour la validation des types.
    """
    # --- Configuration de la base de données PostgreSQL ---
    POSTGRES_SERVER: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    DATABASE_URL: str

    class Config:
        # Spécifie le fichier .env à charger
        env_file = ".env"
        # Permet de ne pas être sensible à la casse pour les variables d'env
        case_sensitive = True


settings = Settings()