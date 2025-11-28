from collections.abc import Callable
import dataclasses


@dataclasses.dataclass
class ProgressiveStreamerContext:
    placeholder_mapper: dict
    get_counter_func: Callable[..., int]
    update_counter_func: Callable
