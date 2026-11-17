from beanie import PydanticObjectId
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from src.auth import get_current_user
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
    dependencies=[Depends(get_current_user)],
)


@router.get(
    "/",
    summary="Lister les fils de discussion",
    description=(
        "Retourne tous les fils de discussion enregistrés. Chaque fil est "
        "rattaché soit à un groupe, soit à un événement, et contient ses "
        "messages ainsi que les commentaires associés. Une liste vide est "
        "retournée lorsqu'aucun fil n'existe."
    ),
)
async def list_discussions() -> list[Discussion]:
    """Retourne tous les fils liés aux groupes ou aux événements."""
    return await Discussion.find_all().to_list()


@router.get(
    "/{discussion_id}",
    summary="Consulter un fil",
    description=(
        "Retourne un fil complet à partir de `discussion_id`, avec son "
        "rattachement, ses messages, leurs auteurs et leurs commentaires. "
        "Retourne 404 si le fil demandé n'existe pas."
    ),
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
    description=(
        "Crée un fil de discussion vide lié à un seul contexte fonctionnel. "
        "Le corps doit fournir soit `groupe_id`, soit `evenement_id` ; fournir "
        "les deux ou aucun des deux est refusé par la validation. Les messages "
        "seront ajoutés par la route dédiée."
    ),
)
async def create_discussion(data: DiscussionCreate) -> Discussion:
    """Crée un fil lié à un groupe ou à un événement, mais jamais aux deux."""
    discussion = Discussion(**data.model_dump())
    await discussion.insert()
    return discussion


@router.patch(
    "/{discussion_id}",
    summary="Modifier un fil",
    description=(
        "Met à jour la liste des messages d'un fil existant. Les messages "
        "fournis remplacent la liste actuelle ; le rattachement au groupe ou "
        "à l'événement reste inchangé. Retourne 404 si le fil est introuvable."
    ),
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
    description=(
        "Supprime définitivement le fil identifié par `discussion_id`, ainsi "
        "que les messages et commentaires qu'il contient. Retourne 204 sans "
        "contenu en cas de succès et 404 si le fil n'existe pas."
    ),
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
    description=(
        "Ajoute un message à un fil existant. Le corps indique l'auteur et le "
        "contenu du message ; sa date et son identifiant sont générés par "
        "l'application. Le message est créé sans commentaire et un retour 404 "
        "est produit si le fil est introuvable."
    ),
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
    description=(
        "Ajoute un commentaire au message identifié par `message_id` dans le "
        "fil `discussion_id`. Le commentaire contient l'auteur et son contenu. "
        "Le fil et le message doivent exister ; sinon une réponse 404 est "
        "retournée. Le statut 201 confirme l'ajout."
    ),
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
