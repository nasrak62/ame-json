from collections.abc import AsyncGenerator
from abc import ABC, abstractmethod
from pydantic import BaseModel


class AsyncAbstractBaseProgressiveJSONStreamer[T: AsyncBaseProgressiveSchema](ABC):
    def __init__(self, schema_instance: T):
        pass

    @abstractmethod
    async def stream(self) -> AsyncGenerator[bytes, None]:
        raise NotImplementedError

        yield b""


class AsyncBaseProgressiveJSONStreamer[T: AsyncBaseProgressiveSchema](
    AsyncAbstractBaseProgressiveJSONStreamer[T]
):
    async def stream(self) -> AsyncGenerator[bytes, None]:
        yield b""


class AsyncBaseProgressiveSchema(BaseModel):
    def to_streamer(self) -> AsyncBaseProgressiveJSONStreamer:
        """
        Exposes the streamer instance, which contains the async generator.
        """
        return AsyncBaseProgressiveJSONStreamer(self)
