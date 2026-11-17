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
    description=(
        "Retourne toutes les offres de covoiturage enregistrées, avec leur "
        "événement, conducteur, lieu de départ, heure, prix, nombre de places "
        "et écart maximal accepté."
    ),
)
async def list_covoiturages() -> list[Covoiturage]:
    """Retourne toutes les offres de covoiturage."""
    return await Covoiturage.find_all().to_list()


@router.get(
    "/{covoiturage_id}",
    summary="Consulter une offre",
    description=(
        "Retourne le détail d'une offre grâce à `covoiturage_id`. La réponse "
        "décrit le trajet proposé et ses conditions : départ, horaire, prix, "
        "places disponibles et marge de temps autorisée. Retourne 404 si "
        "l'offre n'existe pas."
    ),
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
    description=(
        "Crée une offre de trajet associée à un événement. L'événement doit "
        "exister et avoir l'option covoiturage activée ; sinon la création est "
        "refusée. Le prix doit être positif ou nul, le nombre de places "
        "strictement positif et l'écart maximal supérieur ou égal à zéro."
    ),
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
    description=(
        "Met à jour partiellement une offre de covoiturage existante. Les "
        "champs non fournis restent inchangés et les contraintes de prix, de "
        "places et d'écart maximal sont revalidées automatiquement."
    ),
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
    description=(
        "Supprime définitivement l'offre correspondant à `covoiturage_id`. "
        "Retourne 204 sans contenu en cas de succès et 404 lorsque l'offre "
        "demandée n'existe pas."
    ),
)
async def delete_covoiturage(covoiturage_id: PydanticObjectId) -> None:
    """Supprime une offre de covoiturage."""
    covoiturage = await Covoiturage.get(covoiturage_id)
    if covoiturage is None:
        raise HTTPException(status_code=404, detail="Covoiturage introuvable")

    await covoiturage.delete()
