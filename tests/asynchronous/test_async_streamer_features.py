import pytest
from tests.asynchronous.test_features_utils import (
    Emoji,
    Like,
    PostWithLikes,
    PostWithReactions,
    UserWithAddressAndCountry,
    AddressWithCountry,
    Country,
    Post,
    Comment,
)
from tests.asynchronous.utils import assert_as_json, assert_end_of_stream_async


@pytest.mark.asyncio
async def test_deeply_nested_model():
    user_data = UserWithAddressAndCountry(
        user_id=201,
        username="testuser",
        email="test@example.com",
        address=AddressWithCountry(
            street="456 Stream Ave",
            city="Testville",
            country=Country(name="Testland", code="TL"),
        ),
    )

    generator = user_data.to_streamer().stream()

    assert generator is not None

    # First chunk: base model with placeholder for address
    value = await anext(generator)
    expected = {
        "user_id": 201,
        "username": "testuser",
        "email": "test@example.com",
        "completed_stream": False,
        "address": "$1",
    }
    assert_as_json(value, expected)

    # Second chunk: address with placeholder for country
    value = await anext(generator)
    expected = {
        "$1": {
            "street": "456 Stream Ave",
            "city": "Testville",
            "country": "$2",
        },
        "completed_stream": False,
    }
    assert_as_json(value, expected)

    # Third chunk: country
    value = await anext(generator)
    expected = {
        "$2": {"name": "Testland", "code": "TL"},
        "completed_stream": False,
    }
    assert_as_json(value, expected)

    # End of stream
    await assert_end_of_stream_async(generator)


@pytest.mark.asyncio
async def test_list_of_models():
    post_data = Post(
        user_id=301,
        username="blogger",
        email="blogger@example.com",
        title="My new post",
        comments=[
            Comment(text="Great post!", author="reader1"),
            Comment(text="I agree!", author="reader2"),
        ],
    )

    generator = post_data.to_streamer().stream()

    assert generator is not None

    value = await anext(generator)
    expected = {
        "user_id": 301,
        "username": "blogger",
        "email": "blogger@example.com",
        "title": "My new post",
        "completed_stream": False,
        "comments": [
            "$1",
            "$2",
        ],
    }
    assert_as_json(value, expected)

    value = await anext(generator)

    expected = {
        "completed_stream": False,
        "$1": {"text": "Great post!", "author": "reader1"},
    }

    assert_as_json(value, expected)

    value = await anext(generator)

    expected = {
        "completed_stream": False,
        "$2": {"text": "I agree!", "author": "reader2"},
    }

    assert_as_json(value, expected)

    # End of stream
    await assert_end_of_stream_async(generator)


@pytest.mark.asyncio
async def test_dict():
    post_data = PostWithLikes(
        user_id=301,
        username="blogger",
        email="blogger@example.com",
        title="My new post",
        comments=[
            Comment(text="Great post!", author="reader1"),
            Comment(text="I agree!", author="reader2"),
        ],
        likes={
            "user1": 12,
            "user2": 13,
        },
    )

    generator = post_data.to_streamer().stream()

    assert generator is not None

    value = await anext(generator)
    expected = {
        "user_id": 301,
        "username": "blogger",
        "email": "blogger@example.com",
        "title": "My new post",
        "completed_stream": False,
        "comments": [
            "$1",
            "$2",
        ],
        "likes": {
            "user1": 12,
            "user2": 13,
        },
    }
    assert_as_json(value, expected)

    value = await anext(generator)

    expected = {
        "completed_stream": False,
        "$1": {"text": "Great post!", "author": "reader1"},
    }

    assert_as_json(value, expected)

    value = await anext(generator)

    expected = {
        "completed_stream": False,
        "$2": {"text": "I agree!", "author": "reader2"},
    }

    assert_as_json(value, expected)

    # End of stream
    await assert_end_of_stream_async(generator)


@pytest.mark.asyncio
async def test_dict_with_model():
    post_data = PostWithReactions(
        user_id=301,
        username="blogger",
        email="blogger@example.com",
        title="My new post",
        comments=[
            Comment(text="Great post!", author="reader1"),
            Comment(text="I agree!", author="reader2"),
        ],
        reactions={
            "user1": Like(username="test1234", score=12),
            "user2": Emoji(text="text", score=13),
        },
    )

    generator = post_data.to_streamer().stream()

    assert generator is not None

    value = await anext(generator)
    expected = {
        "user_id": 301,
        "username": "blogger",
        "email": "blogger@example.com",
        "title": "My new post",
        "completed_stream": False,
        "comments": [
            "$1",
            "$2",
        ],
        "reactions": {
            "user1": "$3",
            "user2": "$4",
        },
    }
    assert_as_json(value, expected)

    value = await anext(generator)

    expected = {
        "completed_stream": False,
        "$1": {"text": "Great post!", "author": "reader1"},
    }

    assert_as_json(value, expected)

    value = await anext(generator)

    expected = {
        "completed_stream": False,
        "$2": {"text": "I agree!", "author": "reader2"},
    }

    assert_as_json(value, expected)

    value = await anext(generator)

    expected = {
        "completed_stream": False,
        "$3": {"username": "test1234", "score": 12},
    }

    assert_as_json(value, expected)

    value = await anext(generator)

    expected = {
        "completed_stream": False,
        "$4": {"text": "text", "score": 13},
    }

    assert_as_json(value, expected)

    # End of stream
    await assert_end_of_stream_async(generator)
