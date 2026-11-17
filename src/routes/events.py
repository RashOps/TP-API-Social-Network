from beanie import PydanticObjectId
from fastapi import APIRouter, Depends, HTTPException, status

from src.auth import get_current_user
from src.models.event import Event, EventCreate, EventUpdate


router = APIRouter(
    prefix="/events",
    tags=["Events"],
    dependencies=[Depends(get_current_user)],
)


@router.get(
    "/",
    summary="Lister les événements",
    description=(
        "Retourne tous les événements enregistrés avec leurs informations "
        "principales, leurs organisateurs et leurs participants. Les options "
        "d'activation de la shopping list et du covoiturage sont également "
        "présentes dans chaque événement."
    ),
)
async def list_events() -> list[Event]:
    """Retourne la liste complète des événements."""
    return await Event.find_all().to_list()


@router.get(
    "/{event_id}",
    summary="Consulter un événement",
    description=(
        "Retourne le détail complet d'un événement identifié par `event_id`, "
        "notamment ses dates, son lieu, sa visibilité, ses organisateurs et "
        "ses participants. Retourne 404 si l'identifiant MongoDB est inconnu."
    ),
)
async def get_event(event_id: PydanticObjectId) -> Event:
    """Retourne le détail d'un événement grâce à son identifiant."""
    event = await Event.get(event_id)
    if event is None:
        raise HTTPException(status_code=404, detail="Événement introuvable")

    return event


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    summary="Créer un événement",
    description=(
        "Crée un événement à partir de son nom, sa description, ses dates, "
        "son lieu et sa visibilité. Au moins un organisateur est obligatoire ; "
        "la shopping list et le covoiturage sont désactivés par défaut mais "
        "peuvent être activés dans la requête. Retourne 201 après création."
    ),
)
async def create_event(event_data: EventCreate) -> Event:
    """Crée un événement avec au moins un organisateur."""
    event = Event(**event_data.model_dump())
    await event.insert()
    return event


@router.patch(
    "/{event_id}",
    summary="Modifier un événement",
    description=(
        "Met à jour partiellement l'événement ciblé. Les champs non transmis "
        "restent inchangés, y compris les listes d'organisateurs et de "
        "participants. Les options shopping list et covoiturage peuvent être "
        "activées ou désactivées ; retourne 404 si l'événement est absent."
    ),
)
async def update_event(
    event_id: PydanticObjectId,
    event_data: EventUpdate,
) -> Event:
    """Met à jour les informations d'un événement existant."""
    event = await Event.get(event_id)
    if event is None:
        raise HTTPException(status_code=404, detail="Événement introuvable")

    for field, value in event_data.model_dump(exclude_unset=True).items():
        setattr(event, field, value)

    await event.save()
    return event


@router.delete(
    "/{event_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Supprimer un événement",
    description=(
        "Supprime définitivement l'événement identifié par `event_id`. "
        "Aucun contenu n'est retourné lorsque la suppression réussit et le "
        "statut 204 est renvoyé. Retourne 404 si l'événement n'existe pas."
    ),
)
async def delete_event(event_id: PydanticObjectId) -> None:
    """Supprime définitivement un événement."""
    event = await Event.get(event_id)
    if event is None:
        raise HTTPException(status_code=404, detail="Événement introuvable")

    await event.delete()
