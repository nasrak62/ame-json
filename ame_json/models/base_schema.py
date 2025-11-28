from collections.abc import AsyncGenerator, Generator
from abc import ABC, abstractmethod
from typing import Any
from pydantic import BaseModel


class AbstractBaseProgressiveJSONStreamer[T: BaseProgressiveSchema](ABC):
    def __init__(self, schema_instance: T):
        pass

    @abstractmethod
    def stream(self) -> Generator[bytes, Any, None]:
        raise NotImplementedError

        yield b""


class BaseProgressiveJSONStreamer[T: BaseProgressiveSchema](
    AbstractBaseProgressiveJSONStreamer[T]
):
    def stream(self) -> Generator[bytes, Any, None]:
        yield b""


class BaseProgressiveSchema(BaseModel):
    def to_streamer(self) -> BaseProgressiveJSONStreamer:
        """
        Exposes the streamer instance, which contains the async generator.
        """
        return BaseProgressiveJSONStreamer(self)
