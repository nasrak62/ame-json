from pydantic import BaseModel
from tests.utils import BaseUserProfile, UserAddress


class Country(BaseModel):
    name: str
    code: str


class AddressWithCountry(UserAddress):
    country: Country


class UserWithAddressAndCountry(BaseUserProfile):
    address: AddressWithCountry


class Comment(BaseModel):
    text: str
    author: str


class Post(BaseUserProfile):
    title: str
    comments: list[Comment]


class PostWithLikes(BaseUserProfile):
    title: str
    comments: list[Comment]
    likes: dict[str, int]


class Like(BaseModel):
    username: str
    score: int


class Emoji(BaseModel):
    text: str
    score: int


class PostWithReactions(BaseUserProfile):
    title: str
    comments: list[Comment]
    reactions: dict[str, Like | Emoji]
