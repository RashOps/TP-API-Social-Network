from beanie import PydanticObjectId
from fastapi import APIRouter, HTTPException, status

from src.models.groupe import Groupe, GroupeCreate, GroupeUpdate


router = APIRouter(
    prefix="/groupes",
    tags=["Groupes"],
)


@router.get("/")
async def list_groupes() -> list[Groupe]:
    return await Groupe.find_all().to_list()


@router.get("/{groupe_id}")
async def get_groupe(groupe_id: PydanticObjectId) -> Groupe:
    groupe = await Groupe.get(groupe_id)
    if groupe is None:
        raise HTTPException(status_code=404, detail="Groupe introuvable")

    return groupe


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_groupe(groupe_data: GroupeCreate) -> Groupe:
    groupe = Groupe(**groupe_data.model_dump())
    await groupe.insert()
    return groupe


@router.patch("/{groupe_id}")
async def update_groupe(
    groupe_id: PydanticObjectId,
    groupe_data: GroupeUpdate,
) -> Groupe:
    groupe = await Groupe.get(groupe_id)
    if groupe is None:
        raise HTTPException(status_code=404, detail="Groupe introuvable")

    for field, value in groupe_data.model_dump(exclude_unset=True).items():
        setattr(groupe, field, value)

    await groupe.save()
    return groupe


@router.delete("/{groupe_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_groupe(groupe_id: PydanticObjectId) -> None:
    groupe = await Groupe.get(groupe_id)
    if groupe is None:
        raise HTTPException(status_code=404, detail="Groupe introuvable")

    await groupe.delete()
