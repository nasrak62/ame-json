from collections.abc import Callable, AsyncGenerator
from typing import Any
from pydantic import BaseModel
from ame_json.models.field_handler import FieldHandler
from ame_json.models.field_helper import get_field_list, prepare_data_str
from ame_json.models.progressive_streamer_context import ProgressiveStreamerContext


async def handle_model_iterable(
    computations: list,
    layer_items: list,
    model: BaseModel,
    context: ProgressiveStreamerContext,
) -> AsyncGenerator[dict, Any]:
    try:
        fields = get_field_list(model)
        new_computations = []
        new_layers_items = []
        data = {}

        for field_name in fields:
            field_handler = FieldHandler(new_computations, new_layers_items, context)

            data[field_name] = field_handler.handle_field(
                field_name,
                model,
            )

        yield data

        if new_computations:
            computations.extend(new_computations)

        if new_layers_items:
            layer_items.extend(new_layers_items)
    except Exception as e:
        print(f"Error handle_model: {e}")


async def handle_model(
    computations: list,
    layer_items: list,
    model: BaseModel,
    context: ProgressiveStreamerContext,
    get_stream_completed_fun: Callable[..., bool],
    placeholder_value: str | None = None,
) -> AsyncGenerator[bytes, Any]:
    try:
        fields = get_field_list(model)
        new_computations = []
        new_layers_items = []
        data = {}

        for field_name in fields:
            field_handler = FieldHandler(new_computations, new_layers_items, context)

            data[field_name] = field_handler.handle_field(field_name, model)

        effective_data = data

        if placeholder_value:
            effective_data = {placeholder_value: data}

        yield prepare_data_str(effective_data, get_stream_completed_fun)

        if new_computations:
            computations.extend(new_computations)

        if new_layers_items:
            layer_items.extend(new_layers_items)
    except Exception as e:
        print(f"Error handle_model: {e}")
