from pydantic import BaseModel

from collections.abc import Callable
import json
from typing import Any, cast

from src.ame_json.models.progressive_streamer_context import ProgressiveStreamerContext
from src.ame_json.models.computation import Computation
from src.ame_json.models.async_computation import AsyncComputation


PRIMITIVES = (str, int, float, bool, complex, bytes, bytearray, type(None))


def is_computation(value: Any) -> bool:
    return isinstance(value, (Computation, AsyncComputation))


def is_model(value: Any) -> bool:
    return isinstance(value, BaseModel)


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
