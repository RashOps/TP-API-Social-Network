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


@router.get("/")
async def list_albums() -> list[Album]:
    return await Album.find_all().to_list()


@router.get("/{album_id}")
async def get_album(album_id: PydanticObjectId) -> Album:
    album = await Album.get(album_id)
    if album is None:
        raise HTTPException(status_code=404, detail="Album introuvable")

    return album


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_album(data: AlbumCreate) -> Album:
    album = Album(**data.model_dump())
    await album.insert()
    return album


@router.patch("/{album_id}")
async def update_album(
    album_id: PydanticObjectId,
    data: AlbumUpdate,
) -> Album:
    album = await Album.get(album_id)
    if album is None:
        raise HTTPException(status_code=404, detail="Album introuvable")

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(album, field, value)

    await album.save()
    return album


@router.delete("/{album_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_album(album_id: PydanticObjectId) -> None:
    album = await Album.get(album_id)
    if album is None:
        raise HTTPException(status_code=404, detail="Album introuvable")

    await album.delete()


@router.post("/{album_id}/photos", status_code=status.HTTP_201_CREATED)
async def add_photo(
    album_id: PydanticObjectId,
    data: PhotoCreate,
) -> Photo:
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
)
async def add_photo_comment(
    album_id: PydanticObjectId,
    photo_id: PydanticObjectId,
    data: PhotoCommentaireCreate,
) -> PhotoCommentaire:
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
