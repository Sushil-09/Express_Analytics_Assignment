from typing import Any

import requests

from config import (
    BACKEND_URL,
    CHAT_TIMEOUT_SECONDS,
    FEEDBACK_TIMEOUT_SECONDS,
    HEALTH_TIMEOUT_SECONDS,
    INGEST_TIMEOUT_SECONDS,
)


class BackendAPIError(Exception):
    """An error returned by or encountered while contacting the backend."""


def _request_json(
    method: str,
    path: str,
    timeout: int,
    **kwargs: Any,
) -> dict[str, Any]:
    try:
        response = requests.request(
            method,
            f"{BACKEND_URL.rstrip('/')}{path}",
            timeout=timeout,
            **kwargs,
        )
    except requests.Timeout as error:
        raise BackendAPIError(
            "The backend took too long to respond. Please try again."
        ) from error
    except requests.ConnectionError as error:
        raise BackendAPIError(
            "Cannot connect to the backend. Make sure the FastAPI server is running."
        ) from error
    except requests.RequestException as error:
        raise BackendAPIError(f"Unable to contact the backend: {error}") from error

    try:
        payload = response.json()
    except ValueError as error:
        if not response.ok:
            raise BackendAPIError(
                f"Backend request failed (HTTP {response.status_code})."
            ) from error
        raise BackendAPIError("The backend returned an invalid response.") from error

    if not response.ok:
        detail = payload.get("detail") if isinstance(payload, dict) else None
        message = detail or (
            payload.get("message") if isinstance(payload, dict) else None
        )
        if isinstance(message, (dict, list)):
            message = str(message)
        if not isinstance(message, str) or not message.strip():
            message = f"Backend request failed (HTTP {response.status_code})."
        raise BackendAPIError(message)

    if not isinstance(payload, dict):
        raise BackendAPIError("The backend returned an unexpected response format.")
    return payload


def check_health() -> dict[str, Any]:
    payload = _request_json("GET", "/health", HEALTH_TIMEOUT_SECONDS)
    if payload.get("status") != "healthy":
        raise BackendAPIError("The backend did not report a healthy status.")
    return payload


def send_chat_message(question: str) -> dict[str, Any]:
    return _request_json(
        "POST",
        "/chat",
        CHAT_TIMEOUT_SECONDS,
        json={"question": question},
    )


def send_feedback(
    rating: str,
    comment: str | None = None,
    question: str | None = None,
    answer: str | None = None,
) -> dict[str, Any]:
    return _request_json(
        "POST",
        "/feedback",
        FEEDBACK_TIMEOUT_SECONDS,
        json={
            "rating": rating,
            "comment": comment,
            "question": question,
            "answer": answer,
        },
    )


def ingest_url(url: str) -> dict[str, Any]:
    return _request_json(
        "POST",
        "/ingest/url",
        INGEST_TIMEOUT_SECONDS,
        json={"url": url},
    )


def ingest_file(uploaded_file: Any) -> dict[str, Any]:
    uploaded_file.seek(0)
    file_upload = (
        uploaded_file.name,
        uploaded_file,
        getattr(uploaded_file, "type", None) or "application/octet-stream",
    )
    return _request_json(
        "POST",
        "/ingest/file",
        INGEST_TIMEOUT_SECONDS,
        files={"file": file_upload},
    )
