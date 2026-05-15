"""Companies convenience resource — delegates to Records with object_slug='companies'."""

from __future__ import annotations

from attio.resources._standard_object import (
    AsyncStandardObjectResource,
    StandardObjectResource,
)


class CompaniesResource(StandardObjectResource):
    """Synchronous Companies resource (convenience wrapper around Records)."""

    _object_slug = "companies"


class AsyncCompaniesResource(AsyncStandardObjectResource):
    """Asynchronous Companies resource (convenience wrapper around Records)."""

    _object_slug = "companies"
