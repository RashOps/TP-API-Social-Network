from beanie import PydanticObjectId
from fastapi import APIRouter, Depends, HTTPException, status

from src.auth import get_current_user
from src.models.event import Event
from src.models.shopping_list import (
    ShoppingItem,
    ShoppingItemCreate,
    ShoppingItemUpdate,
)


router = APIRouter(
    prefix="/shopping-list",
    tags=["Shopping list"],
    dependencies=[Depends(get_current_user)],
)


@router.get(
    "/",
    summary="Lister les éléments",
    description=(
        "Retourne toutes les contributions enregistrées dans les shopping "
        "lists. Chaque élément indique l'événement, l'utilisateur, le nom de "
        "la contribution, sa quantité et son heure d'arrivée."
    ),
)
async def list_items() -> list[ShoppingItem]:
    """Retourne tous les éléments des shopping lists."""
    return await ShoppingItem.find_all().to_list()


@router.get(
    "/{item_id}",
    summary="Consulter un élément",
    description=(
        "Retourne une contribution précise à partir de `item_id`. Le résultat "
        "contient les informations de l'utilisateur et de l'événement associés. "
        "Retourne 404 si l'élément demandé n'existe pas."
    ),
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
    description=(
        "Ajoute une contribution à un événement lorsque sa shopping list est "
        "activée. Le nom de l'élément doit être unique dans cet événement, la "
        "quantité doit être positive et l'heure d'arrivée doit être valide. "
        "L'événement désactivé retourne 400 et un doublon retourne 409."
    ),
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
    description=(
        "Modifie partiellement une contribution existante, notamment son nom, "
        "sa quantité ou son heure d'arrivée. Un changement de nom est contrôlé "
        "pour conserver l'unicité des éléments dans l'événement. Retourne 404 "
        "si l'élément est absent et 409 en cas de doublon."
    ),
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
    description=(
        "Supprime définitivement une contribution de la shopping list. "
        "Retourne 204 sans contenu si la suppression réussit et 404 si "
        "l'identifiant ne correspond à aucun élément."
    ),
)
async def delete_item(item_id: PydanticObjectId) -> None:
    """Supprime un élément d'une shopping list."""
    item = await ShoppingItem.get(item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Élément introuvable")

    await item.delete()
