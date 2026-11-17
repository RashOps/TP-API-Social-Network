from beanie import PydanticObjectId
from fastapi import APIRouter, Depends, HTTPException, status
from pymongo.errors import DuplicateKeyError

from src.auth import get_current_user, hash_password
from src.models.user import User, UserCreate, UserResponse, UserUpdate


router = APIRouter(
    prefix="/users",
    tags=["Users"],
    dependencies=[Depends(get_current_user)],
)


@router.get(
    "/",
    response_model=list[UserResponse],
    summary="Lister les utilisateurs",
    description=(
        "Retourne la liste complète des utilisateurs enregistrés dans MongoDB. "
        "Chaque élément contient les informations publiques du compte et son "
        "identifiant. Cette route est en lecture seule et retourne une liste "
        "vide si aucun utilisateur n'est enregistré."
    ),
)
async def list_users() -> list[User]:
    """Retourne tous les utilisateurs enregistrés."""
    return await User.find_all().to_list()


@router.get(
    "/{user_id}",
    response_model=UserResponse,
    summary="Consulter un utilisateur",
    description=(
        "Recherche un utilisateur à partir de son identifiant MongoDB valide "
        "et retourne ses informations. Une réponse 404 est renvoyée si aucun "
        "utilisateur ne correspond à l'identifiant fourni."
    ),
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
    response_model=UserResponse,
    summary="Créer un utilisateur",
    description=(
        "Crée un compte utilisateur à partir de son nom, son email, son mot "
        "de passe et son rôle. L'email est validé puis contrôlé par un index "
        "unique MongoDB : une adresse déjà utilisée retourne 409. Une réponse "
        "201 contient l'utilisateur nouvellement créé."
    ),
)
async def create_user(user_data: UserCreate) -> User:
    """Crée un utilisateur et refuse les emails déjà utilisés."""
    user_values = user_data.model_dump()
    user_values["password"] = hash_password(user_values["password"])
    user = User(**user_values)
    try:
        await user.insert()
    except DuplicateKeyError:
        raise HTTPException(status_code=409, detail="Cet email est déjà utilisé")

    return user


@router.patch(
    "/{user_id}",
    response_model=UserResponse,
    summary="Modifier un utilisateur",
    description=(
        "Met à jour partiellement le compte correspondant à `user_id`. Les "
        "champs absents sont conservés et seuls les champs fournis sont "
        "modifiés. Retourne 404 si l'utilisateur n'existe pas ou 409 si le "
        "nouvel email est déjà utilisé."
    ),
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
    description=(
        "Supprime définitivement le compte correspondant à `user_id`. "
        "L'opération ne retourne pas de contenu en cas de succès et renvoie "
        "204. Une réponse 404 est produite lorsque l'utilisateur est absent."
    ),
)
async def delete_user(user_id: PydanticObjectId) -> None:
    """Supprime un utilisateur existant."""
    user = await User.get(user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="Utilisateur introuvable")

    await user.delete()
