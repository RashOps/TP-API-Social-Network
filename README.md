# Social Network API

[![Python](https://img.shields.io/badge/Python-3.12%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.163%2B-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Pydantic](https://img.shields.io/badge/Pydantic-2.x-E92063?logo=pydantic&logoColor=white)](https://docs.pydantic.dev/)
[![Beanie](https://img.shields.io/badge/Beanie-ODM-47A248?logo=mongodb&logoColor=white)](https://beanie-odm.dev/)
[![MongoDB](https://img.shields.io/badge/MongoDB-Database-47A248?logo=mongodb&logoColor=white)](https://www.mongodb.com/)
[![Uvicorn](https://img.shields.io/badge/Uvicorn-ASGI-499848)](https://www.uvicorn.org/)
[![uv](https://img.shields.io/badge/uv-Package%20manager-DE5FE9)](https://docs.astral.sh/uv/)

API REST de gestion d'un réseau social orienté événements, groupes et activités
communautaires.

## Fonctionnalités

- Utilisateurs : CRUD et email unique.
- Événements : CRUD, participants et organisateurs.
- Groupes : CRUD, membres et administrateurs.
- Fils de discussion, messages et commentaires.
- Albums photo liés aux événements.
- Sondages et votes.
- Billetteries pour les événements publics.
- Shopping lists liées aux événements.
- Offres de covoiturage activables par événement.
- Authentification JWT avec protection des routes métier.

## Prérequis

- Python 3.12 ou supérieur.
- MongoDB local ou MongoDB Atlas.
- [uv](https://docs.astral.sh/uv/) installé.

## Installation

Depuis la racine du projet :

```powershell
uv sync
```

Cette commande installe également la dépendance `PyJWT` utilisée pour signer
et vérifier les tokens.

## Configuration

Copiez `.env.example` vers `.env`, puis renseignez les informations MongoDB :

```powershell
Copy-Item .env.example .env
```

Exemple :

```env
MONGO_URI="mongodb://localhost:27017/"
MONGO_DB_NAME="social_network_event"
JWT_SECRET_KEY="replace-with-a-long-random-secret-at-least-32-characters"
JWT_ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES="30"
```

La configuration est chargée par [src/config.py](src/config.py). Ne commitez
jamais vos identifiants MongoDB.

## Lancer l'API

```powershell
uv run python -m server
```

L'API est disponible à l'adresse :

```text
http://127.0.0.1:8000
```

Documentation interactive :

- Swagger UI : http://127.0.0.1:8000/docs
- ReDoc : http://127.0.0.1:8000/redoc

## Authentification JWT

La création de compte et la connexion sont publiques :

```text
POST /api/v1/auth/register
POST /api/v1/auth/login
```

La connexion utilise le format OAuth2 formulaire :

```powershell
curl.exe -X POST http://127.0.0.1:8000/api/v1/auth/login `
  -H "Content-Type: application/x-www-form-urlencoded" `
  -d "username=alice@example.com&password=sample-password"
```

La réponse contient un token Bearer :

```json
{
  "access_token": "eyJ...",
  "token_type": "bearer"
}
```

Pour appeler une route protégée, transmettre le token dans l'en-tête :

```text
Authorization: Bearer <access_token>
```

Toutes les routes métier nécessitent un token JWT valide. Le secret
`JWT_SECRET_KEY` doit être long, aléatoire et différent en production.

Le serveur utilise le rechargement automatique en mode développement.

## Données d'exemple

Pour peupler la base avec des données de démonstration :

```powershell
uv run python -m data.samples
```

Le script est relançable et utilise des identifiants fixes pour remplacer les
données d'exemple existantes.

## Préfixe des routes

Toutes les routes sont préfixées par :

```text
/api/v1
```

Exemples :

```text
GET    /api/v1/users/
POST   /api/v1/events/
GET    /api/v1/groupes/
POST   /api/v1/discussions/
POST   /api/v1/albums/{album_id}/photos
POST   /api/v1/sondages/{sondage_id}/votes
POST   /api/v1/billetteries/{billetterie_id}/billets
POST   /api/v1/shopping-list/
POST   /api/v1/covoiturages/
```

## Structure du projet

```text
.
├── data/
│   └── samples.py
├── src/
│   ├── api/
│   │   └── api.py
│   ├── models/
│   ├── routes/
│   ├── config.py
│   └── utils/
│       └── db_client.py
└── server.py
```

## Sécurité

Les mots de passe doivent être hashés avant leur enregistrement en base. Les
valeurs présentes dans `data/samples.py` sont uniquement destinées aux tests.