from beanie import PydanticObjectId
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from src.models.album import (
    Album,
    AlbumCreate,
    AlbumUpdate,
    Photo,
    PhotoCommentaire,
)


class PhotoCreate(BaseModel):
    participant_id: PydanticObjectId
    url: str


class PhotoCommentaireCreate(BaseModel):
    auteur_id: PydanticObjectId
    contenu: str


router = APIRouter(
    prefix="/albums",
    tags=["Albums"],
)


@router.get(
    "/",
    summary="Lister les albums photo",
    description=(
        "Retourne tous les albums photo enregistrés dans l'application. "
        "Chaque album contient l'identifiant de son événement ainsi que la liste "
        "des photos et des commentaires associés."
    ),
)
async def list_albums() -> list[Album]:
    """Retourne tous les albums photo disponibles."""
    return await Album.find_all().to_list()


@router.get(
    "/{album_id}",
    summary="Consulter un album photo",
    description=(
        "Recherche un album à partir de son identifiant MongoDB et retourne "
        "son événement, ses photos, les participants qui les ont publiées et "
        "les commentaires présents sur chaque photo. "
        "Retourne 404 si l'album n'existe pas."
    ),
)
async def get_album(album_id: PydanticObjectId) -> Album:
    """Retourne un album et l'ensemble de ses photos et commentaires."""
    album = await Album.get(album_id)
    if album is None:
        raise HTTPException(status_code=404, detail="Album introuvable")

    return album


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    summary="Créer un album photo",
    description=(
        "Crée un album et l'associe à un événement grâce à `evenement_id`. "
        "Un album est initialement vide : les photos sont ajoutées ensuite "
        "avec la route dédiée. "
        "Retourne 201 lorsque l'album est créé."
    ),
)
async def create_album(data: AlbumCreate) -> Album:
    """Crée un album photo associé à un événement existant."""
    album = Album(**data.model_dump())
    await album.insert()
    return album


@router.patch(
    "/{album_id}",
    summary="Modifier un album photo",
    description=(
        "Met à jour les informations modifiables d'un album existant. "
        "Les champs absents de la requête restent inchangés. "
        "Retourne 404 si l'album demandé n'existe pas."
    ),
)
async def update_album(
    album_id: PydanticObjectId,
    data: AlbumUpdate,
) -> Album:
    """Modifie l'événement associé à un album photo."""
    album = await Album.get(album_id)
    if album is None:
        raise HTTPException(status_code=404, detail="Album introuvable")

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(album, field, value)

    await album.save()
    return album


@router.delete(
    "/{album_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Supprimer un album photo",
    description=(
        "Supprime définitivement l'album identifié ainsi que les photos et "
        "commentaires qu'il contient. "
        "Retourne 404 si l'album n'existe pas et 204 en cas de succès."
    ),
)
async def delete_album(album_id: PydanticObjectId) -> None:
    """Supprime un album ainsi que ses photos et commentaires intégrés."""
    album = await Album.get(album_id)
    if album is None:
        raise HTTPException(status_code=404, detail="Album introuvable")

    await album.delete()


@router.post(
    "/{album_id}/photos",
    status_code=status.HTTP_201_CREATED,
    summary="Ajouter une photo à un album",
    description=(
        "Ajoute une photo dans un album existant. Le champ `participant_id` "
        "identifie le participant qui publie la photo et `url` contient son "
        "emplacement. Une photo est créée sans commentaire et peut ensuite "
        "être commentée avec la route dédiée."
    ),
)
async def add_photo(
    album_id: PydanticObjectId,
    data: PhotoCreate,
) -> Photo:
    """Ajoute une photo à un album pour un participant de l'événement."""
    album = await Album.get(album_id)
    if album is None:
        raise HTTPException(status_code=404, detail="Album introuvable")

    photo = Photo(**data.model_dump())
    album.photos.append(photo)
    await album.save()
    return photo


@router.post(
    "/{album_id}/photos/{photo_id}/commentaires",
    status_code=status.HTTP_201_CREATED,
    summary="Commenter une photo",
    description=(
        "Ajoute un commentaire à une photo précise d'un album. "
        "L'identifiant `photo_id` doit correspondre à une photo présente dans "
        "l'album indiqué. Retourne 404 si l'album ou la photo est introuvable."
    ),
)
async def add_photo_comment(
    album_id: PydanticObjectId,
    photo_id: PydanticObjectId,
    data: PhotoCommentaireCreate,
) -> PhotoCommentaire:
    """Ajoute un commentaire sur une photo existante de l'album."""
    album = await Album.get(album_id)
    if album is None:
        raise HTTPException(status_code=404, detail="Album introuvable")

    photo = next(
        (photo for photo in album.photos if photo.id == photo_id),
        None,
    )
    if photo is None:
        raise HTTPException(status_code=404, detail="Photo introuvable")

    commentaire = PhotoCommentaire(**data.model_dump())
    photo.commentaires.append(commentaire)
    await album.save()
    return commentaire
