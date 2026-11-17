from beanie import PydanticObjectId
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from src.auth import get_current_user
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
    dependencies=[Depends(get_current_user)],
)


@router.get(
    "/",
    summary="Lister les albums photo",
    description=(
        "Cette route retourne l'ensemble des albums photo enregistrés dans "
        "l'application. Chaque album est rattaché à un seul événement grâce à "
        "son champ `evenement_id`. La réponse contient également les photos "
        "publiées, l'identifiant de leur participant et les commentaires "
        "associés à chaque photo. Cette route ne modifie aucune donnée et "
        "retourne une liste vide lorsqu'aucun album n'est encore disponible."
    ),
)
async def list_albums() -> list[Album]:
    """Retourne tous les albums photo disponibles."""
    return await Album.find_all().to_list()


@router.get(
    "/{album_id}",
    summary="Consulter un album photo",
    description=(
        "Cette route recherche un album à partir de son identifiant MongoDB. "
        "Elle retourne l'identifiant de l'événement concerné, toutes les "
        "photos publiées dans l'album, les participants à l'origine de ces "
        "photos ainsi que les commentaires présents. L'identifiant doit être "
        "un ObjectId MongoDB valide. Une réponse 404 est retournée lorsque "
        "l'album demandé n'existe pas."
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
        "Cette route crée un nouvel album photo et l'associe à un événement "
        "avec le champ obligatoire `evenement_id`. L'album est créé vide : "
        "les photos seront ajoutées séparément avec la route "
        "`POST /albums/{album_id}/photos`. Le service retourne le document "
        "créé avec son identifiant MongoDB. Une réponse 201 confirme la "
        "création ; les données invalides sont rejetées par FastAPI."
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
        "Cette route modifie les informations autorisées d'un album existant. "
        "La mise à jour est partielle : seuls les champs fournis dans le corps "
        "de la requête sont appliqués et les autres restent inchangés. "
        "L'identifiant `album_id` désigne l'album à modifier. Une réponse 404 "
        "est retournée si cet album n'existe pas, puis le document mis à jour "
        "est renvoyé en cas de succès."
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
        "Cette route supprime définitivement l'album identifié par "
        "`album_id`. Les photos et les commentaires intégrés à cet album sont "
        "également supprimés puisqu'ils appartiennent au document de l'album. "
        "Aucune donnée n'est retournée lorsque la suppression réussit : le "
        "statut 204 confirme l'opération. Une réponse 404 est renvoyée si "
        "l'album n'existe pas."
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
        "Cette route ajoute une nouvelle photo dans l'album indiqué par "
        "`album_id`. Le champ `participant_id` identifie le participant qui "
        "publie la photo et `url` contient l'adresse de l'image. Une photo "
        "nouvellement créée ne possède aucun commentaire ; elle peut ensuite "
        "être commentée avec la route "
        "`POST /albums/{album_id}/photos/{photo_id}/commentaires`. Une "
        "réponse 404 est renvoyée si l'album n'existe pas."
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
        "Cette route ajoute un commentaire à une photo précise. "
        "`album_id` identifie l'album parent et `photo_id` doit correspondre "
        "à une photo effectivement présente dans cet album. Le corps de la "
        "requête contient l'identifiant de l'auteur et le contenu du "
        "commentaire. Une réponse 404 est renvoyée si l'album ou la photo "
        "n'existe pas ; une réponse 201 confirme la création du commentaire."
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
