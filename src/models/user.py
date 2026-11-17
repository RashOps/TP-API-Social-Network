from beanie import Document, Indexed
from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    nom: str
    email: EmailStr
    password: str
    role: str


class UserUpdate(BaseModel):
    nom: str | None = None
    email: EmailStr | None = None
    password: str | None = None
    role: str | None = None


class User(Document):
    nom: str
    email: Indexed(EmailStr, unique=True)
    password: str
    role: str

    class Settings:
        name = "users"