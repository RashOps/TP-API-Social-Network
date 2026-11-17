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


@router.get(
    "/",
    summary="Lister les billetteries",
    description="Retourne toutes les billetteries avec leurs types de billets et les billets achetés.",
)
async def list_billetteries() -> list[Billetterie]:
    """Retourne toutes les billetteries disponibles."""
    return await Billetterie.find_all().to_list()


@router.get(
    "/{billetterie_id}",
    summary="Consulter une billetterie",
    description="Retourne le détail d'une billetterie. Retourne 404 si elle n'existe pas.",
)
async def get_billetterie(billetterie_id: PydanticObjectId) -> Billetterie:
    """Retourne une billetterie avec ses types de billets et achats."""
    billetterie = await Billetterie.get(billetterie_id)
    if billetterie is None:
        raise HTTPException(status_code=404, detail="Billetterie introuvable")

    return billetterie


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    summary="Créer une billetterie",
    description="Crée une billetterie pour un événement public. Seul un organisateur de l'événement peut la créer.",
)
async def create_billetterie(data: BilletterieCreate) -> Billetterie:
    """Crée une billetterie uniquement pour un événement public."""
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


@router.patch(
    "/{billetterie_id}",
    summary="Modifier une billetterie",
    description="Met à jour les types de billets proposés par une billetterie existante.",
)
async def update_billetterie(
    billetterie_id: PydanticObjectId,
    data: BilletterieUpdate,
) -> Billetterie:
    """Modifie les types de billets d'une billetterie."""
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
    summary="Supprimer une billetterie",
    description="Supprime une billetterie et les billets qui lui sont associés.",
)
async def delete_billetterie(billetterie_id: PydanticObjectId) -> None:
    """Supprime une billetterie et les billets qui lui sont associés."""
    billetterie = await Billetterie.get(billetterie_id)
    if billetterie is None:
        raise HTTPException(status_code=404, detail="Billetterie introuvable")

    await billetterie.delete()


@router.post(
    "/{billetterie_id}/billets",
    status_code=status.HTTP_201_CREATED,
    summary="Acheter un billet",
    description="Achète un billet d'un type disponible. Un acheteur ne peut obtenir qu'un seul billet par billetterie.",
)
async def buy_ticket(
    billetterie_id: PydanticObjectId,
    data: AchatBilletCreate,
) -> Billet:
    """Achète un billet si le type n'est pas épuisé et l'acheteur n'en possède pas déjà un."""
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
