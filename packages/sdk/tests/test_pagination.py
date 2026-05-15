"""Tests for pagination helpers (CursorIterator, AsyncCursorIterator, OffsetIterator, AsyncOffsetIterator)."""

from __future__ import annotations

from attio._pagination import (
    AsyncCursorIterator,
    AsyncOffsetIterator,
    CursorIterator,
    OffsetIterator,
)
from attio.models._base import ListResponse, PaginatedResponse, Pagination

# ---------------------------------------------------------------------------
# CursorIterator (sync)
# ---------------------------------------------------------------------------


class TestCursorIterator:
    def test_single_page(self) -> None:
        """Single page with no next_cursor should yield all items and stop."""
        page = PaginatedResponse[str](
            data=["a", "b", "c"],
            pagination=Pagination(next_cursor=None),
        )

        def fetch_page(cursor: str | None) -> PaginatedResponse[str]:
            assert cursor is None
            return page

        items = list(CursorIterator(fetch_page=fetch_page))
        assert items == ["a", "b", "c"]

    def test_multi_page(self) -> None:
        """Multiple pages should all be yielded in order."""
        pages = [
            PaginatedResponse[str](
                data=["a", "b"],
                pagination=Pagination(next_cursor="cursor_2"),
            ),
            PaginatedResponse[str](
                data=["c", "d"],
                pagination=Pagination(next_cursor="cursor_3"),
            ),
            PaginatedResponse[str](
                data=["e"],
                pagination=Pagination(next_cursor=None),
            ),
        ]
        call_count = 0

        def fetch_page(cursor: str | None) -> PaginatedResponse[str]:
            nonlocal call_count
            if call_count == 0:
                assert cursor is None
            elif call_count == 1:
                assert cursor == "cursor_2"
            elif call_count == 2:
                assert cursor == "cursor_3"
            result = pages[call_count]
            call_count += 1
            return result

        items = list(CursorIterator(fetch_page=fetch_page))
        assert items == ["a", "b", "c", "d", "e"]
        assert call_count == 3

    def test_empty_results(self) -> None:
        """Empty first page should yield nothing."""
        page = PaginatedResponse[str](
            data=[],
            pagination=Pagination(next_cursor=None),
        )

        def fetch_page(cursor: str | None) -> PaginatedResponse[str]:
            return page

        items = list(CursorIterator(fetch_page=fetch_page))
        assert items == []


# ---------------------------------------------------------------------------
# AsyncCursorIterator
# ---------------------------------------------------------------------------


class TestAsyncCursorIterator:
    async def test_single_page(self) -> None:
        """Single page with no next_cursor should yield all items and stop."""
        page = PaginatedResponse[str](
            data=["a", "b", "c"],
            pagination=Pagination(next_cursor=None),
        )

        async def fetch_page(cursor: str | None) -> PaginatedResponse[str]:
            assert cursor is None
            return page

        items = []
        async for item in AsyncCursorIterator(fetch_page=fetch_page):
            items.append(item)
        assert items == ["a", "b", "c"]

    async def test_multi_page(self) -> None:
        """Multiple pages should all be yielded in order."""
        pages = [
            PaginatedResponse[str](
                data=["a", "b"],
                pagination=Pagination(next_cursor="cursor_2"),
            ),
            PaginatedResponse[str](
                data=["c", "d"],
                pagination=Pagination(next_cursor="cursor_3"),
            ),
            PaginatedResponse[str](
                data=["e"],
                pagination=Pagination(next_cursor=None),
            ),
        ]
        call_count = 0

        async def fetch_page(cursor: str | None) -> PaginatedResponse[str]:
            nonlocal call_count
            result = pages[call_count]
            call_count += 1
            return result

        items = []
        async for item in AsyncCursorIterator(fetch_page=fetch_page):
            items.append(item)
        assert items == ["a", "b", "c", "d", "e"]
        assert call_count == 3

    async def test_empty_results(self) -> None:
        """Empty first page should yield nothing."""
        page = PaginatedResponse[str](
            data=[],
            pagination=Pagination(next_cursor=None),
        )

        async def fetch_page(cursor: str | None) -> PaginatedResponse[str]:
            return page

        items = []
        async for item in AsyncCursorIterator(fetch_page=fetch_page):
            items.append(item)
        assert items == []


# ---------------------------------------------------------------------------
# OffsetIterator (sync)
# ---------------------------------------------------------------------------


class TestOffsetIterator:
    def test_single_page(self) -> None:
        """Partial page (len(data) < limit) should stop after one fetch."""
        page = ListResponse[str](data=["a", "b"])

        def fetch_page(offset: int, limit: int) -> ListResponse[str]:
            assert offset == 0
            assert limit == 10
            return page

        items = list(OffsetIterator(fetch_page=fetch_page, limit=10))
        assert items == ["a", "b"]

    def test_multi_page(self) -> None:
        """Full pages should continue fetching; partial page stops iteration."""
        pages = [
            ListResponse[str](data=["a", "b", "c"]),  # full page (limit=3)
            ListResponse[str](data=["d", "e", "f"]),  # full page
            ListResponse[str](data=["g"]),             # partial page -> stop
        ]
        call_count = 0

        def fetch_page(offset: int, limit: int) -> ListResponse[str]:
            nonlocal call_count
            if call_count == 0:
                assert offset == 0
            elif call_count == 1:
                assert offset == 3
            elif call_count == 2:
                assert offset == 6
            result = pages[call_count]
            call_count += 1
            return result

        items = list(OffsetIterator(fetch_page=fetch_page, limit=3))
        assert items == ["a", "b", "c", "d", "e", "f", "g"]
        assert call_count == 3

    def test_empty_results(self) -> None:
        """Empty first page should yield nothing."""
        page = ListResponse[str](data=[])

        def fetch_page(offset: int, limit: int) -> ListResponse[str]:
            return page

        items = list(OffsetIterator(fetch_page=fetch_page, limit=10))
        assert items == []

    def test_exact_page_boundary(self) -> None:
        """When last page is exactly full, one more empty fetch stops iteration."""
        pages = [
            ListResponse[str](data=["a", "b"]),  # full page (limit=2)
            ListResponse[str](data=[]),           # empty -> stop
        ]
        call_count = 0

        def fetch_page(offset: int, limit: int) -> ListResponse[str]:
            nonlocal call_count
            result = pages[call_count]
            call_count += 1
            return result

        items = list(OffsetIterator(fetch_page=fetch_page, limit=2))
        assert items == ["a", "b"]
        assert call_count == 2


# ---------------------------------------------------------------------------
# AsyncOffsetIterator
# ---------------------------------------------------------------------------


class TestAsyncOffsetIterator:
    async def test_single_page(self) -> None:
        """Partial page (len(data) < limit) should stop after one fetch."""
        page = ListResponse[str](data=["a", "b"])

        async def fetch_page(offset: int, limit: int) -> ListResponse[str]:
            return page

        items = []
        async for item in AsyncOffsetIterator(fetch_page=fetch_page, limit=10):
            items.append(item)
        assert items == ["a", "b"]

    async def test_multi_page(self) -> None:
        """Full pages should continue fetching; partial page stops iteration."""
        pages = [
            ListResponse[str](data=["a", "b", "c"]),
            ListResponse[str](data=["d", "e", "f"]),
            ListResponse[str](data=["g"]),
        ]
        call_count = 0

        async def fetch_page(offset: int, limit: int) -> ListResponse[str]:
            nonlocal call_count
            result = pages[call_count]
            call_count += 1
            return result

        items = []
        async for item in AsyncOffsetIterator(fetch_page=fetch_page, limit=3):
            items.append(item)
        assert items == ["a", "b", "c", "d", "e", "f", "g"]
        assert call_count == 3

    async def test_empty_results(self) -> None:
        """Empty first page should yield nothing."""
        page = ListResponse[str](data=[])

        async def fetch_page(offset: int, limit: int) -> ListResponse[str]:
            return page

        items = []
        async for item in AsyncOffsetIterator(fetch_page=fetch_page, limit=10):
            items.append(item)
        assert items == []

    async def test_exact_page_boundary(self) -> None:
        """When last page is exactly full, one more empty fetch stops iteration."""
        pages = [
            ListResponse[str](data=["a", "b"]),
            ListResponse[str](data=[]),
        ]
        call_count = 0

        async def fetch_page(offset: int, limit: int) -> ListResponse[str]:
            nonlocal call_count
            result = pages[call_count]
            call_count += 1
            return result

        items = []
        async for item in AsyncOffsetIterator(fetch_page=fetch_page, limit=2):
            items.append(item)
        assert items == ["a", "b"]
        assert call_count == 2
