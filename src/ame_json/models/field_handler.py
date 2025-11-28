from typing import Any, cast
from pydantic import BaseModel

from src.ame_json.models.placeholder_utils import (
    handle_computation,
    handle_model_instance,
)

from src.ame_json.models.field_helper import (
    PRIMITIVES,
    is_computation,
    is_model,
)

from src.ame_json.models.progressive_streamer_context import ProgressiveStreamerContext


class FieldHandler:
    def __init__(
        self,
        new_computations: list,
        new_layers_items: list,
        context: ProgressiveStreamerContext,
    ):
        self.context = context
        self.new_computations = new_computations
        self.new_layers_items = new_layers_items

    def handle_field_by_value(
        self,
        field_name: str,
        model: BaseModel,
        value: Any,
    ):
        if is_computation(value):
            return handle_computation(
                field_name,
                model,
                self.new_computations,
                self.context,
            )

        if is_model(value):
            return handle_model_instance(
                field_name,
                self.new_layers_items,
                self.context,
                value,
            )

        if isinstance(value, list):
            return self.handle_iterable_field(
                field_name,
                model,
                value,
            )

        if isinstance(value, dict):
            return self.handle_dict_field(
                field_name,
                model,
                value,
            )

        return value

    def handle_iterable_field(
        self,
        field_name: str,
        model: BaseModel,
        value: list,
    ) -> list:
        new_value_list = []

        for inner_value in value:
            if isinstance(inner_value, PRIMITIVES):
                new_value_list.append(inner_value)

                continue

            if isinstance(inner_value, BaseModel):
                new_value = self.handle_field_by_value(
                    field_name,
                    model,
                    inner_value,
                )

                new_value_list.append(new_value)

                continue

            new_value_list.append(inner_value)

        return new_value_list

    def handle_dict_field(
        self,
        field_name: str,
        model: BaseModel,
        value: dict,
    ) -> dict:
        new_value_dict = {}

        for key, inner_value in value.items():
            if isinstance(inner_value, PRIMITIVES):
                new_value_dict[key] = inner_value

                continue

            if isinstance(inner_value, BaseModel):
                new_value = self.handle_field_by_value(
                    field_name,
                    model,
                    inner_value,
                )

                new_value_dict[key] = new_value

                continue

            new_value_dict[key] = inner_value

        return new_value_dict

    def handle_field(
        self,
        field_name: str,
        model: BaseModel,
    ) -> Any:
        try:
            value = cast(Any, getattr(model, field_name, None))

            return self.handle_field_by_value(field_name, model, value)
        except Exception as e:
            print(f"Error handle_field: {e}")
