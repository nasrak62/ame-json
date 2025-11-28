from collections.abc import AsyncGenerator
from typing import Any

from ame_json.models.assembler.base import ProgressiveAssemblerBase
from ame_json.models.path_data import PathDataMapper
from ame_json.logging_utils import get_logger

logger = get_logger(__name__)


class AsyncProgressiveAssembler(ProgressiveAssemblerBase):
    @staticmethod
    async def assamble(generator: AsyncGenerator[bytes, Any]) -> dict:
        stream_completed = False
        final_data: dict = {}
        path_data_mapper: PathDataMapper = {}

        while not stream_completed:
            try:
                value = await anext(generator)

                if not isinstance(value, bytes):
                    logger.error(f"excpected bytes, got: {value}")

                    continue

                object_value = AsyncProgressiveAssembler._decode_value(value)
                is_finished = bool(object_value.pop("completed_stream", None))

                if not isinstance(object_value, dict):
                    logger.error(f"excpected dict, got: {object_value}")

                    continue

                final_data, path_data_mapper = AsyncProgressiveAssembler.update_data(
                    object_value, final_data, path_data_mapper
                )

                if is_finished:
                    stream_completed = True

            except Exception as e:
                print(f"assamble: {e}")

        return final_data
