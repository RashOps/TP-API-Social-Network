from beanie import PydanticObjectId
from fastapi import APIRouter, HTTPException, status

from src.models.groupe import Groupe, GroupeCreate, GroupeUpdate


router = APIRouter(
    prefix="/groupes",
    tags=["Groupes"],
)


@router.get(
    "/",
    summary="Lister les groupes",
    description="Retourne tous les groupes avec leurs membres et administrateurs.",
)
async def list_groupes() -> list[Groupe]:
    """Retourne tous les groupes enregistrés."""
    return await Groupe.find_all().to_list()


@router.get(
    "/{groupe_id}",
    summary="Consulter un groupe",
    description="Retourne le détail d'un groupe grâce à son identifiant. Retourne 404 s'il n'existe pas.",
)
async def get_groupe(groupe_id: PydanticObjectId) -> Groupe:
    """Retourne un groupe avec ses membres et administrateurs."""
    groupe = await Groupe.get(groupe_id)
    if groupe is None:
        raise HTTPException(status_code=404, detail="Groupe introuvable")

    return groupe


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    summary="Créer un groupe",
    description="Crée un groupe avec au moins un membre et un administrateur.",
)
async def create_groupe(groupe_data: GroupeCreate) -> Groupe:
    """Crée un groupe avec au moins un membre et un administrateur."""
    groupe = Groupe(**groupe_data.model_dump())
    await groupe.insert()
    return groupe


@router.patch(
    "/{groupe_id}",
    summary="Modifier un groupe",
    description="Met à jour les informations, membres et administrateurs d'un groupe existant.",
)
async def update_groupe(
    groupe_id: PydanticObjectId,
    groupe_data: GroupeUpdate,
) -> Groupe:
    """Modifie les informations, membres ou administrateurs d'un groupe."""
    groupe = await Groupe.get(groupe_id)
    if groupe is None:
        raise HTTPException(status_code=404, detail="Groupe introuvable")

    for field, value in groupe_data.model_dump(exclude_unset=True).items():
        setattr(groupe, field, value)

    await groupe.save()
    return groupe


@router.delete(
    "/{groupe_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Supprimer un groupe",
    description="Supprime définitivement le groupe indiqué et retourne 204 en cas de succès.",
)
async def delete_groupe(groupe_id: PydanticObjectId) -> None:
    """Supprime un groupe existant."""
    groupe = await Groupe.get(groupe_id)
    if groupe is None:
        raise HTTPException(status_code=404, detail="Groupe introuvable")

    await groupe.delete()
