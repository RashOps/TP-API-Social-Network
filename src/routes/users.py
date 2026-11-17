from beanie import PydanticObjectId
from fastapi import APIRouter, HTTPException, status
from pymongo.errors import DuplicateKeyError

from src.models.user import User, UserCreate, UserUpdate


router = APIRouter(
    prefix="/users",
    tags=["Users"],
)


@router.get("/")
async def list_users() -> list[User]:
    return await User.find_all().to_list()


@router.get("/{user_id}")
async def get_user(user_id: PydanticObjectId) -> User:
    user = await User.get(user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="Utilisateur introuvable")

    return user


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_user(user_data: UserCreate) -> User:
    user = User(**user_data.model_dump())
    try:
        await user.insert()
    except DuplicateKeyError:
        raise HTTPException(status_code=409, detail="Cet email est déjà utilisé")

    return user


@router.patch("/{user_id}")
async def update_user(
    user_id: PydanticObjectId,
    user_data: UserUpdate,
) -> User:
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


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: PydanticObjectId) -> None:
    user = await User.get(user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="Utilisateur introuvable")

    await user.delete()
