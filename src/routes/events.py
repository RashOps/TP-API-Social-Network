from beanie import PydanticObjectId
from fastapi import APIRouter, HTTPException, status

from src.models.event import Event, EventCreate, EventUpdate


router = APIRouter(
    prefix="/events",
    tags=["Events"],
)


@router.get(
    "/",
    summary="Lister les événements",
    description="Retourne tous les événements avec leurs organisateurs et participants.",
)
async def list_events() -> list[Event]:
    """Retourne la liste complète des événements."""
    return await Event.find_all().to_list()


@router.get(
    "/{event_id}",
    summary="Consulter un événement",
    description="Retourne le détail d'un événement. Retourne 404 si l'identifiant est inconnu.",
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
    description="Crée un événement avec au moins un organisateur. Les options shopping list et covoiturage sont désactivées par défaut.",
)
async def create_event(event_data: EventCreate) -> Event:
    """Crée un événement avec au moins un organisateur."""
    event = Event(**event_data.model_dump())
    await event.insert()
    return event


@router.patch(
    "/{event_id}",
    summary="Modifier un événement",
    description="Met à jour partiellement un événement et ses options. Retourne 404 si l'événement n'existe pas.",
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
    description="Supprime définitivement l'événement indiqué et retourne 204 en cas de succès.",
)
async def delete_event(event_id: PydanticObjectId) -> None:
    """Supprime définitivement un événement."""
    event = await Event.get(event_id)
    if event is None:
        raise HTTPException(status_code=404, detail="Événement introuvable")

    await event.delete()
