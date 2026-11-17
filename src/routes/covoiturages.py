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


@router.get(
    "/",
    summary="Lister les offres de covoiturage",
    description="Retourne toutes les offres de covoiturage disponibles dans l'application.",
)
async def list_covoiturages() -> list[Covoiturage]:
    """Retourne toutes les offres de covoiturage."""
    return await Covoiturage.find_all().to_list()


@router.get(
    "/{covoiturage_id}",
    summary="Consulter une offre",
    description="Retourne une offre de covoiturage avec son départ, son prix et ses places disponibles.",
)
async def get_covoiturage(
    covoiturage_id: PydanticObjectId,
) -> Covoiturage:
    """Retourne une offre de covoiturage grâce à son identifiant."""
    covoiturage = await Covoiturage.get(covoiturage_id)
    if covoiturage is None:
        raise HTTPException(status_code=404, detail="Covoiturage introuvable")

    return covoiturage


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    summary="Créer une offre",
    description="Crée une offre uniquement si le covoiturage est activé pour l'événement.",
)
async def create_covoiturage(data: CovoiturageCreate) -> Covoiturage:
    """Crée une offre si le covoiturage est activé pour l'événement."""
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


@router.patch(
    "/{covoiturage_id}",
    summary="Modifier une offre",
    description="Met à jour les informations d'une offre de covoiturage existante.",
)
async def update_covoiturage(
    covoiturage_id: PydanticObjectId,
    data: CovoiturageUpdate,
) -> Covoiturage:
    """Modifie les informations d'une offre de covoiturage."""
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
    summary="Supprimer une offre",
    description="Supprime définitivement une offre de covoiturage.",
)
async def delete_covoiturage(covoiturage_id: PydanticObjectId) -> None:
    """Supprime une offre de covoiturage."""
    covoiturage = await Covoiturage.get(covoiturage_id)
    if covoiturage is None:
        raise HTTPException(status_code=404, detail="Covoiturage introuvable")

    await covoiturage.delete()
