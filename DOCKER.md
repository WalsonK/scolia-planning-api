# Instructions Docker

Ce document explique comment utiliser Docker et Docker Compose pour lancer l'API de planning.

## Prérequis

- Docker installé sur votre machine
- Docker Compose installé

## Option 1: Utiliser Docker Compose (Recommandé)

### Lancement en production
```bash
docker-compose up --build
```

L'API sera accessible sur : http://localhost:8000

### Lancement en mode développement
```bash
docker-compose --profile dev up --build planning-api-dev
```

L'API sera accessible sur : http://localhost:8001 avec auto-reload

### Arrêter les services
```bash
docker-compose down
```

## Option 2: Utiliser Docker directement

### Construire l'image
```bash
docker build -t planning-api .
```

### Lancer le conteneur
```bash
docker run -p 8000:8000 planning-api
```

## Option 3: Script local (sans Docker)

Si vous préférez ne pas utiliser Docker, vous pouvez utiliser le script local :

```bash
./start.sh
```

Ce script va :
1. Compiler la bibliothèque Rust
2. Copier les fichiers binaires
3. Installer les dépendances Python
4. Lancer FastAPI

## Endpoints disponibles

Une fois l'API lancée, vous pouvez accéder à :

- **Documentation interactive** : http://localhost:8000/docs
- **API Root** : http://localhost:8000/
- **Informations** : http://localhost:8000/info

## Troubleshooting

### Problème de compilation Rust
Si la compilation Rust échoue, vérifiez que :
- Rust est bien installé dans le conteneur
- Les fichiers `Cargo.toml` sont présents dans `libs/rustlib/`

### Problème de bibliothèque
Si l'API ne trouve pas la bibliothèque Rust :
- Vérifiez que le fichier `.so`/`.dylib`/`.dll` est présent dans `libs/`
- Vérifiez les permissions du fichier

### Redémarrer complètement
```bash
docker-compose down --volumes --remove-orphans
docker-compose up --build --force-recreate
```
