# Social Network API

[![Python](https://img.shields.io/badge/Python-3.12%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.163%2B-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Pydantic](https://img.shields.io/badge/Pydantic-2.x-E92063?logo=pydantic&logoColor=white)](https://docs.pydantic.dev/)
[![Beanie](https://img.shields.io/badge/Beanie-ODM-47A248?logo=mongodb&logoColor=white)](https://beanie-odm.dev/)
[![MongoDB](https://img.shields.io/badge/MongoDB-Database-47A248?logo=mongodb&logoColor=white)](https://www.mongodb.com/)
[![Uvicorn](https://img.shields.io/badge/Uvicorn-ASGI-499848)](https://www.uvicorn.org/)
[![uv](https://img.shields.io/badge/uv-Package%20manager-DE5FE9)](https://docs.astral.sh/uv/)

API REST de gestion d'un réseau social orienté événements, groupes et activités
communautaires. L'application permet aux utilisateurs de créer et de gérer
des événements, de rejoindre des groupes et d'échanger autour des activités
proposées.

L'API est construite avec FastAPI, utilise MongoDB pour la persistance des
données et expose une documentation OpenAPI interactive. Les ressources sont
organisées autour d'un préfixe commun `/api/v1` et les routes métier sont
protégées par authentification JWT.

Lien Postman : [Lien_postman](https://documenter.getpostman.com/view/59275013/2sBYHbrbgB)

## Fonctionnalités

- **Utilisateurs** : création, consultation, modification et suppression des
  comptes. L'adresse email est validée et doit être unique.
- **Événements** : gestion du nom, de la description, des dates, du lieu, de
  la visibilité, de la photo de couverture, des organisateurs et des
  participants.
- **Groupes** : création de groupes publics, privés ou secrets avec membres,
  administrateurs et permissions de publication ou de création d'événements.
- **Fils de discussion** : un fil peut être rattaché à un groupe ou à un
  événement, mais jamais aux deux. Il contient des messages et des
  commentaires.
- **Albums photo** : un album est associé à un événement et peut contenir des
  photos publiées par les participants, ainsi que leurs commentaires.
- **Sondages** : création de questions et de choix multiples. Un participant
  ne peut sélectionner qu'une réponse par question.
- **Billetteries** : création de plusieurs types de billets pour un événement
  public, avec montant, stock limité et achat unique par personne.
- **Shopping lists** : activation par événement et déclaration d'éléments à
  apporter avec quantité et heure d'arrivée. Un élément est unique par
  événement.
- **Covoiturage** : publication d'offres de trajet lorsque l'option est
  activée, avec départ, horaire, prix, places et écart maximal accepté.
- **Authentification JWT** : inscription, connexion OAuth2 et protection des
  routes métier avec des tokens Bearer.

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

La configuration est chargée par [src/config.py](src/config.py). Les variables
JWT permettent de contrôler la signature et la durée de validité des tokens.
Ne commitez jamais vos identifiants MongoDB ni votre clé JWT.

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

La création de compte et la connexion sont les seules routes publiques :

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

Toutes les autres routes nécessitent un token JWT valide. Le secret
`JWT_SECRET_KEY` doit être long, aléatoire et différent en production. Les
mots de passe sont hashés avec `scrypt` avant leur stockage.

Le serveur utilise le rechargement automatique en mode développement.

## Données d'exemple

Pour peupler la base avec des données de démonstration :

```powershell
uv run python -m data.samples
```

Le script est relançable et utilise des identifiants fixes pour remplacer les
données d'exemple existantes.

## Ressources et routes principales

Toutes les routes sont préfixées par :

```text
/api/v1
```

Les routes de lecture, modification et suppression utilisent l'identifiant
MongoDB de la ressource concernée. Les routes de création renvoient
généralement le statut `201`, les suppressions réussies renvoient `204` et les
ressources inexistantes renvoient `404`.

Exemples de routes :

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

Les routes détaillées et leurs paramètres sont disponibles dans Swagger.

## Description détaillée des routes

### Authentification

| Méthode | Route | Description |
|---|---|---|
| `POST` | `/api/v1/auth/register` | Crée un compte utilisateur. Le mot de passe est hashé avant son enregistrement et l'email doit être unique. |
| `POST` | `/api/v1/auth/login` | Vérifie les identifiants envoyés au format OAuth2 formulaire et retourne un token JWT Bearer. |

### Utilisateurs

| Méthode | Route | Description |
|---|---|---|
| `GET` | `/api/v1/users/` | Retourne la liste des utilisateurs sans exposer leur mot de passe. |
| `GET` | `/api/v1/users/{user_id}` | Retourne un utilisateur précis à partir de son identifiant MongoDB. |
| `POST` | `/api/v1/users/` | Crée un utilisateur authentifié et refuse les emails déjà utilisés. |
| `PATCH` | `/api/v1/users/{user_id}` | Modifie partiellement les informations d'un utilisateur existant. |
| `DELETE` | `/api/v1/users/{user_id}` | Supprime définitivement un utilisateur et retourne `204` en cas de succès. |

### Événements

| Méthode | Route | Description |
|---|---|---|
| `GET` | `/api/v1/events/` | Retourne les événements avec leurs dates, leur visibilité, leurs organisateurs et leurs participants. |
| `GET` | `/api/v1/events/{event_id}` | Retourne le détail d'un événement identifié par son ObjectId MongoDB. |
| `POST` | `/api/v1/events/` | Crée un événement avec au moins un organisateur. La shopping list et le covoiturage sont désactivés par défaut. |
| `PATCH` | `/api/v1/events/{event_id}` | Met à jour partiellement les informations et les options d'un événement. |
| `DELETE` | `/api/v1/events/{event_id}` | Supprime définitivement l'événement demandé. |

### Groupes

| Méthode | Route | Description |
|---|---|---|
| `GET` | `/api/v1/groupes/` | Retourne les groupes avec leurs règles, leurs membres et leurs administrateurs. |
| `GET` | `/api/v1/groupes/{groupe_id}` | Retourne le détail d'un groupe précis. |
| `POST` | `/api/v1/groupes/` | Crée un groupe public, privé ou secret avec au moins un membre et un administrateur. |
| `PATCH` | `/api/v1/groupes/{groupe_id}` | Modifie les informations, permissions, membres ou administrateurs d'un groupe. |
| `DELETE` | `/api/v1/groupes/{groupe_id}` | Supprime définitivement un groupe. |

### Fils de discussion

| Méthode | Route | Description |
|---|---|---|
| `GET` | `/api/v1/discussions/` | Retourne tous les fils, leurs messages et leurs commentaires. |
| `GET` | `/api/v1/discussions/{discussion_id}` | Retourne un fil complet à partir de son identifiant. |
| `POST` | `/api/v1/discussions/` | Crée un fil lié à un groupe ou à un événement, mais jamais aux deux. |
| `PATCH` | `/api/v1/discussions/{discussion_id}` | Met à jour la liste des messages d'un fil existant. |
| `DELETE` | `/api/v1/discussions/{discussion_id}` | Supprime un fil ainsi que les messages et commentaires intégrés. |
| `POST` | `/api/v1/discussions/{discussion_id}/messages` | Ajoute un message avec son auteur dans un fil existant. |
| `POST` | `/api/v1/discussions/{discussion_id}/messages/{message_id}/commentaires` | Ajoute un commentaire au message indiqué. |

### Albums photo

| Méthode | Route | Description |
|---|---|---|
| `GET` | `/api/v1/albums/` | Retourne les albums avec leur événement, leurs photos et leurs commentaires. |
| `GET` | `/api/v1/albums/{album_id}` | Retourne le contenu complet d'un album précis. |
| `POST` | `/api/v1/albums/` | Crée un album vide associé à un événement. |
| `PATCH` | `/api/v1/albums/{album_id}` | Modifie les informations autorisées d'un album existant. |
| `DELETE` | `/api/v1/albums/{album_id}` | Supprime un album, ses photos et ses commentaires. |
| `POST` | `/api/v1/albums/{album_id}/photos` | Ajoute une photo publiée par un participant dans un album. |
| `POST` | `/api/v1/albums/{album_id}/photos/{photo_id}/commentaires` | Ajoute un commentaire sur une photo existante. |

### Sondages

| Méthode | Route | Description |
|---|---|---|
| `GET` | `/api/v1/sondages/` | Retourne les sondages, leurs questions, leurs choix et leurs votes. |
| `GET` | `/api/v1/sondages/{sondage_id}` | Retourne le détail d'un sondage précis. |
| `POST` | `/api/v1/sondages/` | Crée un sondage avec au moins une question et deux choix par question. |
| `PATCH` | `/api/v1/sondages/{sondage_id}` | Remplace les questions d'un sondage existant. |
| `DELETE` | `/api/v1/sondages/{sondage_id}` | Supprime un sondage et les votes associés. |
| `POST` | `/api/v1/sondages/{sondage_id}/votes` | Enregistre une réponse ; un participant ne peut répondre qu'une fois par question. |

### Billetteries

| Méthode | Route | Description |
|---|---|---|
| `GET` | `/api/v1/billetteries/` | Retourne les billetteries, leurs types et les billets attribués. |
| `GET` | `/api/v1/billetteries/{billetterie_id}` | Retourne le détail d'une billetterie. |
| `POST` | `/api/v1/billetteries/` | Crée une billetterie pour un événement public avec au moins un organisateur autorisé. |
| `PATCH` | `/api/v1/billetteries/{billetterie_id}` | Modifie les types de billets proposés. |
| `DELETE` | `/api/v1/billetteries/{billetterie_id}` | Supprime une billetterie et les billets associés. |
| `POST` | `/api/v1/billetteries/{billetterie_id}/billets` | Attribue un billet disponible à une personne ; une personne ne peut en obtenir qu'un seul par billetterie. |

### Shopping lists

| Méthode | Route | Description |
|---|---|---|
| `GET` | `/api/v1/shopping-list/` | Retourne toutes les contributions déclarées pour les événements. |
| `GET` | `/api/v1/shopping-list/{item_id}` | Retourne une contribution précise avec son utilisateur et son événement. |
| `POST` | `/api/v1/shopping-list/` | Ajoute un élément si la shopping list est activée et si son nom est unique dans l'événement. |
| `PATCH` | `/api/v1/shopping-list/{item_id}` | Modifie le nom, la quantité ou l'heure d'arrivée sans créer de doublon. |
| `DELETE` | `/api/v1/shopping-list/{item_id}` | Supprime une contribution de la shopping list. |

### Covoiturages

| Méthode | Route | Description |
|---|---|---|
| `GET` | `/api/v1/covoiturages/` | Retourne les offres avec leur conducteur, départ, prix, places et écart maximal. |
| `GET` | `/api/v1/covoiturages/{covoiturage_id}` | Retourne le détail d'une offre de covoiturage. |
| `POST` | `/api/v1/covoiturages/` | Crée une offre uniquement si le covoiturage est activé pour l'événement. |
| `PATCH` | `/api/v1/covoiturages/{covoiturage_id}` | Modifie partiellement une offre et revalide ses contraintes. |
| `DELETE` | `/api/v1/covoiturages/{covoiturage_id}` | Supprime définitivement une offre de covoiturage. |

## Champs des routes

Les champs ci-dessous correspondent aux corps JSON utilisés par les routes
`POST` et `PATCH`. Les identifiants suffixés par `_id` sont des ObjectId
MongoDB représentés sous forme de chaînes dans les requêtes HTTP.

### Authentification et utilisateurs

| Ressource | Champs | Description |
|---|---|---|
| Inscription | `nom`, `email`, `password`, `role` | Informations du compte. Le rôle vaut `membre` par défaut et le mot de passe est hashé. |
| Connexion | `username`, `password` | `username` contient l'email du compte. Les champs sont envoyés en `application/x-www-form-urlencoded`. |
| Utilisateur | `user_id` | Identifiant présent dans l'URL pour consulter, modifier ou supprimer un compte. |

### Événements

| Champ | Type / contenu | Description |
|---|---|---|
| `nom` | Texte | Nom affiché de l'événement. |
| `description` | Texte | Présentation, programme et informations pratiques. |
| `date_debut`, `date_fin` | Date ISO avec heure | Période de déroulement de l'événement. |
| `lieu` | Texte | Adresse ou lieu de l'événement. |
| `photo_couverture` | URL ou texte | Image de couverture de l'événement. |
| `visibilite` | `public` ou `prive` | Définit si l'événement est visible par tous ou réservé aux personnes autorisées. |
| `organisateurs` | Liste d'`user_id` | Doit contenir au moins un organisateur. |
| `participants` | Liste d'`user_id` | Participants inscrits à l'événement, vide par défaut. |
| `shopping_list_active` | Booléen | Autorise ou non les contributions de shopping list. |
| `covoiturage_active` | Booléen | Autorise ou non la création d'offres de covoiturage. |

### Groupes

| Champ | Type / contenu | Description |
|---|---|---|
| `nom` | Texte | Nom du groupe. |
| `description` | Texte | Présentation et objectif du groupe. |
| `icone`, `photo_couverture` | URL ou texte | Images utilisées pour représenter le groupe. |
| `type_groupe` | `public`, `privé` ou `secret` | Niveau de visibilité du groupe. |
| `autorise_membre_publier` | Booléen | Autorise les membres à publier dans le groupe. |
| `autorise_membre_creer_event` | Booléen | Autorise les membres à créer des événements. |
| `membres` | Liste d'`user_id` | Membres du groupe, au moins un requis. |
| `administrateurs` | Liste d'`user_id` | Administrateurs du groupe, au moins un requis. |

### Discussions, messages et commentaires

| Champ | Type / contenu | Description |
|---|---|---|
| `groupe_id` | `group_id` optionnel | Groupe auquel le fil est rattaché. |
| `evenement_id` | `event_id` optionnel | Événement auquel le fil est rattaché. |
| `auteur_id` | `user_id` | Auteur d'un message ou d'un commentaire. |
| `contenu` | Texte | Contenu du message ou du commentaire. |
| `discussion_id` | Identifiant d'URL | Fil ciblé par la route. |
| `message_id` | Identifiant d'URL | Message ciblé pour ajouter un commentaire. |

Un fil doit fournir exactement un seul de `groupe_id` ou `evenement_id`.
Les messages et commentaires reçoivent automatiquement leur date de création
et leur identifiant.

### Albums et photos

| Champ | Type / contenu | Description |
|---|---|---|
| `evenement_id` | `event_id` | Événement auquel l'album est associé. |
| `participant_id` | `user_id` | Participant qui publie la photo. |
| `url` | URL ou texte | Adresse de la photo publiée. |
| `auteur_id` | `user_id` | Participant qui écrit un commentaire. |
| `contenu` | Texte | Texte du commentaire de photo. |
| `album_id`, `photo_id` | Identifiants d'URL | Album et photo ciblés par les routes imbriquées. |

### Sondages et votes

| Champ | Type / contenu | Description |
|---|---|---|
| `evenement_id` | `event_id` | Événement concerné par le sondage. |
| `createur_id` | `user_id` | Organisateur à l'origine du sondage. |
| `questions` | Liste | Une question minimum est requise. |
| `questions[].texte` | Texte | Énoncé de la question. |
| `questions[].choix` | Liste | Au moins deux choix sont nécessaires par question. |
| `questions[].choix[].texte` | Texte | Réponse possible proposée au participant. |
| `participant_id` | `user_id` | Participant qui répond au sondage. |
| `question_id`, `choix_id` | Identifiants | Question et choix sélectionnés pour le vote. |

Chaque question et chaque choix reçoit automatiquement un identifiant. Un
participant ne peut enregistrer qu'un vote pour une même question.

### Billetteries et achats

| Champ | Type / contenu | Description |
|---|---|---|
| `evenement_id` | `event_id` | Événement public concerné par la billetterie. |
| `organisateur_id` | `user_id` | Organisateur autorisé à créer la billetterie. |
| `types_billets` | Liste | Types proposés, au moins un requis. |
| `types_billets[].nom` | Texte | Nom commercial du billet. |
| `types_billets[].montant` | Nombre positif ou nul | Prix du billet. |
| `types_billets[].quantite_limitee` | Entier positif | Nombre maximal de billets de ce type. |
| `type_billet_id` | Identifiant | Type de billet choisi lors de l'achat. |
| `acheteur.nom`, `acheteur.prenom` | Texte | Identité de la personne extérieure. |
| `acheteur.adresse_complete` | Texte | Adresse complète de l'acheteur. |

La date d'achat et les identifiants des billets sont générés automatiquement.
Une personne ne peut obtenir qu'un seul billet dans une billetterie.

### Shopping lists

| Champ | Type / contenu | Description |
|---|---|---|
| `evenement_id` | `event_id` | Événement dont la shopping list est utilisée. |
| `utilisateur_id` | `user_id` | Utilisateur qui indique ce qu'il apporte. |
| `nom` | Texte unique par événement | Nom de l'élément apporté. |
| `quantite` | Entier strictement positif | Quantité prévue. |
| `heure_arrivee` | Date ISO avec heure | Heure prévue d'arrivée de l'utilisateur. |
| `item_id` | Identifiant d'URL | Élément ciblé pour la consultation, modification ou suppression. |

La création est possible uniquement lorsque `shopping_list_active` vaut `true`.

### Covoiturages

| Champ | Type / contenu | Description |
|---|---|---|
| `evenement_id` | `event_id` | Événement auquel l'offre est associée. |
| `conducteur_id` | `user_id` | Utilisateur qui propose le trajet. |
| `lieu_depart` | Texte | Point de départ du trajet. |
| `heure_depart` | Date ISO avec heure | Date et heure prévues du départ. |
| `prix` | Nombre positif ou nul | Participation financière demandée. |
| `places_disponibles` | Entier strictement positif | Nombre de places proposées. |
| `ecart_max_minutes` | Entier positif ou nul | Temps de détour maximal accepté en minutes. |
| `covoiturage_id` | Identifiant d'URL | Offre ciblée pour la consultation, modification ou suppression. |

La création d'une offre est possible uniquement lorsque
`covoiturage_active` vaut `true` pour l'événement.

## Champs attendus par endpoint

Cette synthèse associe chaque opération d'écriture à son corps de requête.
Les routes `GET`, `PATCH` et `DELETE` utilisant un identifiant indiquent
celui-ci directement dans l'URL.

| Endpoint | Corps attendu |
|---|---|
| `POST /auth/register` | `nom`, `email`, `password`, `role` optionnel |
| `POST /auth/login` | Formulaire `username` et `password` |
| `POST /users/` | `nom`, `email`, `password`, `role` |
| `PATCH /users/{user_id}` | Au moins un champ parmi `nom`, `email`, `password`, `role` |
| `POST /events/` | `nom`, `description`, `date_debut`, `date_fin`, `lieu`, `photo_couverture`, `visibilite`, `organisateurs`, `participants` optionnel, `shopping_list_active` optionnel, `covoiturage_active` optionnel |
| `PATCH /events/{event_id}` | Tous les champs d'événement sont optionnels ; seuls les champs fournis sont modifiés |
| `POST /groupes/` | `nom`, `description`, `icone`, `photo_couverture`, `type_groupe`, `autorise_membre_publier`, `autorise_membre_creer_event`, `membres`, `administrateurs` |
| `PATCH /groupes/{groupe_id}` | Champs du groupe optionnels, avec au moins un membre et un administrateur si les listes sont envoyées |
| `POST /discussions/` | Un seul des champs `groupe_id` ou `evenement_id` |
| `PATCH /discussions/{discussion_id}` | `messages` optionnel, sous forme de liste de messages |
| `POST /discussions/{discussion_id}/messages` | `auteur_id`, `contenu` |
| `POST /discussions/{discussion_id}/messages/{message_id}/commentaires` | `auteur_id`, `contenu` |
| `POST /albums/` | `evenement_id` |
| `PATCH /albums/{album_id}` | `evenement_id` optionnel |
| `POST /albums/{album_id}/photos` | `participant_id`, `url` |
| `POST /albums/{album_id}/photos/{photo_id}/commentaires` | `auteur_id`, `contenu` |
| `POST /sondages/` | `evenement_id`, `createur_id`, `questions` avec au moins deux choix par question |
| `PATCH /sondages/{sondage_id}` | `questions` optionnel, avec au moins une question |
| `POST /sondages/{sondage_id}/votes` | `participant_id`, `question_id`, `choix_id` |
| `POST /billetteries/` | `evenement_id`, `organisateur_id`, `types_billets` |
| `PATCH /billetteries/{billetterie_id}` | `types_billets` optionnel |
| `POST /billetteries/{billetterie_id}/billets` | `type_billet_id`, `acheteur.nom`, `acheteur.prenom`, `acheteur.adresse_complete` |
| `POST /shopping-list/` | `evenement_id`, `utilisateur_id`, `nom`, `quantite`, `heure_arrivee` |
| `PATCH /shopping-list/{item_id}` | `nom`, `quantite` et `heure_arrivee` optionnels |
| `POST /covoiturages/` | `evenement_id`, `conducteur_id`, `lieu_depart`, `heure_depart`, `prix`, `places_disponibles`, `ecart_max_minutes` |
| `PATCH /covoiturages/{covoiturage_id}` | `lieu_depart`, `heure_depart`, `prix`, `places_disponibles`, `ecart_max_minutes` optionnels |

Les réponses de création incluent les identifiants générés par MongoDB. Les
dates de création, dates d'achat et identifiants internes des messages,
photos, choix et billets sont générés automatiquement par l'application.

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

Les mots de passe sont hashés avant leur enregistrement en base et ne sont pas
renvoyés par les endpoints utilisateurs. Les routes métier vérifient la
présence et la validité du token JWT dans l'en-tête `Authorization`.

Les valeurs présentes dans [data/samples.py](data/samples.py) sont uniquement
destinées au développement et aux tests locaux. Elles ne doivent pas être
utilisées dans un environnement de production.