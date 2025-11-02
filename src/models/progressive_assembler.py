from collections.abc import Generator
import json
from typing import Any

from src.models.path_data import PathData, PathDataMapper
from src.logging_utils import get_logger

logger = get_logger(__name__)


class ProgressiveAssembler:
    def __init__(self):
        pass

    def decode_value(self, value: bytes) -> dict:
        json_value_str = value.decode()
        data = json.loads(json_value_str)

        return data

    def insert_value(self, data: dict, path: list[str], value: Any):
        data_value = data

        for index, path_part in enumerate(path):
            if path_part not in data:
                raise Exception(f"Bad path: {path}")

            if index == len(path) - 1:
                data_value[path_part] = value

                continue

            data_value = data_value[path_part]

    def get_first_computed_key(self, keys: list) -> str | None:
        for key in keys:
            if key.startswith("$"):
                return key

    def get_current_path(
        self, path_data_mapper: PathDataMapper, keys: list
    ) -> list[str]:
        key = self.get_first_computed_key(keys)

        if key is None:
            return []

        path_data = path_data_mapper.get(key)

        if path_data is None:
            return []

        return path_data.path

    def update_data(
        self,
        object_value: dict[str, Any],
        final_data: dict,
        path_data_mapper: PathDataMapper,
    ) -> tuple[dict, dict]:
        keys = list(object_value.keys())
        current_path = self.get_current_path(path_data_mapper, keys)

        for key, value in object_value.items():
            if key.startswith("$"):
                if key not in path_data_mapper:
                    logger.error(f"key was not in pending update data: {key}")

                    continue

                path_data = path_data_mapper.get(key)

                if not path_data:
                    logger.error(f"can't find path for key: {key}")

                    continue

                self.insert_value(final_data, path_data.path, value)

                continue

            if isinstance(value, str) and value.startswith("$"):
                path = [*current_path, key]
                path_data_mapper[value] = PathData(value=value, path=path)

            final_data[key] = value

        return final_data, path_data_mapper

    def assamble(self, generator: Generator[bytes, Any, None]) -> dict:
        stream_completed = False
        final_data: dict = {}
        path_data_mapper: PathDataMapper = {}

        while not stream_completed:
            try:
                value = next(generator)

                if not isinstance(value, bytes):
                    logger.error(f"excpected bytes, got: {value}")

                    continue

                object_value = self.decode_value(value)
                is_finished = bool(object_value.pop("completed_stream", None))

                if not isinstance(object_value, dict):
                    logger.error(f"excpected dict, got: {object_value}")

                    continue

                final_data, path_data_mapper = self.update_data(
                    object_value, final_data, path_data_mapper
                )

                if is_finished:
                    stream_completed = True

            except Exception as e:
                print(f"assamble: {e}")

        return final_data
