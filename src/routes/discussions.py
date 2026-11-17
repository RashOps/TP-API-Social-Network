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


@router.get(
    "/",
    summary="Lister les fils de discussion",
    description="Retourne les fils liés aux groupes ou aux événements, avec leurs messages et commentaires.",
)
async def list_discussions() -> list[Discussion]:
    """Retourne tous les fils liés aux groupes ou aux événements."""
    return await Discussion.find_all().to_list()


@router.get(
    "/{discussion_id}",
    summary="Consulter un fil",
    description="Retourne un fil complet à partir de son identifiant. Retourne 404 s'il n'existe pas.",
)
async def get_discussion(discussion_id: PydanticObjectId) -> Discussion:
    """Retourne un fil avec ses messages et commentaires."""
    discussion = await Discussion.get(discussion_id)
    if discussion is None:
        raise HTTPException(status_code=404, detail="Discussion introuvable")

    return discussion


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    summary="Créer un fil de discussion",
    description="Crée un fil lié à un groupe ou à un événement, mais jamais aux deux simultanément.",
)
async def create_discussion(data: DiscussionCreate) -> Discussion:
    """Crée un fil lié à un groupe ou à un événement, mais jamais aux deux."""
    discussion = Discussion(**data.model_dump())
    await discussion.insert()
    return discussion


@router.patch(
    "/{discussion_id}",
    summary="Modifier un fil",
    description="Met à jour les messages d'un fil existant. Retourne 404 si le fil est introuvable.",
)
async def update_discussion(
    discussion_id: PydanticObjectId,
    data: DiscussionUpdate,
) -> Discussion:
    """Remplace les messages d'un fil existant."""
    discussion = await Discussion.get(discussion_id)
    if discussion is None:
        raise HTTPException(status_code=404, detail="Discussion introuvable")

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(discussion, field, value)

    await discussion.save()
    return discussion


@router.delete(
    "/{discussion_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Supprimer un fil",
    description="Supprime le fil et les messages et commentaires qu'il contient.",
)
async def delete_discussion(discussion_id: PydanticObjectId) -> None:
    """Supprime un fil ainsi que ses messages et commentaires."""
    discussion = await Discussion.get(discussion_id)
    if discussion is None:
        raise HTTPException(status_code=404, detail="Discussion introuvable")

    await discussion.delete()


@router.post(
    "/{discussion_id}/messages",
    status_code=status.HTTP_201_CREATED,
    summary="Publier un message",
    description="Ajoute un message à un fil existant et l'associe à son auteur.",
)
async def add_message(
    discussion_id: PydanticObjectId,
    data: MessageCreate,
) -> Message:
    """Publie un nouveau message dans un fil de discussion."""
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
    summary="Commenter un message",
    description="Ajoute un commentaire au message indiqué. Retourne 404 si le fil ou le message n'existe pas.",
)
async def add_comment(
    discussion_id: PydanticObjectId,
    message_id: PydanticObjectId,
    data: CommentaireCreate,
) -> Commentaire:
    """Ajoute un commentaire sur un message existant."""
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
