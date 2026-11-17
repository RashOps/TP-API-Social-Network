from datetime import datetime

from beanie import Document, PydanticObjectId
from pydantic import BaseModel, Field


class TypeBillet(BaseModel):
    id: PydanticObjectId = Field(default_factory=PydanticObjectId)
    nom: str
    montant: float = Field(ge=0)
    quantite_limitee: int = Field(gt=0)


class Acheteur(BaseModel):
    nom: str
    prenom: str
    adresse_complete: str


class Billet(BaseModel):
    id: PydanticObjectId = Field(default_factory=PydanticObjectId)
    type_billet_id: PydanticObjectId
    acheteur: Acheteur
    date_achat: datetime = Field(default_factory=datetime.utcnow)


class BilletterieCreate(BaseModel):
    evenement_id: PydanticObjectId
    organisateur_id: PydanticObjectId
    types_billets: list[TypeBillet] = Field(min_length=1)


class BilletterieUpdate(BaseModel):
    types_billets: list[TypeBillet] | None = Field(default=None, min_length=1)


class AchatBilletCreate(BaseModel):
    type_billet_id: PydanticObjectId
    acheteur: Acheteur


class Billetterie(Document):
    evenement_id: PydanticObjectId
    types_billets: list[TypeBillet] = Field(min_length=1)
    billets: list[Billet] = Field(default_factory=list)

    class Settings:
        name = "billetteries"

