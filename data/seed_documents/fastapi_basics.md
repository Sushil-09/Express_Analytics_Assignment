# FastAPI Basics

## Introduction

FastAPI is a modern Python framework for building APIs. It uses standard Python type hints to define request data and validate inputs.

FastAPI automatically generates interactive API documentation based on the OpenAPI standard. By default, the interactive documentation is available through Swagger UI.

## Creating an Application

A basic FastAPI application starts by creating an instance of the FastAPI class.

```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World"}
```

In this example, the application defines a GET endpoint at the root path.

## Path Operations

A path operation consists of an HTTP method and a URL path.

Common HTTP methods include:

- GET: Retrieve information
- POST: Create new data
- PUT: Update existing data
- DELETE: Remove data
- PATCH: Partially update data

## Path Parameters

Path parameters allow values to be included directly in the URL.

Example:

```python
@app.get("/items/{item_id}")
async def read_item(item_id: int):
    return {"item_id": item_id}
```

The `item_id` value is extracted from the URL and converted according to its declared type.

If the provided value does not match the expected type, FastAPI automatically returns a validation error.

## Query Parameters

Query parameters are values included after the question mark in a URL.

Example:

```python
@app.get("/items/")
async def read_items(skip: int = 0, limit: int = 10):
    return {"skip": skip, "limit": limit}
```

In this example, `skip` and `limit` are query parameters with default values.

## Request and Response

An API receives requests from clients and returns responses.

FastAPI can automatically parse request data, validate it using Python type annotations, and serialize Python objects into JSON responses.