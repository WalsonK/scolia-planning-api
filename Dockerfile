# Utiliser une image de base avec Python et Rust (version récente pour édition 2024)
FROM rust:1.88 as rust-builder

# Installer Python dans l'image Rust
RUN apt-get update && apt-get install -y python3 python3-pip python3-venv

# Créer le répertoire de travail
WORKDIR /app

# Copier les fichiers Rust
COPY libs/rustlib ./libs/rustlib

# Compiler la bibliothèque Rust
WORKDIR /app/libs/rustlib
RUN cargo build --release

# Étape finale avec Python
FROM python:3.12-slim

# Installer les dépendances système nécessaires
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Créer le répertoire de travail
WORKDIR /app

# Copier les fichiers Python
COPY requirements.txt .
COPY main.py .
COPY basic_function.py .
COPY models.py .
COPY datas.json .
COPY libs/ ./libs/

# Copier la bibliothèque Rust compilée depuis l'étape précédente
COPY --from=rust-builder /app/libs/rustlib/target/release/ ./libs/

# Installer les dépendances Python
RUN pip install --no-cache-dir -r requirements.txt

# Exposer le port
EXPOSE 8000

# Commande par défaut
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
