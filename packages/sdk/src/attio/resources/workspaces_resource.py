"""Workspaces convenience resource — delegates to Records with object_slug='workspaces'.

The filename uses ``workspaces_resource`` to avoid conflict with potential
``workspaces`` module names elsewhere in the package.
"""

from __future__ import annotations

from attio.resources._standard_object import (
    AsyncStandardObjectResource,
    StandardObjectResource,
)


class WorkspacesResource(StandardObjectResource):
    """Synchronous Workspaces resource (convenience wrapper around Records)."""

    _object_slug = "workspaces"


# --- GENERATED ASYNC CODE BELOW --- #


class AsyncWorkspacesResource(AsyncStandardObjectResource):
    """Asynchronous Workspaces resource (convenience wrapper around Records)."""

    _object_slug = "workspaces"
