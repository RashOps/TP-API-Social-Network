from beanie import PydanticObjectId
from fastapi import APIRouter, Depends, HTTPException, status

from src.auth import get_current_user
from src.models.groupe import Groupe, GroupeCreate, GroupeUpdate


router = APIRouter(
    prefix="/groupes",
    tags=["Groupes"],
    dependencies=[Depends(get_current_user)],
)


@router.get(
    "/",
    summary="Lister les groupes",
    description=(
        "Retourne la liste des groupes enregistrés avec leur nom, leur type, "
        "leurs règles de publication et de création d'événements. Chaque "
        "groupe expose également ses membres et ses administrateurs."
    ),
)
async def list_groupes() -> list[Groupe]:
    """Retourne tous les groupes enregistrés."""
    return await Groupe.find_all().to_list()


@router.get(
    "/{groupe_id}",
    summary="Consulter un groupe",
    description=(
        "Retourne le détail d'un groupe à partir de `groupe_id`, notamment "
        "sa visibilité, ses autorisations, ses membres et ses administrateurs. "
        "Une réponse 404 est renvoyée si le groupe est introuvable."
    ),
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
    description=(
        "Crée un groupe public, privé ou secret avec ses règles de "
        "fonctionnement. Le groupe doit contenir au moins un membre et un "
        "administrateur. Retourne le document créé avec le statut 201."
    ),
)
async def create_groupe(groupe_data: GroupeCreate) -> Groupe:
    """Crée un groupe avec au moins un membre et un administrateur."""
    groupe = Groupe(**groupe_data.model_dump())
    await groupe.insert()
    return groupe


@router.patch(
    "/{groupe_id}",
    summary="Modifier un groupe",
    description=(
        "Modifie partiellement un groupe existant, ses informations, ses "
        "permissions, sa liste de membres ou ses administrateurs. Les champs "
        "non transmis restent inchangés et un groupe doit toujours conserver "
        "au moins un membre et un administrateur."
    ),
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
    description=(
        "Supprime définitivement le groupe identifié par `groupe_id`. "
        "L'opération retourne 204 sans contenu si elle réussit et 404 si le "
        "groupe demandé n'existe pas."
    ),
)
async def delete_groupe(groupe_id: PydanticObjectId) -> None:
    """Supprime un groupe existant."""
    groupe = await Groupe.get(groupe_id)
    if groupe is None:
        raise HTTPException(status_code=404, detail="Groupe introuvable")

    await groupe.delete()
