from beanie import PydanticObjectId
from fastapi import APIRouter, HTTPException, status
from pymongo.errors import DuplicateKeyError

from src.models.user import User, UserCreate, UserUpdate


router = APIRouter(
    prefix="/users",
    tags=["Users"],
)


@router.get(
    "/",
    summary="Lister les utilisateurs",
    description="Retourne tous les utilisateurs enregistrés dans la base.",
)
async def list_users() -> list[User]:
    """Retourne tous les utilisateurs enregistrés."""
    return await User.find_all().to_list()


@router.get(
    "/{user_id}",
    summary="Consulter un utilisateur",
    description="Retourne un utilisateur grâce à son identifiant MongoDB. Retourne 404 s'il n'existe pas.",
)
async def get_user(user_id: PydanticObjectId) -> User:
    """Retourne un utilisateur grâce à son identifiant MongoDB."""
    user = await User.get(user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="Utilisateur introuvable")

    return user


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    summary="Créer un utilisateur",
    description="Crée un utilisateur avec un email valide. L'email doit être unique ; un doublon retourne 409.",
)
async def create_user(user_data: UserCreate) -> User:
    """Crée un utilisateur et refuse les emails déjà utilisés."""
    user = User(**user_data.model_dump())
    try:
        await user.insert()
    except DuplicateKeyError:
        raise HTTPException(status_code=409, detail="Cet email est déjà utilisé")

    return user


@router.patch(
    "/{user_id}",
    summary="Modifier un utilisateur",
    description="Modifie uniquement les champs fournis pour l'utilisateur indiqué. Retourne 404 ou 409 selon l'erreur.",
)
async def update_user(
    user_id: PydanticObjectId,
    user_data: UserUpdate,
) -> User:
    """Modifie partiellement les informations d'un utilisateur."""
    user = await User.get(user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="Utilisateur introuvable")

    for field, value in user_data.model_dump(exclude_unset=True).items():
        setattr(user, field, value)

    try:
        await user.save()
    except DuplicateKeyError:
        raise HTTPException(status_code=409, detail="Cet email est déjà utilisé")

    return user


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Supprimer un utilisateur",
    description="Supprime définitivement l'utilisateur indiqué et retourne 204 en cas de succès.",
)
async def delete_user(user_id: PydanticObjectId) -> None:
    """Supprime un utilisateur existant."""
    user = await User.get(user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="Utilisateur introuvable")

    await user.delete()
