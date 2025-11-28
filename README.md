# ame-json

`ame-json` is a Python library that enables progressive streaming of JSON data. It's built on top of `pydantic` and allows you to define a schema with `Computation` fields. These fields are populated by functions (which can be synchronous or asynchronous) that are executed as their data is needed, and the results are streamed to the client. This is particularly useful for applications where parts of the JSON response are slow to generate, as it allows the client to receive and process the faster parts of the response without waiting for the entire payload.

## Features

-   **Progressive Streaming**: Stream complex JSON objects as they are constructed.
-   **Layered Streaming**: Nested objects are streamed layer by layer, allowing the client to process data as it arrives.
-   **Pydantic Integration**: Define your data models using `pydantic`.
-   **Sync and Async Support**: Works with both synchronous and asynchronous code.
-   **Computable Fields**: Defer slow computations and stream their results.

## Installation

```bash
pip install ame-json
```

## Quick Start

Here's a simple example of how to use `ame-json` to stream a JSON object with a computed field and a nested object.

```python
import time
from pydantic import BaseModel
from ame_json.models.progressive_schema import ProgressiveSchema
from ame_json.models.computation import Computation

# 1. Define your data models using Pydantic
class Product(BaseModel):
    name: str
    price: float

class Address(BaseModel):
    street: str
    city: str

def get_user_products() -> list[Product]:
    """Simulates a slow database call."""
    time.sleep(2)
    return [
        Product(name="Laptop Bag", price=45.00),
        Product(name="Monitor", price=350.50),
    ]

# 2. Create a ProgressiveSchema for the streaming response
class UserProfile(ProgressiveSchema):
    user_id: int
    username: str
    address: Address
    products: Computation[list[Product]]

# 3. Instantiate your schema with data and computations
user_profile = UserProfile(
    user_id=101,
    username="jdoe",
    address=Address(street="123 Main St", city="Anytown"),
    products=Computation(get_user_products),
)

# 4. Create a streamer and iterate through the stream
streamer = user_profile.to_streamer()

for chunk in streamer.stream():
    print(chunk.decode(), end="")

```

## Async Quick Start

`ame-json` also provides full support for asynchronous operations using Python's `asyncio`. This is ideal for applications that need to perform non-blocking I/O operations, such as fetching data from a database or an external API asynchronously.

Here's how you can use `ame-json` with async/await:

```python
import asyncio
from pydantic import BaseModel
from ame_json.models.async_progressive_schema import AsyncProgressiveSchema
from ame_json.models.async_computation import AsyncComputation

# 1. Define your data models as usual
class Product(BaseModel):
    name: str
    price: float

class Address(BaseModel):
    street: str
    city: str

async def get_user_products() -> list[Product]:
    """Simulates a slow async database call."""
    await asyncio.sleep(2)
    return [
        Product(name="Laptop Bag", price=45.00),
        Product(name="Monitor", price=350.50),
    ]

# 2. Use AsyncProgressiveSchema for the streaming response
class UserProfile(AsyncProgressiveSchema):
    user_id: int
    username: str
    address: Address
    products: AsyncComputation[list[Product]]

# 3. Instantiate your schema with async computations
user_profile = UserProfile(
    user_id=101,
    username="jdoe",
    address=Address(street="123 Main St", city="Anytown"),
    products=AsyncComputation(get_user_products),
)

# 4. Create an async streamer and iterate through the stream
async def main():
    streamer = user_profile.to_streamer()
    async for chunk in streamer.stream():
        print(chunk.decode(), end="")

if __name__ == "__main__":
    asyncio.run(main())

```
The async equivalent of `ProgressiveSchema` is `AsyncProgressiveSchema`, and `Computation` is `AsyncComputation`. The `AsyncComputation` class is designed to wrap an `async` function, and the `AsyncProgressiveJSONStreamer` will `await` it during the streaming process.

The streaming process remains the same, but the iteration over the stream is now done asynchronously with `async for`.

## How It Works

The streaming process works by breaking down the JSON object into layers. Each nested object or `Computation` field represents a new layer that is streamed separately.

The core of `ame-json` is the `ProgressiveSchema` and the `Computation` class.

-   **`ProgressiveSchema`**: A `pydantic.BaseModel` subclass that can have fields of type `Computation` and nested `pydantic` models.
-   **`Computation`**: A generic type that you wrap around a callable. `ame-json` will execute this callable to compute the value of the field during the streaming process.

When you create a `ProgressiveJSONStreamer` from a `ProgressiveSchema` instance, it starts serializing the object into JSON.

1.  It first sends the top-level fields of the main object.
2.  When it encounters a **nested `pydantic` model**, it sends a placeholder and adds the nested object to a queue to be processed in a subsequent layer.
3.  When it encounters a **`Computation` field**, it also sends a placeholder and starts executing the callable to compute the value.

The streamer then processes the queue, sending the content of each nested object and the results of each computation as separate chunks in the stream, each replacing its placeholder. This allows a client to parse and use the initial data immediately and then progressively render the more complex, nested, or computed parts of the JSON as they arrive.


## Development

To set up the development environment:

```bash
# Clone the repository
git clone https://github.com/nasrak62/ame-json.git
cd ame-json

# Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -e ".[dev]"

# Run tests
pytest
```

## License

This project is licensed under the MIT License.
