from pydantic import SerializationInfo
from pydantic_core import core_schema

from typing import Any, Callable


type ComputationFunction[R] = Callable[..., R]


class Computation[R]:
    def __init__(self, func: ComputationFunction[R], func_kwargs: dict | None = None):
        self.func = func
        self.func_kwargs = func_kwargs or {}

    def __repr__(self):
        return f"<Computation func={self.func.__name__}>"

    def __pydantic_serializer__(
        self,
        _instance: Any,  # Pydantic passes the instance (self) here
        _info: SerializationInfo,
    ) -> R:
        return self.run()

    @classmethod
    def __get_pydantic_core_schema__(
        cls, source: Any, handler: Any
    ) -> core_schema.CoreSchema:
        instance_schema = core_schema.is_instance_schema(Computation)

        callable_coercion_schema = core_schema.no_info_after_validator_function(
            lambda v: cls(v),
            core_schema.callable_schema(),
            serialization=core_schema.plain_serializer_function_ser_schema(
                cls._serialize,
                info_arg=False,
                return_schema=core_schema.any_schema(),
            ),
        )

        return core_schema.union_schema(
            [
                instance_schema,
                callable_coercion_schema,
            ]
        )

    def _serialize(self):
        return self.run()

    def run(self) -> R:
        return self.func(**self.func_kwargs)
