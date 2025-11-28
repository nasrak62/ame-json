import pytest
from ame_json.models.async_computation import AsyncComputation
from tests.asynchronous.utils import (
    BaseUserProfile,
    assert_as_json,
    assert_end_of_stream_async,
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

    assert generator is not None

    expected = {
        "user_id": 101,
        "username": "jdoe",
        "email": "john.doe@example.com",
        "completed_stream": False,
    }
    first_value = await anext(generator)

    assert_as_json(first_value, expected)

    await assert_end_of_stream_async(generator)


@pytest.mark.asyncio
async def test_user_with_address():
    user_data = UserWithAddress(
        user_id=101,
        username="jdoe",
        email="john.doe@example.com",
        address=UserAddress(street="123 Placeholder Dr", city="Streamington"),
    )

    generator = user_data.to_streamer().stream()

    assert generator is not None

    value = await anext(generator)

    expected = {
        "user_id": 101,
        "username": "jdoe",
        "email": "john.doe@example.com",
        "completed_stream": False,
        "address": "$1",
    }

    assert_as_json(value, expected)

    value = await anext(generator)

    expected = {
        "$1": {"street": "123 Placeholder Dr", "city": "Streamington"},
        "completed_stream": False,
    }

    assert_as_json(value, expected)

    await assert_end_of_stream_async(generator)


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

    assert generator is not None

    value = await anext(generator)

    expected = {
        "user_id": 101,
        "username": "jdoe",
        "email": "john.doe@example.com",
        "completed_stream": False,
        "address": "$1",
        "loyalty_score": "$2",
    }

    assert_as_json(value, expected)

    value = await anext(generator)

    expected = {
        "$1": {"street": "123 Placeholder Dr", "city": "Streamington"},
        "completed_stream": False,
    }

    assert_as_json(value, expected)

    expected = {
        "$2": 95,
        "completed_stream": False,
    }

    value = await anext(generator)

    assert_as_json(value, expected)

    await assert_end_of_stream_async(generator)


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

    assert generator is not None

    value = await anext(generator)

    expected = {
        "user_id": 101,
        "username": "jdoe",
        "email": "john.doe@example.com",
        "completed_stream": False,
        "address": "$1",
        "products": "$3",
        "loyalty_score": "$2",
    }

    assert_as_json(value, expected)

    value = await anext(generator)

    expected = {
        "$1": {"street": "123 Placeholder Dr", "city": "Streamington"},
        "completed_stream": False,
    }

    assert_as_json(value, expected)

    expected = {
        "$2": 95,
        "completed_stream": False,
    }

    value = await anext(generator)

    assert_as_json(value, expected)

    expected = {
        "$3": [
            {"name": "Laptop Bag", "price": 0.0},
            {"name": "Monitor", "price": 0.0},
            {"name": "Mechanical Keyboard", "price": 0.0},
        ],
        "completed_stream": False,
    }

    value = await anext(generator)

    assert_as_json(value, expected)

    await assert_end_of_stream_async(generator)
