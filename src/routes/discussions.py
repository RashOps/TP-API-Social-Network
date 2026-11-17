from beanie import PydanticObjectId
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from src.models.discussion import (
    Commentaire,
    Discussion,
    DiscussionCreate,
    DiscussionUpdate,
    Message,
)


class MessageCreate(BaseModel):
    auteur_id: PydanticObjectId
    contenu: str


class CommentaireCreate(BaseModel):
    auteur_id: PydanticObjectId
    contenu: str


router = APIRouter(
    prefix="/discussions",
    tags=["Discussions"],
)


@router.get("/")
async def list_discussions() -> list[Discussion]:
    return await Discussion.find_all().to_list()


@router.get("/{discussion_id}")
async def get_discussion(discussion_id: PydanticObjectId) -> Discussion:
    discussion = await Discussion.get(discussion_id)
    if discussion is None:
        raise HTTPException(status_code=404, detail="Discussion introuvable")

    return discussion


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_discussion(data: DiscussionCreate) -> Discussion:
    discussion = Discussion(**data.model_dump())
    await discussion.insert()
    return discussion


@router.patch("/{discussion_id}")
async def update_discussion(
    discussion_id: PydanticObjectId,
    data: DiscussionUpdate,
) -> Discussion:
    discussion = await Discussion.get(discussion_id)
    if discussion is None:
        raise HTTPException(status_code=404, detail="Discussion introuvable")

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(discussion, field, value)

    await discussion.save()
    return discussion


@router.delete("/{discussion_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_discussion(discussion_id: PydanticObjectId) -> None:
    discussion = await Discussion.get(discussion_id)
    if discussion is None:
        raise HTTPException(status_code=404, detail="Discussion introuvable")

    await discussion.delete()


@router.post("/{discussion_id}/messages", status_code=status.HTTP_201_CREATED)
async def add_message(
    discussion_id: PydanticObjectId,
    data: MessageCreate,
) -> Message:
    discussion = await Discussion.get(discussion_id)
    if discussion is None:
        raise HTTPException(status_code=404, detail="Discussion introuvable")

    message = Message(**data.model_dump())
    discussion.messages.append(message)
    await discussion.save()
    return message


@router.post(
    "/{discussion_id}/messages/{message_id}/commentaires",
    status_code=status.HTTP_201_CREATED,
)
async def add_comment(
    discussion_id: PydanticObjectId,
    message_id: PydanticObjectId,
    data: CommentaireCreate,
) -> Commentaire:
    discussion = await Discussion.get(discussion_id)
    if discussion is None:
        raise HTTPException(status_code=404, detail="Discussion introuvable")

    message = next(
        (message for message in discussion.messages if message.id == message_id),
        None,
    )
    if message is None:
        raise HTTPException(status_code=404, detail="Message introuvable")

    commentaire = Commentaire(**data.model_dump())
    message.commentaires.append(commentaire)
    await discussion.save()
    return commentaire
