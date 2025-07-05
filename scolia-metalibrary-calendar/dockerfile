# Étape 1: Compilation
FROM rust:latest as builder

WORKDIR /src

# Copie les fichiers de dépendances et les télécharge pour le cache
COPY Cargo.toml Cargo.lock ./
RUN cargo fetch

# Copie tout le code source et compile en mode release
COPY . .
RUN cargo build --release

# Étape 2: La commande qui sera exécutée
# Cette commande copie la librairie compilée dans un dossier qui sera notre volume partagé.
CMD ["cp", "target/release/librustlib.so", "/shared_libs/"]