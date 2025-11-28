from typing import Any
from pydantic import BaseModel

from ame_json.models.field_helper import (
    add_computation,
    add_placeholder,
)
from ame_json.models.progressive_streamer_context import ProgressiveStreamerContext


def handle_computation(
    field_name: str,
    model: BaseModel,
    new_computations: list,
    context: ProgressiveStreamerContext,
) -> str:
    add_computation(
        field_name,
        model,
        new_computations,
        context,
    )

    return "$" + str(context.placeholder_mapper[field_name])


def handle_model_instance(
    field_name: str,
    new_layers_items: list,
    context: ProgressiveStreamerContext,
    value: Any,
) -> str:
    add_placeholder(field_name, context)

    placeholder_value = "$" + str(context.placeholder_mapper[field_name])

    new_layers_items.append((value, placeholder_value))

    return placeholder_value
