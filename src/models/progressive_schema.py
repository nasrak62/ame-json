from src.models.progressive_streamer import ProgressiveJSONStreamer
from src.models.base_schema import BaseProgressiveSchema


class ProgressiveSchema(BaseProgressiveSchema):
    """
    A base class for schemas that will be streamed progressively.
    """

    def to_streamer(self) -> ProgressiveJSONStreamer:
        """
        Exposes the streamer instance, which contains the async generator.
        """
        return ProgressiveJSONStreamer(self)
