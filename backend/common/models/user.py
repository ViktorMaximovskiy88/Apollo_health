from typing import Optional

from beanie import Indexed, PydanticObjectId
from pydantic import EmailStr, Field

from backend.common.models.base_document import BaseDocument, BaseModel


class NewUser(BaseModel):
    email: EmailStr
    full_name: str
    roles: list[str] | None = None
    is_admin: bool | None = None


class UserUpdate(BaseModel):
    email: EmailStr | None = None
    full_name: str | None = None
    roles: list[str] | None = None
    is_admin: bool | None = None
    disabled: bool | None = None


class UserPublic(UserUpdate):
    id: PydanticObjectId = Field(..., alias="_id")
    email: Indexed(EmailStr, unique=True)  # type: ignore
    full_name: str
    disabled: bool = False
    is_admin: bool = False
    roles: list[str] = []


class User(BaseDocument, UserPublic):
    hashed_password: str | None = ""

    @classmethod
    async def by_email(cls, email: str) -> Optional["User"]:
        return await cls.find_one({"email": {"$regex": rf"^{email}$", "$options": "-i"}})

    @classmethod
    async def get_api_user(cls) -> Optional["User"]:
        return await cls.find_one({"email": "api@mmitnetwork.com"})

    @classmethod
    async def get_admin_user(cls) -> Optional["User"]:
        return await cls.find_one({"email": "admin@mmitnetwork.com"})
