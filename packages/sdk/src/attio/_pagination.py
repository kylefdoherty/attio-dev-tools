"""Pagination helpers for auto-iterating through multi-page API responses."""

from __future__ import annotations

from collections.abc import Callable, Coroutine, Iterator
from typing import Any, Generic, TypeVar

from attio.models._base import ListResponse, PaginatedResponse

T = TypeVar("T")


class CursorIterator(Generic[T]):
    """Synchronous auto-paginator for cursor-based endpoints.

    Iterates through all pages by following ``pagination.next_cursor`` until
    it is ``None``.
    """

    def __init__(
        self,
        fetch_page: Callable[[str | None], PaginatedResponse[T]],
    ) -> None:
        self._fetch_page = fetch_page

    def __iter__(self) -> Iterator[T]:
        cursor: str | None = None
        while True:
            response = self._fetch_page(cursor)
            yield from response.data
            cursor = response.pagination.next_cursor
            if cursor is None:
                break


class AsyncCursorIterator(Generic[T]):
    """Asynchronous auto-paginator for cursor-based endpoints.

    Iterates through all pages by following ``pagination.next_cursor`` until
    it is ``None``.
    """

    def __init__(
        self,
        fetch_page: Callable[[str | None], Coroutine[Any, Any, PaginatedResponse[T]]],
    ) -> None:
        self._fetch_page = fetch_page

    def __aiter__(self) -> AsyncCursorIterator[T]:
        self._cursor: str | None = None
        self._buffer: list[T] = []
        self._done = False
        return self

    async def __anext__(self) -> T:
        while not self._buffer:
            if self._done:
                raise StopAsyncIteration
            response = await self._fetch_page(self._cursor)
            self._buffer = list(response.data)
            self._cursor = response.pagination.next_cursor
            if self._cursor is None:
                self._done = True
            if not self._buffer and self._done:
                raise StopAsyncIteration

        return self._buffer.pop(0)


class OffsetIterator(Generic[T]):
    """Synchronous auto-paginator for offset-based endpoints.

    Increments offset by the number of items returned. Stops when
    ``len(data) < limit`` (partial page indicates end of results).
    """

    def __init__(
        self,
        fetch_page: Callable[[int, int], ListResponse[T]],
        limit: int = 500,
    ) -> None:
        self._fetch_page = fetch_page
        self._limit = limit

    def __iter__(self) -> Iterator[T]:
        offset = 0
        while True:
            response = self._fetch_page(offset, self._limit)
            yield from response.data
            if len(response.data) < self._limit:
                break
            offset += len(response.data)


class AsyncOffsetIterator(Generic[T]):
    """Asynchronous auto-paginator for offset-based endpoints.

    Increments offset by the number of items returned. Stops when
    ``len(data) < limit`` (partial page indicates end of results).
    """

    def __init__(
        self,
        fetch_page: Callable[[int, int], Coroutine[Any, Any, ListResponse[T]]],
        limit: int = 500,
    ) -> None:
        self._fetch_page = fetch_page
        self._limit = limit

    def __aiter__(self) -> AsyncOffsetIterator[T]:
        self._offset = 0
        self._buffer: list[T] = []
        self._done = False
        return self

    async def __anext__(self) -> T:
        while not self._buffer:
            if self._done:
                raise StopAsyncIteration
            response = await self._fetch_page(self._offset, self._limit)
            self._buffer = list(response.data)
            if len(response.data) < self._limit:
                self._done = True
            else:
                self._offset += len(response.data)
            if not self._buffer and self._done:
                raise StopAsyncIteration

        return self._buffer.pop(0)
