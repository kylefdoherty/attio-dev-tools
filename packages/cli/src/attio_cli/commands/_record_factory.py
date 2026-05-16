"""Factory for building record-command Typer groups.

Eliminates copy-paste duplication across people, companies, deals, and records
modules.  Each known object (people, companies, deals) becomes a thin
registration; the generic ``records`` module gets the same commands with an
extra ``--object`` flag.
"""

from __future__ import annotations

import sys
from typing import Any, Callable, Optional

import typer

from attio_cli._client import get_client
from attio_cli._errors import handle_api_error
from attio_cli._output import output_list, output_single, output_success
from attio_cli._values import expand_values
from attio_cli.commands._record_helpers import (
    ENTRY_LIST_COLUMNS,
    GENERIC_COLUMNS,
    VALUE_COLUMNS,
    parse_json_option,
    record_to_dict,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _get_sub_client(client: Any, slug: str) -> Any:
    """Return the dedicated sub-client for known objects, else ``client.records``."""
    return getattr(client, slug, None) or client.records


def _singular(slug: str) -> str:
    """Derive a singular display name from an object slug.

    people -> person, companies -> company, deals -> deal, fallback strips trailing 's'.
    """
    _SINGULAR_MAP = {
        "people": "person",
        "companies": "company",
    }
    if slug in _SINGULAR_MAP:
        return _SINGULAR_MAP[slug]
    if slug.endswith("s"):
        return slug[:-1]
    return slug


def _plural_title(slug: str) -> str:
    """Capitalised plural title: 'people' -> 'People'."""
    return slug.replace("_", " ").replace("-", " ").title()


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------


def create_record_commands(
    object_slug: str,
    *,
    columns: list[dict[str, Any]] | None = None,
    is_generic: bool = False,
    extra_commands: Callable[[typer.Typer], None] | None = None,
) -> typer.Typer:
    """Build a complete Typer command group for a record object.

    Parameters
    ----------
    object_slug:
        The Attio object API slug (``people``, ``companies``, ``deals``, ...).
    columns:
        Column definitions for ``output_list`` in the ``list`` command.
        Falls back to ``GENERIC_COLUMNS``.
    is_generic:
        When *True* every sub-command gets an ``--object`` option and calls go
        through ``client.records.*`` with the slug as the first positional arg.
        This is the behaviour for the ``records`` command group.
    extra_commands:
        Optional callback that receives the ``typer.Typer`` to attach
        additional sub-commands (e.g. the ``move`` command on deals).
    """

    cols = columns or GENERIC_COLUMNS
    singular = _singular(object_slug)
    plural = _plural_title(object_slug)

    app = typer.Typer(no_args_is_help=True)

    # -- helpers for calling the right client method -----------------------

    def _sub(client: Any, slug: str) -> Any:
        """Get the right SDK sub-client."""
        if is_generic:
            return client.records
        return getattr(client, slug)

    def _call(method: Any, slug: str, *args: Any, **kwargs: Any) -> Any:
        """Call *method* prepending *slug* only in generic mode."""
        if is_generic:
            return method(slug, *args, **kwargs)
        return method(*args, **kwargs)

    # -- object slug option for generic mode --------------------------------

    _object_option = typer.Option(
        ..., "--object", help="Object slug (e.g., people, companies, or custom)."
    )

    def _slug(object_arg: str | None) -> str:
        return object_arg if is_generic and object_arg else object_slug

    # ======================================================================
    # list
    # ======================================================================

    if is_generic:
        @app.command("list")
        def list_records(
            ctx: typer.Context,
            object: str = _object_option,
            limit: int = typer.Option(25, help="Maximum number of results."),
            offset: int = typer.Option(0, help="Pagination offset."),
            filter: Optional[str] = typer.Option(None, "--filter", help="Raw filter JSON."),
            sort: Optional[str] = typer.Option(None, help="Sort by attribute slug."),
            sort_direction: str = typer.Option("asc", help="Sort direction: asc or desc."),
            all_results: bool = typer.Option(False, "--all", help="Fetch all results."),
        ) -> None:
            """List records for a given object with optional filtering and sorting."""
            slug = _slug(object)
            client = get_client(ctx)
            try:
                if all_results:
                    filter_obj = parse_json_option(filter) if filter else None
                    iterator = _call(_sub(client, slug).query_all, slug, filter=filter_obj)
                    all_data = [record_to_dict(r) for r in iterator]
                    output_list(all_data, cols, ctx, title=f"Records ({slug}) (all)")
                    return

                filter_obj = parse_json_option(filter)
                if filter_obj or sort:
                    from attio.models.records import Sort as SortModel

                    sorts = [SortModel(attribute=sort, direction=sort_direction)] if sort else None
                    result = _call(
                        _sub(client, slug).query, slug,
                        filter=filter_obj, sorts=sorts, limit=limit, offset=offset,
                    )
                else:
                    result = _call(_sub(client, slug).list, slug, limit=limit, offset=offset)
                data = [record_to_dict(r) for r in result.data]
                output_list(data, cols, ctx, title=f"Records ({slug})")
            except SystemExit:
                raise
            except Exception as e:
                handle_api_error(e, ctx)
    else:
        @app.command("list")
        def list_records(
            ctx: typer.Context,
            limit: int = typer.Option(25, help="Maximum number of results."),
            offset: int = typer.Option(0, help="Pagination offset."),
            filter: Optional[str] = typer.Option(None, "--filter", help="Raw filter JSON."),
            sort: Optional[str] = typer.Option(None, help="Sort by attribute slug."),
            sort_direction: str = typer.Option("asc", help="Sort direction: asc or desc."),
            all_results: bool = typer.Option(False, "--all", help="Fetch all results."),
        ) -> None:
            _list_records_impl(ctx, object_slug, limit, offset, filter, sort, sort_direction, all_results, cols, plural)

        list_records.__doc__ = f"List {singular} records with optional filtering and sorting."

    # ======================================================================
    # get
    # ======================================================================

    if is_generic:
        @app.command()
        def get(
            ctx: typer.Context,
            record_id: str = typer.Argument(help="The record ID to retrieve."),
            object: str = _object_option,
        ) -> None:
            """Get a record by ID."""
            slug = _slug(object)
            client = get_client(ctx)
            try:
                record = _call(_sub(client, slug).get, slug, record_id)
                data = record_to_dict(record)
                output_single(data, ctx, title=f"Record {record_id}")
            except SystemExit:
                raise
            except Exception as e:
                handle_api_error(e, ctx)
    else:
        @app.command()
        def get(
            ctx: typer.Context,
            record_id: str = typer.Argument(help="The record ID to retrieve."),
        ) -> None:
            _get_impl(ctx, object_slug, record_id, singular)

        get.__doc__ = f"Get a {singular} by record ID."

    # ======================================================================
    # create
    # ======================================================================

    if is_generic:
        @app.command()
        def create(
            ctx: typer.Context,
            object: str = _object_option,
            values: str = typer.Option(..., "--values", help="JSON object of attribute values."),
        ) -> None:
            """Create a new record."""
            slug = _slug(object)
            client = get_client(ctx)
            try:
                values_obj = parse_json_option(values)
                if not values_obj:
                    raise typer.BadParameter("--values must be a non-empty JSON object.")
                values_obj = expand_values(client, slug, values_obj)
                record = _call(_sub(client, slug).create, slug, values=values_obj)
                data = record_to_dict(record)
                output_single(data, ctx, title="Created Record")
            except SystemExit:
                raise
            except Exception as e:
                handle_api_error(e, ctx)
    else:
        @app.command()
        def create(
            ctx: typer.Context,
            values: str = typer.Option(..., "--values", help="JSON object of attribute values."),
        ) -> None:
            _create_impl(ctx, object_slug, values, singular)

        create.__doc__ = f"Create a new {singular} record."

    # ======================================================================
    # update
    # ======================================================================

    if is_generic:
        @app.command()
        def update(
            ctx: typer.Context,
            record_id: str = typer.Argument(help="The record ID to update."),
            object: str = _object_option,
            values: str = typer.Option(..., "--values", help="JSON object of attribute values."),
        ) -> None:
            """Update an existing record."""
            slug = _slug(object)
            client = get_client(ctx)
            try:
                values_obj = parse_json_option(values)
                if not values_obj:
                    raise typer.BadParameter("--values must be a non-empty JSON object.")
                values_obj = expand_values(client, slug, values_obj)
                record = _call(_sub(client, slug).update, slug, record_id, values=values_obj)
                data = record_to_dict(record)
                output_single(data, ctx, title="Updated Record")
            except SystemExit:
                raise
            except Exception as e:
                handle_api_error(e, ctx)
    else:
        @app.command()
        def update(
            ctx: typer.Context,
            record_id: str = typer.Argument(help="The record ID to update."),
            values: str = typer.Option(..., "--values", help="JSON object of attribute values."),
        ) -> None:
            _update_impl(ctx, object_slug, record_id, values, singular)

        update.__doc__ = f"Update an existing {singular} record."

    # ======================================================================
    # upsert
    # ======================================================================

    if is_generic:
        @app.command()
        def upsert(
            ctx: typer.Context,
            object: str = _object_option,
            matching_attribute: str = typer.Option(..., "--matching-attribute", help="Attribute slug to match on."),
            values: str = typer.Option(..., "--values", help="JSON object of attribute values."),
        ) -> None:
            """Create or update a record by matching attribute."""
            slug = _slug(object)
            client = get_client(ctx)
            try:
                values_obj = parse_json_option(values)
                if not values_obj:
                    raise typer.BadParameter("--values must be a non-empty JSON object.")
                values_obj = expand_values(client, slug, values_obj)
                record = _call(
                    _sub(client, slug).upsert, slug,
                    matching_attribute=matching_attribute, values=values_obj,
                )
                data = record_to_dict(record)
                output_single(data, ctx, title="Upserted Record")
            except SystemExit:
                raise
            except Exception as e:
                handle_api_error(e, ctx)
    else:
        @app.command()
        def upsert(
            ctx: typer.Context,
            matching_attribute: str = typer.Option(..., "--matching-attribute", help="Attribute slug to match on."),
            values: str = typer.Option(..., "--values", help="JSON object of attribute values."),
        ) -> None:
            _upsert_impl(ctx, object_slug, matching_attribute, values, singular)

        upsert.__doc__ = f"Create or update a {singular} by matching attribute."

    # ======================================================================
    # delete
    # ======================================================================

    if is_generic:
        @app.command()
        def delete(
            ctx: typer.Context,
            record_id: str = typer.Argument(help="The record ID to delete."),
            object: str = _object_option,
            yes: bool = typer.Option(False, "--yes", "-y", help="Skip confirmation."),
        ) -> None:
            """Delete a record."""
            slug = _slug(object)
            if not yes and sys.stdout.isatty():
                typer.confirm(f"Delete record {record_id} from {slug}?", abort=True)
            client = get_client(ctx)
            try:
                _call(_sub(client, slug).delete, slug, record_id)
                output_success(f"Deleted record {record_id} from {slug}", ctx)
            except SystemExit:
                raise
            except Exception as e:
                handle_api_error(e, ctx)
    else:
        @app.command()
        def delete(
            ctx: typer.Context,
            record_id: str = typer.Argument(help="The record ID to delete."),
            yes: bool = typer.Option(False, "--yes", "-y", help="Skip confirmation."),
        ) -> None:
            _delete_impl(ctx, object_slug, record_id, yes, singular)

        delete.__doc__ = f"Delete a {singular} record."

    # ======================================================================
    # search
    # ======================================================================

    if is_generic:
        @app.command()
        def search(
            ctx: typer.Context,
            query: str = typer.Argument(help="Search query string."),
            object: str = typer.Option(..., "--object", help="Object slug to search within."),
            limit: int = typer.Option(25, help="Maximum number of results."),
        ) -> None:
            """Search records within a specific object."""
            slug = _slug(object)
            client = get_client(ctx)
            try:
                result = client.records.global_search(query=query, objects=[slug], limit=limit)
                data = [
                    {"record_id": r.id.record_id, "text": r.record_text, "object": r.object_slug}
                    for r in result.data
                ]
                search_columns = [
                    {"header": "ID", "accessor": lambda r: r.get("record_id", ""), "no_wrap": True},
                    {"header": "Match", "accessor": lambda r: r.get("text", "")},
                    {"header": "Object", "accessor": lambda r: r.get("object", "")},
                ]
                output_list(data, search_columns, ctx, title=f"Search Results ({slug})")
            except SystemExit:
                raise
            except Exception as e:
                handle_api_error(e, ctx)
    else:
        @app.command()
        def search(
            ctx: typer.Context,
            query: str = typer.Argument(help="Search query string."),
            limit: int = typer.Option(25, help="Maximum number of results."),
        ) -> None:
            _search_impl(ctx, object_slug, query, limit, plural)

        search.__doc__ = f"Search {singular} records."

    # ======================================================================
    # append
    # ======================================================================

    if is_generic:
        @app.command()
        def append(
            ctx: typer.Context,
            record_id: str = typer.Argument(help="Record ID."),
            object: str = _object_option,
            values: str = typer.Option(..., "--values", help="JSON values to append."),
        ) -> None:
            """Append values to a record (adds to multiselect fields without overwriting)."""
            slug = _slug(object)
            client = get_client(ctx)
            try:
                values_obj = parse_json_option(values)
                if not values_obj:
                    raise typer.BadParameter("--values must be a non-empty JSON object.")
                values_obj = expand_values(client, slug, values_obj)
                result = _call(_sub(client, slug).append, slug, record_id, values=values_obj)
                output_single(record_to_dict(result), ctx, title=f"Appended Record {record_id}")
            except SystemExit:
                raise
            except Exception as e:
                handle_api_error(e, ctx)
    else:
        @app.command()
        def append(
            ctx: typer.Context,
            record_id: str = typer.Argument(help="Record ID to append values to."),
            values: str = typer.Option(..., "--values", help="JSON values to append."),
        ) -> None:
            """Append values to a record (adds to multiselect fields without overwriting)."""
            _append_impl(ctx, object_slug, record_id, values, singular)

    # ======================================================================
    # values
    # ======================================================================

    if is_generic:
        @app.command("values")
        def get_values(
            ctx: typer.Context,
            record_id: str = typer.Argument(help="Record ID."),
            object: str = _object_option,
            attribute: str = typer.Option(..., "--attribute", help="Attribute slug or ID."),
            show_historic: bool = typer.Option(False, "--show-historic", help="Include historical values."),
            limit: int = typer.Option(25, "--limit", help="Maximum number of results."),
            offset: int = typer.Option(0, "--offset", help="Pagination offset."),
        ) -> None:
            """Get attribute values for a record."""
            slug = _slug(object)
            client = get_client(ctx)
            try:
                result = _call(
                    _sub(client, slug).get_attribute_values, slug,
                    record_id, attribute,
                    show_historic=show_historic, limit=limit, offset=offset,
                )
                output_list(
                    [v.model_dump(mode="json") for v in result.data],
                    VALUE_COLUMNS,
                    ctx,
                    title=f"Values: {attribute}",
                )
            except SystemExit:
                raise
            except Exception as e:
                handle_api_error(e, ctx)
    else:
        @app.command("values")
        def get_values(
            ctx: typer.Context,
            record_id: str = typer.Argument(help="Record ID."),
            attribute: str = typer.Option(..., "--attribute", help="Attribute slug or ID."),
            show_historic: bool = typer.Option(False, "--show-historic", help="Include historical values."),
            limit: int = typer.Option(25, "--limit", help="Maximum number of results."),
            offset: int = typer.Option(0, "--offset", help="Pagination offset."),
        ) -> None:
            """Get attribute values for a record."""
            _values_impl(ctx, object_slug, record_id, attribute, show_historic, limit, offset)

    # ======================================================================
    # entries
    # ======================================================================

    if is_generic:
        @app.command("entries")
        def list_entries(
            ctx: typer.Context,
            record_id: str = typer.Argument(help="Record ID."),
            object: str = _object_option,
            limit: int = typer.Option(25, "--limit", help="Maximum number of results."),
            offset: int = typer.Option(0, "--offset", help="Pagination offset."),
        ) -> None:
            """List entries (list memberships) for a record."""
            slug = _slug(object)
            client = get_client(ctx)
            try:
                result = _call(
                    _sub(client, slug).list_entries, slug,
                    record_id, limit=limit, offset=offset,
                )
                entry_dicts = [
                    {
                        "list_id": e.list_id,
                        "list_slug": e.list_api_slug,
                        "entry_id": e.entry_id,
                        "created_at": str(e.created_at),
                    }
                    for e in result.data
                ]
                output_list(entry_dicts, ENTRY_LIST_COLUMNS, ctx, title="Record Entries")
            except SystemExit:
                raise
            except Exception as e:
                handle_api_error(e, ctx)
    else:
        @app.command("entries")
        def list_entries(
            ctx: typer.Context,
            record_id: str = typer.Argument(help="Record ID."),
            limit: int = typer.Option(25, "--limit", help="Maximum number of results."),
            offset: int = typer.Option(0, "--offset", help="Pagination offset."),
        ) -> None:
            """List entries (list memberships) for a record."""
            _entries_impl(ctx, object_slug, record_id, limit, offset)

    # -- attach any extra commands (e.g. deals move) -----------------------
    if extra_commands is not None:
        extra_commands(app)

    return app


# ==========================================================================
# Implementation functions for known-object (non-generic) commands
# ==========================================================================
# These are called by the thin Typer wrappers created above.  They use the
# dedicated sub-client (``client.people``, ``client.companies``, etc.).


def _list_records_impl(
    ctx: typer.Context,
    slug: str,
    limit: int,
    offset: int,
    filter: str | None,
    sort: str | None,
    sort_direction: str,
    all_results: bool,
    cols: list[dict[str, Any]],
    plural: str,
) -> None:
    client = get_client(ctx)
    sub = getattr(client, slug)
    try:
        if all_results:
            filter_obj = parse_json_option(filter) if filter else None
            iterator = sub.query_all(filter=filter_obj)
            all_data = [record_to_dict(r) for r in iterator]
            output_list(all_data, cols, ctx, title=f"{plural} (all)")
            return

        filter_obj = parse_json_option(filter)
        if filter_obj or sort:
            from attio.models.records import Sort as SortModel

            sorts = [SortModel(attribute=sort, direction=sort_direction)] if sort else None
            result = sub.query(filter=filter_obj, sorts=sorts, limit=limit, offset=offset)
        else:
            result = sub.list(limit=limit, offset=offset)
        data = [record_to_dict(r) for r in result.data]
        output_list(data, cols, ctx, title=plural)
    except SystemExit:
        raise
    except Exception as e:
        handle_api_error(e, ctx)


def _get_impl(
    ctx: typer.Context,
    slug: str,
    record_id: str,
    singular: str,
) -> None:
    client = get_client(ctx)
    sub = getattr(client, slug)
    try:
        record = sub.get(record_id)
        data = record_to_dict(record)
        output_single(data, ctx, title=f"{singular.title()} {record_id}")
    except SystemExit:
        raise
    except Exception as e:
        handle_api_error(e, ctx)


def _create_impl(
    ctx: typer.Context,
    slug: str,
    values: str,
    singular: str,
) -> None:
    client = get_client(ctx)
    sub = getattr(client, slug)
    try:
        values_obj = parse_json_option(values)
        if not values_obj:
            raise typer.BadParameter("--values must be a non-empty JSON object.")
        values_obj = expand_values(client, slug, values_obj)
        record = sub.create(values=values_obj)
        data = record_to_dict(record)
        output_single(data, ctx, title=f"Created {singular.title()}")
    except SystemExit:
        raise
    except Exception as e:
        handle_api_error(e, ctx)


def _update_impl(
    ctx: typer.Context,
    slug: str,
    record_id: str,
    values: str,
    singular: str,
) -> None:
    client = get_client(ctx)
    sub = getattr(client, slug)
    try:
        values_obj = parse_json_option(values)
        if not values_obj:
            raise typer.BadParameter("--values must be a non-empty JSON object.")
        values_obj = expand_values(client, slug, values_obj)
        record = sub.update(record_id, values=values_obj)
        data = record_to_dict(record)
        output_single(data, ctx, title=f"Updated {singular.title()}")
    except SystemExit:
        raise
    except Exception as e:
        handle_api_error(e, ctx)


def _upsert_impl(
    ctx: typer.Context,
    slug: str,
    matching_attribute: str,
    values: str,
    singular: str,
) -> None:
    client = get_client(ctx)
    sub = getattr(client, slug)
    try:
        values_obj = parse_json_option(values)
        if not values_obj:
            raise typer.BadParameter("--values must be a non-empty JSON object.")
        values_obj = expand_values(client, slug, values_obj)
        record = sub.upsert(matching_attribute=matching_attribute, values=values_obj)
        data = record_to_dict(record)
        output_single(data, ctx, title=f"Upserted {singular.title()}")
    except SystemExit:
        raise
    except Exception as e:
        handle_api_error(e, ctx)


def _delete_impl(
    ctx: typer.Context,
    slug: str,
    record_id: str,
    yes: bool,
    singular: str,
) -> None:
    if not yes and sys.stdout.isatty():
        typer.confirm(f"Delete {singular} {record_id}?", abort=True)
    client = get_client(ctx)
    sub = getattr(client, slug)
    try:
        sub.delete(record_id)
        output_success(f"Deleted {singular} {record_id}", ctx)
    except SystemExit:
        raise
    except Exception as e:
        handle_api_error(e, ctx)


def _search_impl(
    ctx: typer.Context,
    slug: str,
    query: str,
    limit: int,
    plural: str,
) -> None:
    client = get_client(ctx)
    try:
        result = client.records.global_search(query=query, objects=[slug], limit=limit)
        data = [
            {"record_id": r.id.record_id, "text": r.record_text, "object": r.object_slug}
            for r in result.data
        ]
        search_columns = [
            {"header": "ID", "accessor": lambda r: r.get("record_id", ""), "no_wrap": True},
            {"header": "Match", "accessor": lambda r: r.get("text", "")},
        ]
        output_list(data, search_columns, ctx, title=f"{plural} Search Results")
    except SystemExit:
        raise
    except Exception as e:
        handle_api_error(e, ctx)


def _append_impl(
    ctx: typer.Context,
    slug: str,
    record_id: str,
    values: str,
    singular: str,
) -> None:
    client = get_client(ctx)
    sub = getattr(client, slug)
    try:
        values_obj = parse_json_option(values)
        if not values_obj:
            raise typer.BadParameter("--values must be a non-empty JSON object.")
        values_obj = expand_values(client, slug, values_obj)
        result = sub.append(record_id, values=values_obj)
        output_single(record_to_dict(result), ctx, title=f"Appended {singular.title()} {record_id}")
    except SystemExit:
        raise
    except Exception as e:
        handle_api_error(e, ctx)


def _values_impl(
    ctx: typer.Context,
    slug: str,
    record_id: str,
    attribute: str,
    show_historic: bool,
    limit: int,
    offset: int,
) -> None:
    client = get_client(ctx)
    sub = getattr(client, slug)
    try:
        result = sub.get_attribute_values(
            record_id, attribute, show_historic=show_historic, limit=limit, offset=offset
        )
        output_list(
            [v.model_dump(mode="json") for v in result.data],
            VALUE_COLUMNS,
            ctx,
            title=f"Values: {attribute}",
        )
    except SystemExit:
        raise
    except Exception as e:
        handle_api_error(e, ctx)


def _entries_impl(
    ctx: typer.Context,
    slug: str,
    record_id: str,
    limit: int,
    offset: int,
) -> None:
    client = get_client(ctx)
    sub = getattr(client, slug)
    try:
        result = sub.list_entries(record_id, limit=limit, offset=offset)
        entry_dicts = [
            {
                "list_id": e.list_id,
                "list_slug": e.list_api_slug,
                "entry_id": e.entry_id,
                "created_at": str(e.created_at),
            }
            for e in result.data
        ]
        output_list(entry_dicts, ENTRY_LIST_COLUMNS, ctx, title="Record Entries")
    except SystemExit:
        raise
    except Exception as e:
        handle_api_error(e, ctx)
