from datetime import datetime

from beanie import Document, PydanticObjectId
from pydantic import BaseModel, Field


class CovoiturageCreate(BaseModel):
    evenement_id: PydanticObjectId
    conducteur_id: PydanticObjectId
    lieu_depart: str
    heure_depart: datetime
    prix: float = Field(ge=0)
    places_disponibles: int = Field(gt=0)
    ecart_max_minutes: int = Field(ge=0)


class CovoiturageUpdate(BaseModel):
    lieu_depart: str | None = None
    heure_depart: datetime | None = None
    prix: float | None = Field(default=None, ge=0)
    places_disponibles: int | None = Field(default=None, gt=0)
    ecart_max_minutes: int | None = Field(default=None, ge=0)


class Covoiturage(Document):
    evenement_id: PydanticObjectId
    conducteur_id: PydanticObjectId
    lieu_depart: str
    heure_depart: datetime
    prix: float = Field(ge=0)
    places_disponibles: int = Field(gt=0)
    ecart_max_minutes: int = Field(ge=0)

    class Settings:
        name = "covoiturages"

