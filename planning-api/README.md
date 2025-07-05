# planning-api

FASTAPI API pour la gestion de plannings scolaires.

## Description

Ce projet fournit une API basée sur FastAPI pour gérer et générer des plannings scolaires. Il utilise une bibliothèque Rust pour des calculs performants et des algorithmes heuristiques.

## Fonctionnalités

- Chargement et gestion des données de planning.
- Ajout de créneaux d'indisponibilité.
- Génération de plannings optimisés à l'aide d'algorithmes heuristiques.
- API REST pour interagir avec les données.

## Installation

1. Clonez le dépôt :
   ```bash
   git clone <URL_DU_DEPOT>
   cd planning-api
   ```

2. Installez les dépendances Python :
   ```bash
   pip install -r requirements.txt
   ```

3. Assurez-vous que Rust est installé sur votre machine. Si ce n'est pas le cas, installez-le via [rustup](https://rustup.rs/).

4. Compilez la bibliothèque Rust :
   ```bash
   cd libs/rustlib
   cargo build --release
   ```

## Utilisation

1. Lancez le serveur FastAPI :
   ```bash
   uvicorn main:app --reload
   ```

2. Accédez à la documentation interactive de l'API :
   - [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

3. Exemple d'utilisation :
   - Endpoint `/generate_planning` pour générer un planning optimisé.

## Tests

### Rust

Pour exécuter les tests Rust :
```bash
cd libs/rustlib
cargo test
```

### Python

Pour exécuter les tests Python (si disponibles) :
```bash
pytest
```

## Structure du projet

- **main.py** : Point d'entrée de l'API FastAPI.
- **libs/rustlib** : Bibliothèque Rust pour les calculs et algorithmes.
- **tester.py** : Script Python pour tester les fonctionnalités Rust.
- **models/** : Définitions des modèles de données.
- **libs/** : Contient les wrappers et fonctions utilitaires.

## Contributeurs

- **Walson** - Développeur principal.

## Licence

Ce projet est sous licence MIT. Consultez le fichier `LICENSE` pour plus d'informations.
