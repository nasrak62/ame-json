import json
import time


from ame_json.models.computation import Computation
from ame_json.models.progressive_schema import ProgressiveSchema
from pydantic import BaseModel


class Products(BaseModel):
    name: str
    price: float


# Mock data retrieval functions (now all synchronous, simulating Django)
def get_user_products_sync() -> list[Products]:
    """Simulates a slow, sync database call."""

    time.sleep(2)  # Simulate 2 seconds of work
    return list(
        map(
            lambda x: Products(name=x, price=0.0),
            ["Laptop Bag", "Monitor", "Mechanical Keyboard"],
        )
    )


def calculate_loyalty_score_sync() -> int:
    """Simulates a slower, sync external API call or heavy computation."""

    time.sleep(1)  # Simulate 1 second of work
    return 95


# The result type definition is just for type hinting, not used by the streamer logic


class UserAddress(BaseModel):
    """A regular nested Pydantic model (no streaming here)."""

    street: str
    city: str


class BaseUserProfile(ProgressiveSchema):
    user_id: int
    username: str
    email: str


class UserWithAddress(BaseUserProfile):
    address: UserAddress


class UserWithLoyaltyScore(UserWithAddress):
    loyalty_score: Computation[int]


class UserProfile(UserWithLoyaltyScore):
    products: Computation[list[Products]]


def assert_as_json(value: bytes, expected: dict):
    dict_value = json.loads(value.decode())

    assert dict_value == expected


def assert_end_of_stream(generator):
    value = next(generator)

    assert_as_json(value, {"completed_stream": True})
