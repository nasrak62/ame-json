# GEMINI.md - ame-json

This file provides a summary of the `ame-json` project, its structure, and how to work with it.

## Project Overview

`ame-json` is a Python library for progressively streaming JSON data. It's built on top of `pydantic` and allows you to define a schema with `Computation` fields. These fields are populated by functions that are executed as their data is needed, and the results are streamed to the client.

This is particularly useful for applications where parts of the JSON response are slow to generate, as it allows the client to receive and process the faster parts of the response without waiting for the entire payload.

The core components are:

*   **`ProgressiveSchema` / `AsyncProgressiveSchema`**: These are `pydantic` models that can contain `Computation` fields.
*   **`Computation`**: A wrapper around a function that will be executed to compute the value of a field.
*   **`ProgressiveJSONStreamer` / `AsyncProgressiveJSONStreamer`**: These classes take a `ProgressiveSchema` instance and generate a stream of JSON data.

The example in `examples/main.py` demonstrates how to use `ame-json` to create a streaming HTTP server.

## Building and Running

### Installation

To install the project and its dependencies, it is recommended to use a virtual environment.

```bash
# Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate

# Install the project in editable mode with dev dependencies
pip install -e ".[dev]"
```

### Running Tests

The project uses `pytest` for testing. To run the tests, execute the following command:

```bash
pytest
```

### Running the Example

The `examples/main.py` file contains a simple HTTP server that demonstrates the streaming functionality. To run it, execute the following command:

```bash
python examples/main.py
```

Then, you can access the stream at `http://localhost:8000/stream`.

## Development Conventions

*   **Code Style**: The project follows the standard Python code style (PEP 8).
*   **Type Hinting**: The project uses type hints extensively.
*   **Dependencies**: The project uses `uv` to manage dependencies. `uv.lock` is the lock file. `pyproject.toml` lists the dependencies.
*   **Testing**: All new features and bug fixes should be accompanied by tests.
