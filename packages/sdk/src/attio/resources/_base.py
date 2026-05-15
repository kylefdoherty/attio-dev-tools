"""Base resource classes for sync and async resources."""

from __future__ import annotations

from attio._http import AsyncHttpTransport, HttpTransport


class SyncResource:
    """Base class for synchronous resources."""

    def __init__(self, http: HttpTransport) -> None:
        self._http = http


class AsyncResource:
    """Base class for asynchronous resources."""

    def __init__(self, http: AsyncHttpTransport) -> None:
        self._http = http
