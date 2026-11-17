from datetime import datetime

from beanie import Document, PydanticObjectId
from pydantic import BaseModel, Field, model_validator


class Commentaire(BaseModel):
    auteur_id: PydanticObjectId
    contenu: str
    date_creation: datetime = Field(default_factory=datetime.utcnow)


class Message(BaseModel):
    id: PydanticObjectId = Field(default_factory=PydanticObjectId)
    auteur_id: PydanticObjectId
    contenu: str
    date_creation: datetime = Field(default_factory=datetime.utcnow)
    commentaires: list[Commentaire] = Field(default_factory=list)


class DiscussionCreate(BaseModel):
    groupe_id: PydanticObjectId | None = None
    evenement_id: PydanticObjectId | None = None

    @model_validator(mode="after")
    def validate_parent(self):
        if (self.groupe_id is None) == (self.evenement_id is None):
            raise ValueError(
                "Un fil doit être lié à un groupe ou à un événement, mais pas aux deux"
            )
        return self


class DiscussionUpdate(BaseModel):
    messages: list[Message] | None = None


class Discussion(Document):
    groupe_id: PydanticObjectId | None = None
    evenement_id: PydanticObjectId | None = None
    messages: list[Message] = Field(default_factory=list)

    class Settings:
        name = "discussions"

