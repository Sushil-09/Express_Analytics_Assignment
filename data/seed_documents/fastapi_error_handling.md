# FastAPI Error Handling

## Introduction

APIs need to communicate errors clearly to clients. FastAPI provides mechanisms for returning HTTP errors and handling validation problems.

## HTTPException

FastAPI provides `HTTPException` for returning HTTP error responses.

Example:

```python
from fastapi import FastAPI, HTTPException

app = FastAPI()

@app.get("/items/{item_id}")
async def read_item(item_id: int):
    if item_id != 1:
        raise HTTPException(
            status_code=404,
            detail="Item not found"
        )

    return {"item_id": item_id}
```

When an `HTTPException` is raised, FastAPI returns an HTTP response containing the specified status code and error details.

## Common HTTP Status Codes

Some common status codes are:

- 200: Successful request
- 201: Resource created successfully
- 400: Bad request
- 401: Authentication required
- 403: Permission denied
- 404: Resource not found
- 422: Validation error
- 500: Internal server error

## Request Validation Errors

FastAPI automatically validates incoming request data based on Python type annotations and Pydantic models.

If a client sends invalid data, FastAPI returns a validation error describing the problem.

For example, if an endpoint expects an integer path parameter but receives text, the request will fail validation.

## Custom Exception Handlers

FastAPI allows applications to define custom exception handlers.

Custom handlers can change how errors are formatted and returned to clients.

This can be useful when an API needs a consistent error response format across multiple endpoints.