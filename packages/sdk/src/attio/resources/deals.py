"""Deals convenience resource — delegates to Records with object_slug='deals'."""

from __future__ import annotations

from attio.resources._standard_object import (
    AsyncStandardObjectResource,
    StandardObjectResource,
)


class DealsResource(StandardObjectResource):
    """Synchronous Deals resource (convenience wrapper around Records)."""

    _object_slug = "deals"


# --- GENERATED ASYNC CODE BELOW --- #


class AsyncDealsResource(AsyncStandardObjectResource):
    """Asynchronous Deals resource (convenience wrapper around Records)."""

    _object_slug = "deals"
