from beanie import PydanticObjectId
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr
from pymongo.errors import DuplicateKeyError

from src.auth import create_access_token, hash_password, verify_password
from src.models.user import User


class RegisterRequest(BaseModel):
    nom: str
    email: EmailStr
    password: str
    role: str = "membre"


class UserResponse(BaseModel):
    id: PydanticObjectId
    nom: str
    email: EmailStr
    role: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Créer un compte",
    description="Crée un compte utilisateur public et hash le mot de passe avant son stockage.",
)
async def register(data: RegisterRequest) -> User:
    user = User(
        nom=data.nom,
        email=data.email,
        password=hash_password(data.password),
        role=data.role,
    )
    try:
        await user.insert()
    except DuplicateKeyError:
        raise HTTPException(status_code=409, detail="Cet email est déjà utilisé")
    return user


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Se connecter",
    description="Vérifie l'email et le mot de passe, puis retourne un token JWT Bearer.",
)
async def login(form_data: OAuth2PasswordRequestForm = Depends()) -> TokenResponse:
    user = await User.find_one(User.email == form_data.username)
    if user is None or not verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou mot de passe incorrect",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return TokenResponse(access_token=create_access_token(user.id))
