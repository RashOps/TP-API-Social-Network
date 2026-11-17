from typing import Literal

from beanie import Document, PydanticObjectId
from pydantic import BaseModel, Field


class GroupeCreate(BaseModel):
    nom: str
    description: str
    icone: str
    photo_couverture: str
    type_groupe: Literal["public", "privé", "secret"]
    autorise_membre_publier: bool
    autorise_membre_creer_event: bool
    membres: list[PydanticObjectId] = Field(min_length=1)
    administrateurs: list[PydanticObjectId] = Field(min_length=1)


class GroupeUpdate(BaseModel):
    nom: str | None = None
    description: str | None = None
    icone: str | None = None
    photo_couverture: str | None = None
    type_groupe: Literal["public", "privé", "secret"] | None = None
    autorise_membre_publier: bool | None = None
    autorise_membre_creer_event: bool | None = None
    membres: list[PydanticObjectId] | None = Field(default=None, min_length=1)
    administrateurs: list[PydanticObjectId] | None = Field(
        default=None,
        min_length=1,
    )


class Groupe(Document):
    nom: str
    description: str
    icone: str
    photo_couverture: str
    type_groupe: Literal["public", "privé", "secret"]
    autorise_membre_publier: bool
    autorise_membre_creer_event: bool
    membres: list[PydanticObjectId] = Field(min_length=1)
    administrateurs: list[PydanticObjectId] = Field(min_length=1)

    class Settings:
        name = "groupes"