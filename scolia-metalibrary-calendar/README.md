# Rustlib - Bibliothèque Rust avec Docker

## Description
Ce projet contient une bibliothèque Rust appelée `rustlib`, qui est construite et déployée à l'aide de Docker. Le projet utilise un fichier `docker-compose.yml` pour simplifier la gestion des conteneurs et le partage de la bibliothèque compilée.

## Structure du projet
```
/Users/walson/Documents/Cours/5A/PA/scolia-metalibrary-calendar/
├── Cargo.toml          # Configuration du projet Rust
├── dockerfile          # Instructions pour construire l'image Docker
├── docker-compose.yml  # Configuration Docker Compose
├── shared/             # Dossier partagé pour la bibliothèque compilée
├── src/                # Code source de la bibliothèque Rust
│   └── lib.rs          # Point d'entrée de la bibliothèque
```

## Prérequis
- [Docker](https://www.docker.com/) installé sur votre machine.
- [Docker Compose](https://docs.docker.com/compose/) installé.

## Instructions

### 1. Construire et démarrer le conteneur
Pour construire l'image Docker et démarrer le conteneur, exécutez :
```bash
docker-compose up --build
```
Cela :
- Reconstruit l'image Docker si nécessaire.
- Démarre le conteneur `rustlib_builder`.

### 2. Arrêter le conteneur
Pour arrêter et supprimer le conteneur, exécutez :
```bash
docker-compose down
```

### 3. Accéder à la bibliothèque compilée
La bibliothèque compilée (`librustlib.so`) sera disponible dans le dossier local `shared/`.

### 4. Vérifier les conteneurs en cours d'exécution
Pour voir les conteneurs actifs, utilisez :
```bash
docker ps
```

## Développement
Si vous modifiez le code source de la bibliothèque, utilisez la commande suivante pour reconstruire et redémarrer le conteneur :
```bash
docker-compose up --build
```

## Fichiers importants
- **`dockerfile`** : Définit les étapes pour construire l'image Docker.
- **`docker-compose.yml`** : Configure le service Docker Compose.
- **`shared/`** : Contient la bibliothèque compilée accessible depuis l'hôte.

## Auteurs
- **Walson**

## Licence
Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.
