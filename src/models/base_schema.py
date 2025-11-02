from collections.abc import Generator
from abc import ABC, abstractmethod
from typing import Any
from pydantic import BaseModel


class AbstractBaseProgressiveJSONStreamer[T: BaseProgressiveSchema](ABC):
    def __init__(self, schema_instance: T):
        pass

    @abstractmethod
    def stream_sync(self) -> Generator[bytes, Any, None]:
        pass


class BaseProgressiveJSONStreamer[T: BaseProgressiveSchema](
    AbstractBaseProgressiveJSONStreamer[T]
):
    def stream_sync(self) -> Generator[bytes, Any, None]:
        yield b""


class BaseProgressiveSchema(BaseModel):
    def to_streamer(self) -> BaseProgressiveJSONStreamer:
        """
        Exposes the streamer instance, which contains the async generator.
        """
        return BaseProgressiveJSONStreamer(self)
