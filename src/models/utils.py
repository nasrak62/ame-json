from collections.abc import Callable, Generator
import json
from typing import Any, cast
from pydantic import BaseModel

from src.models.progressive_streamer_context import ProgressiveStreamerContext
from src.models.computation import Computation


def is_computation(value: Any) -> bool:
    return isinstance(value, Computation)


def get_field_list(model: BaseModel):
    return list(model.__class__.model_fields.keys())


def add_placeholder(
    name: str,
    context: ProgressiveStreamerContext,
):
    context.placeholder_mapper[name] = context.get_counter_func()
    context.update_counter_func()


def add_computation(
    field_name: str,
    model: BaseModel,
    computations: list,
    context: ProgressiveStreamerContext,
):
    value: Computation = cast(Computation, getattr(model, field_name, None))
    computations.append((field_name, value))

    add_placeholder(field_name, context)


def prepare_data_str(
    data: dict, get_stream_completed_fun: Callable[..., bool]
) -> bytes:
    data["completed_stream"] = get_stream_completed_fun()

    data_json = json.dumps(data)

    return data_json.encode("utf-8")


def send_completed_stream() -> bytes:
    data_json = json.dumps(
        {
            "completed_stream": True,
        }
    )

    return data_json.encode("utf-8")


def handle_field(
    field_name: str,
    model: BaseModel,
    new_computations: list,
    new_layers_items: list,
    context: ProgressiveStreamerContext,
):
    try:
        value = cast(Any, getattr(model, field_name, None))

        if is_computation(value):
            add_computation(
                field_name,
                model,
                new_computations,
                context,
            )

            return "$" + str(context.placeholder_mapper[field_name])

        if isinstance(value, BaseModel):
            add_placeholder(field_name, context)

            placeholder_value = "$" + str(context.placeholder_mapper[field_name])

            new_layers_items.append((value, placeholder_value))

            return placeholder_value

        return value

    except Exception as e:
        print(f"Error handle_field: {e}")


def handle_model_iterable(
    computations: list,
    layer_items: list,
    model: BaseModel,
    context: ProgressiveStreamerContext,
) -> Generator[dict, Any, None]:
    try:
        fields = get_field_list(model)
        new_computations = []
        new_layers_items = []
        data = {}

        for field_name in fields:
            data[field_name] = handle_field(
                field_name,
                model,
                new_computations,
                new_layers_items,
                context,
            )

        yield data

        if new_computations:
            computations.extend(new_computations)

        if new_layers_items:
            layer_items.extend(new_layers_items)
    except Exception as e:
        print(f"Error handle_model: {e}")


def handle_model(
    computations: list,
    layer_items: list,
    model: BaseModel,
    context: ProgressiveStreamerContext,
    get_stream_completed_fun: Callable[..., bool],
    placeholder_value: str | None = None,
) -> Generator[bytes, Any, None]:
    try:
        fields = get_field_list(model)
        new_computations = []
        new_layers_items = []
        data = {}

        for field_name in fields:
            data[field_name] = handle_field(
                field_name,
                model,
                new_computations,
                new_layers_items,
                context,
            )

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
