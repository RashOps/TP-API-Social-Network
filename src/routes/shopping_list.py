from beanie import PydanticObjectId
from fastapi import APIRouter, HTTPException, status

from src.models.event import Event
from src.models.shopping_list import (
    ShoppingItem,
    ShoppingItemCreate,
    ShoppingItemUpdate,
)


router = APIRouter(
    prefix="/shopping-list",
    tags=["Shopping list"],
)


@router.get("/")
async def list_items() -> list[ShoppingItem]:
    return await ShoppingItem.find_all().to_list()


@router.get("/{item_id}")
async def get_item(item_id: PydanticObjectId) -> ShoppingItem:
    item = await ShoppingItem.get(item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Élément introuvable")

    return item


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_item(data: ShoppingItemCreate) -> ShoppingItem:
    event = await Event.get(data.evenement_id)
    if event is None:
        raise HTTPException(status_code=404, detail="Événement introuvable")
    if not event.shopping_list_active:
        raise HTTPException(
            status_code=400,
            detail="La shopping list est désactivée pour cet événement",
        )

    existing_item = await ShoppingItem.find_one(
        ShoppingItem.evenement_id == data.evenement_id,
        ShoppingItem.nom == data.nom,
    )
    if existing_item is not None:
        raise HTTPException(
            status_code=409,
            detail="Cet élément existe déjà pour cet événement",
        )

    item = ShoppingItem(**data.model_dump())
    await item.insert()
    return item


@router.patch("/{item_id}")
async def update_item(
    item_id: PydanticObjectId,
    data: ShoppingItemUpdate,
) -> ShoppingItem:
    item = await ShoppingItem.get(item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Élément introuvable")

    values = data.model_dump(exclude_unset=True)
    if "nom" in values:
        existing_item = await ShoppingItem.find_one(
            ShoppingItem.evenement_id == item.evenement_id,
            ShoppingItem.nom == values["nom"],
        )
        if existing_item is not None and existing_item.id != item.id:
            raise HTTPException(
                status_code=409,
                detail="Cet élément existe déjà pour cet événement",
            )

    for field, value in values.items():
        setattr(item, field, value)

    await item.save()
    return item


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_item(item_id: PydanticObjectId) -> None:
    item = await ShoppingItem.get(item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Élément introuvable")

    await item.delete()
