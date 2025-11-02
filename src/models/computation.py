from collections.abc import Coroutine
import inspect
from pydantic import SerializationInfo
from pydantic_core import core_schema

from typing import Any, Callable, cast


type SyncComputation[R] = Callable[..., R]
type AsyncComputation[R] = Callable[..., Coroutine[Any, Any, R]]
type ComputationFunction[R] = SyncComputation[R] | AsyncComputation[R]


class Computation[R]:
    def __init__(self, func: ComputationFunction[R], func_kwargs: dict | None = None):
        self.func = func
        self.func_kwargs = func_kwargs or {}
        self.is_async = inspect.iscoroutinefunction(func)

    def __repr__(self):
        return f"<Computation func={self.func.__name__}, async={self.is_async}>"

    def __pydantic_serializer__(
        self,
        _instance: Any,  # Pydantic passes the instance (self) here
        _info: SerializationInfo,
    ) -> R:
        if self.is_async:
            raise ValueError(
                "Cannot serialize an async Computation synchronously "
                "via model_dump(). Use a custom async context or an async serializer."
            )

        return self.run_sync()

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
        return self.run_sync()

    def run_sync(self) -> R:
        if self.is_async:
            raise Exception("Sync running async")

        self.func = cast(SyncComputation[R], self.func)

        return self.func(**self.func_kwargs)

    async def run(self) -> R:
        if not self.is_async:
            raise Exception("Async running sync")

        self.func = cast(AsyncComputation[R], self.func)

        return await self.func(**self.func_kwargs)
