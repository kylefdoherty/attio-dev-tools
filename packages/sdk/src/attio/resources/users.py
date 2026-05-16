"""Users convenience resource — delegates to Records with object_slug='users'."""

from __future__ import annotations

from attio.resources._standard_object import (
    AsyncStandardObjectResource,
    StandardObjectResource,
)


class UsersResource(StandardObjectResource):
    """Synchronous Users resource (convenience wrapper around Records)."""

    _object_slug = "users"


# --- GENERATED ASYNC CODE BELOW --- #


class AsyncUsersResource(AsyncStandardObjectResource):
    """Asynchronous Users resource (convenience wrapper around Records)."""

    _object_slug = "users"
