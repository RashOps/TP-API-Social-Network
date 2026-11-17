from datetime import datetime
from typing import Literal

from beanie import Document, PydanticObjectId
from pydantic import BaseModel, Field


class EventCreate(BaseModel):
    nom: str
    description: str
    date_debut: datetime
    date_fin: datetime
    lieu: str
    photo_couverture: str
    visibilite: Literal["public", "prive"]
    shopping_list_active: bool = False
    covoiturage_active: bool = False
    organisateurs: list[PydanticObjectId] = Field(min_length=1)
    participants: list[PydanticObjectId] = Field(default_factory=list)


class EventUpdate(BaseModel):
    nom: str | None = None
    description: str | None = None
    date_debut: datetime | None = None
    date_fin: datetime | None = None
    lieu: str | None = None
    photo_couverture: str | None = None
    visibilite: Literal["public", "prive"] | None = None
    shopping_list_active: bool | None = None
    covoiturage_active: bool | None = None
    organisateurs: list[PydanticObjectId] | None = Field(
        default=None,
        min_length=1,
    )
    participants: list[PydanticObjectId] | None = None


class Event(Document):
    nom: str
    description: str
    date_debut: datetime
    date_fin: datetime
    lieu: str
    photo_couverture: str
    visibilite: Literal["public", "prive"]
    shopping_list_active: bool = False
    covoiturage_active: bool = False
    organisateurs: list[PydanticObjectId] = Field(min_length=1)
    participants: list[PydanticObjectId] = Field(default_factory=list)

    class Settings:
        name = "events"