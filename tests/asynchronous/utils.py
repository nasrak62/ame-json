import asyncio
import json

from src.ame_json.models.async_computation import AsyncComputation
from src.ame_json.models.progressive_schema import AsyncProgressiveSchema
from pydantic import BaseModel


class Products(BaseModel):
    name: str
    price: float


# Mock data retrieval functions (now all synchronous, simulating Django)
async def get_user_products_async() -> list[Products]:
    """Simulates a slow, sync database call."""

    await asyncio.sleep(0.02)  # Simulate 2 seconds of work
    return list(
        map(
            lambda x: Products(name=x, price=0.0),
            ["Laptop Bag", "Monitor", "Mechanical Keyboard"],
        )
    )


async def calculate_loyalty_score_async() -> int:
    """Simulates a slower, sync external API call or heavy computation."""

    await asyncio.sleep(0.01)  # Simulate 1 second of work
    return 95


# The result type definition is just for type hinting, not used by the streamer logic


class UserAddress(BaseModel):
    """A regular nested Pydantic model (no streaming here)."""

    street: str
    city: str


class BaseUserProfile(AsyncProgressiveSchema):
    user_id: int
    username: str
    email: str


class UserWithAddress(BaseUserProfile):
    address: UserAddress


class UserWithLoyaltyScore(UserWithAddress):
    loyalty_score: AsyncComputation[int]


class UserProfile(UserWithLoyaltyScore):
    products: AsyncComputation[list[Products]]


def assert_as_json(value: bytes, expected: dict):
    dict_value = json.loads(value.decode())

    assert dict_value == expected


async def assert_end_of_stream_async(generator):
    value = await anext(generator)

    assert_as_json(value, {"completed_stream": True})
