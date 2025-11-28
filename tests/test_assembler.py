from src.ame_json.models.assembler.progressive_assembler import ProgressiveAssembler
from src.ame_json.models.computation import Computation
from tests.utils import (
    BaseUserProfile,
    UserWithAddress,
    UserAddress,
    UserProfile,
    UserWithLoyaltyScore,
    get_user_products_sync,
    calculate_loyalty_score_sync,
)


def test_one_layer_data():
    user_data = BaseUserProfile(
        user_id=101,
        username="jdoe",
        email="john.doe@example.com",
    )

    generator = user_data.to_streamer().stream()

    assembler = ProgressiveAssembler()

    data = assembler.assamble(generator)

    assert data == user_data.model_dump()


def test_user_with_address():
    user_data = UserWithAddress(
        user_id=101,
        username="jdoe",
        email="john.doe@example.com",
        address=UserAddress(street="123 Placeholder Dr", city="Streamington"),
    )

    generator = user_data.to_streamer().stream()

    assembler = ProgressiveAssembler()

    data = assembler.assamble(generator)

    assert data == user_data.model_dump()


def test_user_with_computation():
    user_data = UserWithLoyaltyScore(
        user_id=101,
        username="jdoe",
        email="john.doe@example.com",
        address=UserAddress(street="123 Placeholder Dr", city="Streamington"),
        loyalty_score=Computation(calculate_loyalty_score_sync),
    )

    generator = user_data.to_streamer().stream()

    assembler = ProgressiveAssembler()

    data = assembler.assamble(generator)

    assert data == user_data.model_dump()


def test_user_with_list():
    user_data = UserProfile(
        user_id=101,
        username="jdoe",
        email="john.doe@example.com",
        address=UserAddress(street="123 Placeholder Dr", city="Streamington"),
        products=Computation(get_user_products_sync),
        loyalty_score=Computation(calculate_loyalty_score_sync),
    )

    generator = user_data.to_streamer().stream()

    assembler = ProgressiveAssembler()

    data = assembler.assamble(generator)

    assert data == user_data.model_dump()
