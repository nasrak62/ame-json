import pytest
from ame_json.models.assembler.async_progressive_assembler import (
    AsyncProgressiveAssembler,
)
from ame_json.models.async_computation import AsyncComputation
from tests.asynchronous.utils import (
    BaseUserProfile,
    UserWithAddress,
    UserAddress,
    UserProfile,
    UserWithLoyaltyScore,
    get_user_products_async,
    calculate_loyalty_score_async,
)


@pytest.mark.asyncio
async def test_one_layer_data():
    user_data = BaseUserProfile(
        user_id=101,
        username="jdoe",
        email="john.doe@example.com",
    )

    generator = user_data.to_streamer().stream()

    assembler = AsyncProgressiveAssembler()

    data = await assembler.assamble(generator)

    assert data == user_data.model_dump()


@pytest.mark.asyncio
async def test_user_with_address():
    user_data = UserWithAddress(
        user_id=101,
        username="jdoe",
        email="john.doe@example.com",
        address=UserAddress(street="123 Placeholder Dr", city="Streamington"),
    )

    generator = user_data.to_streamer().stream()

    assembler = AsyncProgressiveAssembler()

    data = await assembler.assamble(generator)

    assert data == user_data.model_dump()


@pytest.mark.asyncio
async def test_user_with_computation():
    user_data = UserWithLoyaltyScore(
        user_id=101,
        username="jdoe",
        email="john.doe@example.com",
        address=UserAddress(street="123 Placeholder Dr", city="Streamington"),
        loyalty_score=AsyncComputation(calculate_loyalty_score_async),
    )

    generator = user_data.to_streamer().stream()

    assembler = AsyncProgressiveAssembler()

    data = await assembler.assamble(generator)
    user_model = await user_data.dumps()

    assert data == user_model


@pytest.mark.asyncio
async def test_user_with_list():
    user_data = UserProfile(
        user_id=101,
        username="jdoe",
        email="john.doe@example.com",
        address=UserAddress(street="123 Placeholder Dr", city="Streamington"),
        products=AsyncComputation(get_user_products_async),
        loyalty_score=AsyncComputation(calculate_loyalty_score_async),
    )

    generator = user_data.to_streamer().stream()

    assembler = AsyncProgressiveAssembler()

    data = await assembler.assamble(generator)
    user_model = await user_data.dumps()

    assert data == user_model
