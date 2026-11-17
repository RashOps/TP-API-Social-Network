from datetime import datetime

from beanie import Document, PydanticObjectId
from pydantic import BaseModel, Field


class Choix(BaseModel):
    id: PydanticObjectId = Field(default_factory=PydanticObjectId)
    texte: str


class Question(BaseModel):
    id: PydanticObjectId = Field(default_factory=PydanticObjectId)
    texte: str
    choix: list[Choix] = Field(min_length=2)


class Vote(BaseModel):
    participant_id: PydanticObjectId
    question_id: PydanticObjectId
    choix_id: PydanticObjectId
    date_creation: datetime = Field(default_factory=datetime.utcnow)


class SondageCreate(BaseModel):
    evenement_id: PydanticObjectId
    createur_id: PydanticObjectId
    questions: list[Question] = Field(min_length=1)


class SondageUpdate(BaseModel):
    questions: list[Question] | None = Field(default=None, min_length=1)


class VoteCreate(BaseModel):
    participant_id: PydanticObjectId
    question_id: PydanticObjectId
    choix_id: PydanticObjectId


class Sondage(Document):
    evenement_id: PydanticObjectId
    createur_id: PydanticObjectId
    questions: list[Question] = Field(min_length=1)
    votes: list[Vote] = Field(default_factory=list)

    class Settings:
        name = "sondages"

