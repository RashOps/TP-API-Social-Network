from beanie import PydanticObjectId
from fastapi import APIRouter, HTTPException, status

from src.models.event import Event, EventCreate, EventUpdate


router = APIRouter(
    prefix="/events",
    tags=["Events"],
)


@router.get("/")
async def list_events() -> list[Event]:
    return await Event.find_all().to_list()


@router.get("/{event_id}")
async def get_event(event_id: PydanticObjectId) -> Event:
    event = await Event.get(event_id)
    if event is None:
        raise HTTPException(status_code=404, detail="Événement introuvable")

    return event


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_event(event_data: EventCreate) -> Event:
    event = Event(**event_data.model_dump())
    await event.insert()
    return event


@router.patch("/{event_id}")
async def update_event(
    event_id: PydanticObjectId,
    event_data: EventUpdate,
) -> Event:
    event = await Event.get(event_id)
    if event is None:
        raise HTTPException(status_code=404, detail="Événement introuvable")

    for field, value in event_data.model_dump(exclude_unset=True).items():
        setattr(event, field, value)

    await event.save()
    return event


@router.delete("/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_event(event_id: PydanticObjectId) -> None:
    event = await Event.get(event_id)
    if event is None:
        raise HTTPException(status_code=404, detail="Événement introuvable")

    await event.delete()
