from beanie import PydanticObjectId
from fastapi import APIRouter, HTTPException, status

from src.models.covoiturage import (
    Covoiturage,
    CovoiturageCreate,
    CovoiturageUpdate,
)
from src.models.event import Event


router = APIRouter(
    prefix="/covoiturages",
    tags=["Covoiturages"],
)


@router.get("/")
async def list_covoiturages() -> list[Covoiturage]:
    return await Covoiturage.find_all().to_list()


@router.get("/{covoiturage_id}")
async def get_covoiturage(
    covoiturage_id: PydanticObjectId,
) -> Covoiturage:
    covoiturage = await Covoiturage.get(covoiturage_id)
    if covoiturage is None:
        raise HTTPException(status_code=404, detail="Covoiturage introuvable")

    return covoiturage


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_covoiturage(data: CovoiturageCreate) -> Covoiturage:
    event = await Event.get(data.evenement_id)
    if event is None:
        raise HTTPException(status_code=404, detail="Événement introuvable")
    if not event.covoiturage_active:
        raise HTTPException(
            status_code=400,
            detail="Le covoiturage est désactivé pour cet événement",
        )

    covoiturage = Covoiturage(**data.model_dump())
    await covoiturage.insert()
    return covoiturage


@router.patch("/{covoiturage_id}")
async def update_covoiturage(
    covoiturage_id: PydanticObjectId,
    data: CovoiturageUpdate,
) -> Covoiturage:
    covoiturage = await Covoiturage.get(covoiturage_id)
    if covoiturage is None:
        raise HTTPException(status_code=404, detail="Covoiturage introuvable")

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(covoiturage, field, value)

    await covoiturage.save()
    return covoiturage


@router.delete(
    "/{covoiturage_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_covoiturage(covoiturage_id: PydanticObjectId) -> None:
    covoiturage = await Covoiturage.get(covoiturage_id)
    if covoiturage is None:
        raise HTTPException(status_code=404, detail="Covoiturage introuvable")

    await covoiturage.delete()
