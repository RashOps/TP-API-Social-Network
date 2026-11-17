from beanie import PydanticObjectId
from fastapi import APIRouter, HTTPException, status

from src.models.billetterie import (
    AchatBilletCreate,
    Billet,
    Billetterie,
    BilletterieCreate,
    BilletterieUpdate,
)
from src.models.event import Event


router = APIRouter(
    prefix="/billetteries",
    tags=["Billetteries"],
)


@router.get("/")
async def list_billetteries() -> list[Billetterie]:
    return await Billetterie.find_all().to_list()


@router.get("/{billetterie_id}")
async def get_billetterie(billetterie_id: PydanticObjectId) -> Billetterie:
    billetterie = await Billetterie.get(billetterie_id)
    if billetterie is None:
        raise HTTPException(status_code=404, detail="Billetterie introuvable")

    return billetterie


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_billetterie(data: BilletterieCreate) -> Billetterie:
    evenement = await Event.get(data.evenement_id)
    if evenement is None:
        raise HTTPException(status_code=404, detail="Événement introuvable")
    if evenement.visibilite != "public":
        raise HTTPException(
            status_code=400,
            detail="Seuls les événements publics peuvent avoir une billetterie",
        )
    if data.organisateur_id not in evenement.organisateurs:
        raise HTTPException(status_code=403, detail="Organisateur non autorisé")

    billetterie = Billetterie(
        evenement_id=data.evenement_id,
        types_billets=data.types_billets,
    )
    await billetterie.insert()
    return billetterie


@router.patch("/{billetterie_id}")
async def update_billetterie(
    billetterie_id: PydanticObjectId,
    data: BilletterieUpdate,
) -> Billetterie:
    billetterie = await Billetterie.get(billetterie_id)
    if billetterie is None:
        raise HTTPException(status_code=404, detail="Billetterie introuvable")

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(billetterie, field, value)

    await billetterie.save()
    return billetterie


@router.delete(
    "/{billetterie_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_billetterie(billetterie_id: PydanticObjectId) -> None:
    billetterie = await Billetterie.get(billetterie_id)
    if billetterie is None:
        raise HTTPException(status_code=404, detail="Billetterie introuvable")

    await billetterie.delete()


@router.post(
    "/{billetterie_id}/billets",
    status_code=status.HTTP_201_CREATED,
)
async def buy_ticket(
    billetterie_id: PydanticObjectId,
    data: AchatBilletCreate,
) -> Billet:
    billetterie = await Billetterie.get(billetterie_id)
    if billetterie is None:
        raise HTTPException(status_code=404, detail="Billetterie introuvable")

    ticket_type = next(
        (
            ticket_type
            for ticket_type in billetterie.types_billets
            if ticket_type.id == data.type_billet_id
        ),
        None,
    )
    if ticket_type is None:
        raise HTTPException(status_code=404, detail="Type de billet introuvable")

    quantity_sold = sum(
        ticket.type_billet_id == data.type_billet_id
        for ticket in billetterie.billets
    )
    if quantity_sold >= ticket_type.quantite_limitee:
        raise HTTPException(status_code=409, detail="Type de billet épuisé")

    already_bought = any(
        ticket.acheteur == data.acheteur
        for ticket in billetterie.billets
    )
    if already_bought:
        raise HTTPException(
            status_code=409,
            detail="Cette personne possède déjà un billet",
        )

    billet = Billet(
        type_billet_id=data.type_billet_id,
        acheteur=data.acheteur,
    )
    billetterie.billets.append(billet)
    await billetterie.save()
    return billet
