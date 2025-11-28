from collections.abc import Coroutine
from pydantic import SerializationInfo
from pydantic_core import core_schema

from typing import Any, Callable


type ComputationFunction[R] = Callable[..., Coroutine[Any, Any, R]]


class AsyncComputation[R]:
    def __init__(self, func: ComputationFunction[R], func_kwargs: dict | None = None):
        self.func = func
        self.func_kwargs = func_kwargs or {}

    def __repr__(self):
        return f"<AsyncComputation func={self.func.__name__}>"

    async def __pydantic_async_serializer__(
        self,
        _instance: Any,
        _info: SerializationInfo,
    ) -> R:
        return await self.run()

    @classmethod
    def __get_pydantic_core_schema__(
        cls, source: Any, handler: Any
    ) -> core_schema.CoreSchema:
        instance_schema = core_schema.is_instance_schema(AsyncComputation)

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

    async def _serialize(self):
        return await self.run()

    async def run(self) -> R:
        return await self.func(**self.func_kwargs)
