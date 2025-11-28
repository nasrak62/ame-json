from collections.abc import Generator
from typing import Any
from pydantic import BaseModel

from ame_json.models.field_helper import send_completed_stream
from ame_json.models.progressive_streamer_context import ProgressiveStreamerContext
from ame_json.models.computation_utils import handle_computations
from ame_json.models.utils import handle_model
from ame_json.models.base_schema import (
    BaseProgressiveJSONStreamer,
    BaseProgressiveSchema,
)


class ProgressiveJSONStreamer(BaseProgressiveJSONStreamer):
    def __init__(self, schema_instance: BaseProgressiveSchema):
        if not isinstance(schema_instance, BaseProgressiveSchema):
            raise TypeError("Instance must be a ProgressiveSchema or inherit from it.")

        self.schema_instance = schema_instance
        self._computations: list[str] = []
        self._placeholder_mapper: dict[str, int] = {}
        self._placeholder_counter: int = 1
        self._layer_items = []
        self._completed_stream = False

        self.context = ProgressiveStreamerContext(
            placeholder_mapper=self._placeholder_mapper,
            get_counter_func=self.get_counter_func,
            update_counter_func=self.update_counter_func,
        )

    def add_computation(self, field_name: str):
        self._computations.append(field_name)
        self.add_placeholder(field_name)

    def add_placeholder(self, name: str):
        self._placeholder_mapper[name] = self._placeholder_counter
        self._placeholder_counter += 1

    def get_counter_func(self) -> int:
        return self._placeholder_counter

    def update_counter_func(self):
        self._placeholder_counter += 1

    def get_stream_completed_fun(self) -> bool:
        return self._completed_stream

    def handle_model(
        self, model: BaseModel, placeholder_value: str | None = None
    ) -> Generator[bytes, Any, None]:
        yield from handle_model(
            self._computations,
            self._layer_items,
            model,
            self.context,
            self.get_stream_completed_fun,
            placeholder_value=placeholder_value,
        )

    def stream(self) -> Generator[bytes, Any, None]:
        try:
            yield from self.handle_model(self.schema_instance)

            placeholder_value = None
            layer = 1

            while self._layer_items:
                current_data_model = None

                if self._layer_items:
                    current_data_model, placeholder_value = self._layer_items.pop(0)

                if current_data_model is not None:
                    yield from self.handle_model(current_data_model, placeholder_value)

                if self._computations:
                    yield from handle_computations(
                        self._computations,
                        self._layer_items,
                        self.get_stream_completed_fun,
                        self.context,
                    )

                layer += 1

            yield send_completed_stream()
        except Exception as e:
            print(f"Error stream: {e}")
