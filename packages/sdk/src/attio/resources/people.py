"""People convenience resource — delegates to Records with object_slug='people'."""

from __future__ import annotations

from attio.resources._standard_object import (
    AsyncStandardObjectResource,
    StandardObjectResource,
)


class PeopleResource(StandardObjectResource):
    """Synchronous People resource (convenience wrapper around Records)."""

    _object_slug = "people"


class AsyncPeopleResource(AsyncStandardObjectResource):
    """Asynchronous People resource (convenience wrapper around Records)."""

    _object_slug = "people"
