from datetime import datetime

from beanie import Document, PydanticObjectId
from pydantic import BaseModel, Field


class AlbumCreate(BaseModel):
    evenement_id: PydanticObjectId


class AlbumUpdate(BaseModel):
    evenement_id: PydanticObjectId | None = None


class PhotoCommentaire(BaseModel):
    auteur_id: PydanticObjectId
    contenu: str
    date_creation: datetime = Field(default_factory=datetime.utcnow)


class Photo(BaseModel):
    id: PydanticObjectId = Field(default_factory=PydanticObjectId)
    participant_id: PydanticObjectId
    url: str
    date_creation: datetime = Field(default_factory=datetime.utcnow)
    commentaires: list[PhotoCommentaire] = Field(default_factory=list)


class Album(Document):
    evenement_id: PydanticObjectId
    photos: list[Photo] = Field(default_factory=list)

    class Settings:
        name = "albums"

