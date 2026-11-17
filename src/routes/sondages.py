from beanie import PydanticObjectId
from fastapi import APIRouter, HTTPException, status

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
)


@router.get("/")
async def list_sondages() -> list[Sondage]:
    return await Sondage.find_all().to_list()


@router.get("/{sondage_id}")
async def get_sondage(sondage_id: PydanticObjectId) -> Sondage:
    sondage = await Sondage.get(sondage_id)
    if sondage is None:
        raise HTTPException(status_code=404, detail="Sondage introuvable")

    return sondage


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_sondage(data: SondageCreate) -> Sondage:
    sondage = Sondage(**data.model_dump())
    await sondage.insert()
    return sondage


@router.patch("/{sondage_id}")
async def update_sondage(
    sondage_id: PydanticObjectId,
    data: SondageUpdate,
) -> Sondage:
    sondage = await Sondage.get(sondage_id)
    if sondage is None:
        raise HTTPException(status_code=404, detail="Sondage introuvable")

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(sondage, field, value)

    await sondage.save()
    return sondage


@router.delete("/{sondage_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_sondage(sondage_id: PydanticObjectId) -> None:
    sondage = await Sondage.get(sondage_id)
    if sondage is None:
        raise HTTPException(status_code=404, detail="Sondage introuvable")

    await sondage.delete()


@router.post("/{sondage_id}/votes", status_code=status.HTTP_201_CREATED)
async def vote(
    sondage_id: PydanticObjectId,
    data: VoteCreate,
) -> Vote:
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
