import asyncio
import sys
from datetime import datetime, timedelta
from pathlib import Path

from beanie import PydanticObjectId

# Permet aussi l'exécution directe avec `python data/samples.py`.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.auth import hash_password
from src.models.album import Album, Photo
from src.models.billetterie import Acheteur, Billet, Billetterie, TypeBillet
from src.models.covoiturage import Covoiturage
from src.models.discussion import Commentaire, Discussion, Message
from src.models.event import Event
from src.models.groupe import Groupe
from src.models.sondage import Choix, Question, Sondage
from src.models.shopping_list import ShoppingItem
from src.models.user import User
from src.utils.db_client import init_db


USER_ORGANIZER_ID = PydanticObjectId("000000000000000000000001")
USER_MEMBER_ID = PydanticObjectId("000000000000000000000002")
EVENT_ID = PydanticObjectId("100000000000000000000001")
GROUP_ID = PydanticObjectId("200000000000000000000001")
DISCUSSION_ID = PydanticObjectId("300000000000000000000001")
ALBUM_ID = PydanticObjectId("400000000000000000000001")
POLL_ID = PydanticObjectId("500000000000000000000001")
TICKETING_ID = PydanticObjectId("600000000000000000000001")
SHOPPING_ITEM_ID = PydanticObjectId("700000000000000000000001")
CARPOOL_ID = PydanticObjectId("800000000000000000000001")


async def save_sample(document) -> None:
    existing = await type(document).get(document.id)
    if existing is None:
        await document.insert()
    else:
        await document.replace()


async def main() -> None:
    client = await init_db(
        [User, Groupe, Event, Discussion, Album, Sondage, Billetterie, ShoppingItem, Covoiturage]
    )
    try:
        user_organizer = User(
            id=USER_ORGANIZER_ID,
            nom="Alice Organisatrice",
            email="alice@example.com",
            password=hash_password("sample-password"),
            role="organisateur",
        )
        user_member = User(
            id=USER_MEMBER_ID,
            nom="Bob Participant",
            email="bob@example.com",
            password=hash_password("sample-password"),
            role="membre",
        )
        await save_sample(user_organizer)
        await save_sample(user_member)

        event = Event(
            id=EVENT_ID,
            nom="Conférence Python",
            description="Une conférence autour de Python et du développement web.",
            date_debut=datetime.now() + timedelta(days=7),
            date_fin=datetime.now() + timedelta(days=7, hours=4),
            lieu="Paris",
            photo_couverture="https://example.com/events/python.jpg",
            visibilite="public",
            shopping_list_active=True,
            covoiturage_active=True,
            organisateurs=[USER_ORGANIZER_ID],
            participants=[USER_ORGANIZER_ID, USER_MEMBER_ID],
        )
        await save_sample(event)

        groupe = Groupe(
            id=GROUP_ID,
            nom="Communauté Python",
            description="Groupe des passionnés de Python.",
            icone="https://example.com/groups/python-icon.png",
            photo_couverture="https://example.com/groups/python-cover.jpg",
            type_groupe="public",
            autorise_membre_publier=True,
            autorise_membre_creer_event=True,
            membres=[USER_ORGANIZER_ID, USER_MEMBER_ID],
            administrateurs=[USER_ORGANIZER_ID],
        )
        await save_sample(groupe)

        message = Message(
            auteur_id=USER_MEMBER_ID,
            contenu="J'ai hâte de participer à la conférence !",
            commentaires=[
                Commentaire(
                    auteur_id=USER_ORGANIZER_ID,
                    contenu="Ravi de vous accueillir.",
                )
            ],
        )
        await save_sample(
            Discussion(
                id=DISCUSSION_ID,
                groupe_id=GROUP_ID,
                messages=[message],
            )
        )

        await save_sample(
            Album(
                id=ALBUM_ID,
                evenement_id=EVENT_ID,
                photos=[
                    Photo(
                        participant_id=USER_MEMBER_ID,
                        url="https://example.com/photos/conference.jpg",
                    )
                ],
            )
        )

        question = Question(
            texte="Quel atelier préférez-vous ?",
            choix=[
                Choix(texte="API REST"),
                Choix(texte="Tests automatisés"),
            ],
        )
        await save_sample(
            Sondage(
                id=POLL_ID,
                evenement_id=EVENT_ID,
                createur_id=USER_ORGANIZER_ID,
                questions=[question],
            )
        )

        ticket_type = TypeBillet(
            nom="Entrée standard",
            montant=15.0,
            quantite_limitee=100,
        )
        await save_sample(
            Billetterie(
                id=TICKETING_ID,
                evenement_id=EVENT_ID,
                types_billets=[ticket_type],
                billets=[
                    Billet(
                        type_billet_id=ticket_type.id,
                        acheteur=Acheteur(
                            nom="Martin",
                            prenom="Claire",
                            adresse_complete="10 rue de Paris, 75001 Paris",
                        ),
                    )
                ],
            )
        )

        await save_sample(
            ShoppingItem(
                id=SHOPPING_ITEM_ID,
                evenement_id=EVENT_ID,
                utilisateur_id=USER_MEMBER_ID,
                nom="Bouteilles d'eau",
                quantite=12,
                heure_arrivee=datetime.now().replace(
                    hour=9,
                    minute=30,
                    second=0,
                    microsecond=0,
                ),
            )
        )

        await save_sample(
            Covoiturage(
                id=CARPOOL_ID,
                evenement_id=EVENT_ID,
                conducteur_id=USER_ORGANIZER_ID,
                lieu_depart="Lyon",
                heure_depart=datetime.now() + timedelta(days=7),
                prix=10.0,
                places_disponibles=3,
                ecart_max_minutes=30,
            )
        )
    finally:
        await client.close()


if __name__ == "__main__":
    asyncio.run(main())
