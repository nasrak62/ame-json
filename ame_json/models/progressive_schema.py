from collections.abc import Iterable
from typing import Any

from pydantic import BaseModel
from ame_json.models.field_helper import PRIMITIVES
from ame_json.models.async_computation import AsyncComputation
from ame_json.models.async_progressive_streamer import AsyncProgressiveJSONStreamer
from ame_json.models.progressive_streamer import ProgressiveJSONStreamer
from ame_json.models.base_schema import BaseProgressiveSchema
from ame_json.models.async_base_schema import AsyncBaseProgressiveSchema


class ProgressiveSchema(BaseProgressiveSchema):
    def to_streamer(self) -> ProgressiveJSONStreamer:
        return ProgressiveJSONStreamer(self)


class AsyncProgressiveSchema(AsyncBaseProgressiveSchema):
    def _handle_nested_field(self, value: Any) -> Any:
        if isinstance(value, PRIMITIVES):
            return value

        if isinstance(value, BaseModel):
            return self._handle_nested_field(value.model_dump())

        if isinstance(value, dict):
            keys = list(value.keys())

            for inner_key in keys:
                value[inner_key] = self._handle_nested_field(value[inner_key])

            return value

        if isinstance(value, Iterable):
            new_values = []

            for inner_value in value:
                new_value = self._handle_nested_field(inner_value)
                new_values.append(new_value)

            return new_values

    async def dumps(self) -> dict:
        data = {}
        dump_data = self.model_dump()

        for key, value in dump_data.items():
            if not isinstance(value, AsyncComputation):
                data[key] = value

                continue

            result = await value.run()

            data[key] = self._handle_nested_field(result)

        return data

    def to_streamer(self) -> AsyncProgressiveJSONStreamer:
        return AsyncProgressiveJSONStreamer(self)
