import json
from typing import Any

from ame_json.models.path_data import PathData, PathDataMapper
from ame_json.logging_utils import get_logger

logger = get_logger(__name__)


class ProgressiveAssemblerBase:
    @staticmethod
    def _decode_value(value: bytes) -> dict:
        json_value_str = value.decode()
        data = json.loads(json_value_str)

        return data

    @staticmethod
    def _insert_value(data: dict, path: list[str], value: Any):
        data_value = data

        for index, path_part in enumerate(path):
            if path_part not in data:
                raise Exception(f"Bad path: {path}")

            if index == len(path) - 1:
                data_value[path_part] = value

                continue

            data_value = data_value[path_part]

    @staticmethod
    def _get_first_computed_key(keys: list) -> str | None:
        for key in keys:
            if key.startswith("$"):
                return key

    @staticmethod
    def _get_current_path(path_data_mapper: PathDataMapper, keys: list) -> list[str]:
        key = ProgressiveAssemblerBase._get_first_computed_key(keys)

        if key is None:
            return []

        path_data = path_data_mapper.get(key)

        if path_data is None:
            return []

        return path_data.path

    @staticmethod
    def update_data(
        object_value: dict[str, Any],
        final_data: dict,
        path_data_mapper: PathDataMapper,
    ) -> tuple[dict, dict]:
        keys = list(object_value.keys())
        current_path = ProgressiveAssemblerBase._get_current_path(
            path_data_mapper, keys
        )

        for key, value in object_value.items():
            if key.startswith("$"):
                if key not in path_data_mapper:
                    logger.error(f"key was not in pending update data: {key}")

                    continue

                path_data = path_data_mapper.get(key)

                if not path_data:
                    logger.error(f"can't find path for key: {key}")

                    continue

                ProgressiveAssemblerBase._insert_value(
                    final_data, path_data.path, value
                )

                continue

            if isinstance(value, str) and value.startswith("$"):
                path = [*current_path, key]
                path_data_mapper[value] = PathData(value=value, path=path)

            final_data[key] = value

        return final_data, path_data_mapper
