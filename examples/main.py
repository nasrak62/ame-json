import http.server
import socketserver
import time

from pydantic import BaseModel

from src.ame_json.models.progressive_schema import ProgressiveSchema
from src.ame_json.models.computation import Computation

PORT = 8000


class Products(BaseModel):
    name: str
    price: float


# Mock data retrieval functions (now all synchronous, simulating Django)
def get_user_products_sync() -> list[Products]:
    """Simulates a slow, sync database call."""

    time.sleep(2)  # Simulate 2 seconds of work
    return list(
        map(
            lambda x: Products(name=x, price=0.0),
            ["Laptop Bag", "Monitor", "Mechanical Keyboard"],
        )
    )


def calculate_loyalty_score_sync() -> int:
    """Simulates a slower, sync external API call or heavy computation."""

    time.sleep(1)  # Simulate 1 second of work
    return 95


# The result type definition is just for type hinting, not used by the streamer logic


class UserAddress(BaseModel):
    """A regular nested Pydantic model (no streaming here)."""

    street: str
    city: str


class UserProfile(ProgressiveSchema):
    """
    The main schema defining the expected JSON structure.
    Computation fields are defined by assigning a Computation object on instance creation.
    """

    # Standard Pydantic fields
    user_id: int
    username: str
    email: str

    address: UserAddress

    products: Computation[list[Products]]
    loyalty_score: Computation[int]


def generate_data():
    user_data = UserProfile(
        user_id=101,
        username="jdoe",
        email="john.doe@example.com",
        address=UserAddress(street="123 Placeholder Dr", city="Streamington"),
        products=Computation(get_user_products_sync),  # Pass the sync callable
        loyalty_score=Computation(
            calculate_loyalty_score_sync
        ),  # Pass another sync callable
    )


class StreamingHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/stream":
            self.send_response(200)
            self.send_header("Content-type", "text/event-stream")
            self.send_header("Cache-Control", "no-cache")
            self.end_headers()

            # Generator function to yield streaming data
            # def generate_data():
            #     for i in range(10):
            #         data = f"data: Message {i}\n\n"
            #         self.wfile.write(data.encode("utf-8"))
            #         time.sleep(1)  # Simulate some processing time
            #     self.wfile.write(b"data: END\n\n")  # Signal end of stream

            generate_data()
        else:
            # Handle other requests normally (e.g., serving static files)
            super().do_GET()


with socketserver.TCPServer(("", PORT), StreamingHandler) as httpd:
    print(f"Serving streaming server at port {PORT}")
    httpd.serve_forever()
