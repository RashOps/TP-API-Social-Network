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


@router.get(
    "/",
    summary="Lister les éléments",
    description="Retourne tous les éléments déclarés dans les shopping lists des événements.",
)
async def list_items() -> list[ShoppingItem]:
    """Retourne tous les éléments des shopping lists."""
    return await ShoppingItem.find_all().to_list()


@router.get(
    "/{item_id}",
    summary="Consulter un élément",
    description="Retourne un élément de shopping list grâce à son identifiant.",
)
async def get_item(item_id: PydanticObjectId) -> ShoppingItem:
    """Retourne un élément de shopping list grâce à son identifiant."""
    item = await ShoppingItem.get(item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Élément introuvable")

    return item


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    summary="Ajouter un élément",
    description="Ajoute une contribution si la shopping list est activée. Le nom doit être unique pour l'événement.",
)
async def create_item(data: ShoppingItemCreate) -> ShoppingItem:
    """Ajoute un élément si la shopping list de l'événement est activée."""
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


@router.patch(
    "/{item_id}",
    summary="Modifier un élément",
    description="Modifie la quantité, l'heure ou le nom sans créer de doublon dans l'événement.",
)
async def update_item(
    item_id: PydanticObjectId,
    data: ShoppingItemUpdate,
) -> ShoppingItem:
    """Modifie un élément sans autoriser un doublon dans l'événement."""
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


@router.delete(
    "/{item_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Supprimer un élément",
    description="Supprime une contribution de la shopping list.",
)
async def delete_item(item_id: PydanticObjectId) -> None:
    """Supprime un élément d'une shopping list."""
    item = await ShoppingItem.get(item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Élément introuvable")

    await item.delete()
