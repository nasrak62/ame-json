from collections.abc import Generator
from typing import Any, Callable

from pydantic import BaseModel

from src.models.utils import handle_model_iterable, prepare_data_str

from src.models.progressive_streamer_context import ProgressiveStreamerContext


def handle_list_generator(
    value_list: list[BaseModel],
    computations: list,
    layer_items: list,
    context: ProgressiveStreamerContext,
):
    results = []

    for value in value_list:
        generator = handle_model_iterable(
            computations,
            layer_items,
            value,
            context,
        )

        result_list = [v for v in generator]

        results.extend(result_list)

    return results


def handle_computations(
    computations: list,
    layer_items: list,
    get_stream_completed_fun: Callable[..., bool],
    context: ProgressiveStreamerContext,
) -> Generator[bytes, Any, None]:
    new_layers = []

    while computations:
        field_name, value = computations.pop(0)
        placeholder_value = "$" + str(context.placeholder_mapper[field_name])
        result = value.run_sync()

        if isinstance(result, list):
            result_list = handle_list_generator(
                result,
                computations,
                layer_items,
                context,
            )

            yield prepare_data_str(
                {placeholder_value: result_list}, get_stream_completed_fun
            )

            continue

        if isinstance(result, BaseModel):
            new_layers.append((result, placeholder_value))

            continue

        yield prepare_data_str({placeholder_value: result}, get_stream_completed_fun)

    layer_items.extend(new_layers)
