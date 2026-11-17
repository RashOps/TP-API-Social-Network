from datetime import datetime

from beanie import Document, PydanticObjectId
from pydantic import BaseModel, Field


class ShoppingItemCreate(BaseModel):
    evenement_id: PydanticObjectId
    utilisateur_id: PydanticObjectId
    nom: str
    quantite: int = Field(gt=0)
    heure_arrivee: datetime


class ShoppingItemUpdate(BaseModel):
    nom: str | None = None
    quantite: int | None = Field(default=None, gt=0)
    heure_arrivee: datetime | None = None


class ShoppingItem(Document):
    evenement_id: PydanticObjectId
    utilisateur_id: PydanticObjectId
    nom: str
    quantite: int = Field(gt=0)
    heure_arrivee: datetime

    class Settings:
        name = "shopping_list"

