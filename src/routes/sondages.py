from beanie import PydanticObjectId
from fastapi import APIRouter, Depends, HTTPException, status

from src.auth import get_current_user
from src.models.sondage import (
    Sondage,
    SondageCreate,
    SondageUpdate,
    Vote,
    VoteCreate,
)


router = APIRouter(
    prefix="/sondages",
    tags=["Sondages"],
    dependencies=[Depends(get_current_user)],
)


@router.get(
    "/",
    summary="Lister les sondages",
    description=(
        "Retourne tous les sondages avec leur événement, leur créateur, leurs "
        "questions, les choix disponibles et les votes enregistrés. Cette "
        "route permet de consulter les résultats sans modifier les réponses."
    ),
)
async def list_sondages() -> list[Sondage]:
    """Retourne tous les sondages créés pour les événements."""
    return await Sondage.find_all().to_list()


@router.get(
    "/{sondage_id}",
    summary="Consulter un sondage",
    description=(
        "Retourne le sondage identifié par `sondage_id`, ses questions, ses "
        "choix et les votes déjà enregistrés. Retourne 404 lorsque le sondage "
        "n'existe pas."
    ),
)
async def get_sondage(sondage_id: PydanticObjectId) -> Sondage:
    """Retourne un sondage avec ses questions, choix et votes."""
    sondage = await Sondage.get(sondage_id)
    if sondage is None:
        raise HTTPException(status_code=404, detail="Sondage introuvable")

    return sondage


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    summary="Créer un sondage",
    description=(
        "Crée un sondage associé à un événement et à son créateur. Le sondage "
        "doit contenir au moins une question et chaque question doit proposer "
        "au moins deux choix. Les votes sont ajoutés ultérieurement par la "
        "route dédiée et le statut 201 confirme la création."
    ),
)
async def create_sondage(data: SondageCreate) -> Sondage:
    """Crée un sondage avec au moins une question et deux choix par question."""
    sondage = Sondage(**data.model_dump())
    await sondage.insert()
    return sondage


@router.patch(
    "/{sondage_id}",
    summary="Modifier un sondage",
    description=(
        "Met à jour les questions d'un sondage existant. La nouvelle liste "
        "doit toujours contenir au moins une question avec plusieurs choix ; "
        "l'événement et le créateur du sondage restent inchangés."
    ),
)
async def update_sondage(
    sondage_id: PydanticObjectId,
    data: SondageUpdate,
) -> Sondage:
    """Modifie les questions d'un sondage existant."""
    sondage = await Sondage.get(sondage_id)
    if sondage is None:
        raise HTTPException(status_code=404, detail="Sondage introuvable")

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(sondage, field, value)

    await sondage.save()
    return sondage


@router.delete(
    "/{sondage_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Supprimer un sondage",
    description=(
        "Supprime définitivement un sondage et les votes stockés avec celui-ci. "
        "La réponse 204 ne contient aucun document ; une réponse 404 indique "
        "que le sondage demandé n'existe pas."
    ),
)
async def delete_sondage(sondage_id: PydanticObjectId) -> None:
    """Supprime un sondage et les votes qui lui sont associés."""
    sondage = await Sondage.get(sondage_id)
    if sondage is None:
        raise HTTPException(status_code=404, detail="Sondage introuvable")

    await sondage.delete()


@router.post(
    "/{sondage_id}/votes",
    status_code=status.HTTP_201_CREATED,
    summary="Répondre à une question",
    description=(
        "Enregistre le choix d'un participant pour une question précise. "
        "Le choix doit appartenir à la question ciblée et un même participant "
        "ne peut répondre qu'une seule fois à cette question. Une question ou "
        "un choix inconnu provoque une erreur et un vote déjà enregistré "
        "retourne 409."
    ),
)
async def vote(
    sondage_id: PydanticObjectId,
    data: VoteCreate,
) -> Vote:
    """Enregistre le choix d'un participant pour une question."""
    sondage = await Sondage.get(sondage_id)
    if sondage is None:
        raise HTTPException(status_code=404, detail="Sondage introuvable")

    question = next(
        (question for question in sondage.questions if question.id == data.question_id),
        None,
    )
    if question is None:
        raise HTTPException(status_code=404, detail="Question introuvable")

    if not any(choix.id == data.choix_id for choix in question.choix):
        raise HTTPException(status_code=400, detail="Choix invalide pour cette question")

    already_voted = any(
        vote.participant_id == data.participant_id
        and vote.question_id == data.question_id
        for vote in sondage.votes
    )
    if already_voted:
        raise HTTPException(
            status_code=409,
            detail="Le participant a déjà répondu à cette question",
        )

    new_vote = Vote(**data.model_dump())
    sondage.votes.append(new_vote)
    await sondage.save()
    return new_vote
