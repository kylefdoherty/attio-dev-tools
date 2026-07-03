#!/usr/bin/env python3
"""Generate async resource classes from sync resource classes.

This script reads each resource file in src/attio/resources/, extracts the sync
resource class source text, and generates the corresponding async class via
targeted text replacements.  The generated async class is written back into
the same file below a ``# --- GENERATED ASYNC CODE BELOW --- #`` marker.

The sync class + mixin are the single source of truth; the async class is
always derived.  Run this script after editing any resource method.

Usage:
    python scripts/generate_async.py          # regenerate all
    python scripts/generate_async.py notes    # regenerate just notes.py
"""

from __future__ import annotations

import ast
import re
import sys
from pathlib import Path

RESOURCES_DIR = Path(__file__).resolve().parent.parent / "src" / "attio" / "resources"

MARKER = "# --- GENERATED ASYNC CODE BELOW --- #"

# Files to skip entirely (no sync/async duplication pattern)
SKIP_FILES = {"__init__.py", "_base.py"}

# Sync base class -> Async base class mapping (for text replacement in class def line)
SYNC_TO_ASYNC_BASE = {
    "SyncResource": "AsyncResource",
    "SyncQueryableResource": "AsyncQueryableResource",
    "StandardObjectResource": "AsyncStandardObjectResource",
}

# Explicit sync class name -> async class name mapping for non-standard names
CLASS_NAME_MAP = {
    "SyncQueryableResource": "AsyncQueryableResource",
}

# Sync iterator -> Async iterator mapping
ITERATOR_MAP = {
    "OffsetIterator": "AsyncOffsetIterator",
    "CursorIterator": "AsyncCursorIterator",
}

# Patterns for delegate calls that also need `await` (records/entries calling base _list, _query, etc.)
DELEGATE_AWAIT_RE = re.compile(
    r"self\._(list|query|get|update|append|delete|get_attribute_values|query_all)\("
)

# Standard object delegate pattern
RECORDS_DELEGATE_RE = re.compile(r"self\._records\.\w+\(")


def _find_all_classes(source: str) -> list[ast.ClassDef]:
    """Return all top-level ClassDef nodes in source order."""
    tree = ast.parse(source)
    return [n for n in ast.iter_child_nodes(tree) if isinstance(n, ast.ClassDef)]


def _get_base_names_raw(cls: ast.ClassDef) -> list[str]:
    """Get base class names as raw strings, handling Subscript (Generic) bases."""
    names = []
    for base in cls.bases:
        if isinstance(base, ast.Name):
            names.append(base.id)
        elif isinstance(base, ast.Subscript) and isinstance(base.value, ast.Name):
            names.append(base.value.id)
    return names


def _is_sync_class(cls: ast.ClassDef) -> bool:
    """Check if a class is a sync resource class (inherits from any sync base)."""
    return bool(set(_get_base_names_raw(cls)) & set(SYNC_TO_ASYNC_BASE.keys()))


def _async_class_name(sync_name: str) -> str:
    """Determine the async class name from a sync class name."""
    if sync_name in CLASS_NAME_MAP:
        return CLASS_NAME_MAP[sync_name]
    return f"Async{sync_name}"


def _extract_class_text(source: str, cls: ast.ClassDef, boundary: int) -> str:
    """Extract the exact source text of a class, ending before boundary line."""
    lines = source.split("\n")
    start = cls.lineno - 1  # 0-indexed
    end = boundary

    # Trim trailing blank lines
    while end > start and lines[end - 1].strip() == "":
        end -= 1

    return "\n".join(lines[start:end])


def _find_boundary_after_sync(source: str, sync_cls: ast.ClassDef, all_classes: list[ast.ClassDef]) -> int:
    """Find the line index where the sync class ends."""
    lines = source.split("\n")
    end = len(lines)

    # Check for classes after the sync class
    for cls in all_classes:
        if cls.lineno > sync_cls.lineno:
            candidate = cls.lineno - 1
            while candidate > sync_cls.lineno and lines[candidate - 1].strip() == "":
                candidate -= 1
            if candidate < end:
                end = candidate
            break

    # Check for the marker
    for i, line in enumerate(lines):
        if MARKER in line:
            candidate = i
            while candidate > sync_cls.lineno and lines[candidate - 1].strip() == "":
                candidate -= 1
            if sync_cls.lineno - 1 < candidate < end:
                end = candidate
            break

    # Also check for section comment blocks (like "# ---" lines) that precede the async class
    for i in range(sync_cls.lineno, len(lines)):
        line = lines[i].strip()
        if line.startswith("# ---") and i > sync_cls.lineno:
            # Walk back to find where this section header block starts
            candidate = i
            while candidate > sync_cls.lineno and lines[candidate - 1].strip() == "":
                candidate -= 1
            if sync_cls.lineno - 1 < candidate < end:
                end = candidate
            break

    return end


def _get_header(source: str, sync_cls: ast.ClassDef, all_classes: list[ast.ClassDef]) -> str:
    """Get everything from the file start through the end of the sync class."""
    boundary = _find_boundary_after_sync(source, sync_cls, all_classes)
    lines = source.split("\n")[:boundary]
    while lines and lines[-1].strip() == "":
        lines.pop()
    return "\n".join(lines)


def _method_has_awaitable_calls(method: ast.FunctionDef, is_standard_object: bool = False) -> bool:
    """Check if a method body has calls that need to be awaited."""
    for node in ast.walk(method):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
            # self._http.request / request_multipart
            if isinstance(node.func.value, ast.Attribute) and isinstance(node.func.value.value, ast.Name):
                if node.func.value.value.id == "self":
                    if node.func.value.attr == "_http" and node.func.attr in (
                        "request",
                        "request_multipart",
                        "request_redirect_url",
                    ):
                        return True
                    if is_standard_object and node.func.value.attr == "_records":
                        return True
            # self._list, self._query, etc. (delegate calls)
            if isinstance(node.func.value, ast.Name) and node.func.value.id == "self":
                candidate = f"self.{node.func.attr}("
                if DELEGATE_AWAIT_RE.match(candidate):
                    return True
    return False


def _is_paginator_method(method: ast.FunctionDef) -> bool:
    """Check if a method is a paginator (query_all, list_all_*) that returns an iterator.

    These methods should NOT be made async; they only need iterator type renames.
    """
    if method.name in ("query_all", "list_all", "get_all") or method.name.startswith("list_all_"):
        return True
    if method.name.startswith("_query_all") or method.name.startswith("_list_all_"):
        return True
    return False


def _method_has_inner_function(method: ast.FunctionDef) -> bool:
    """Check if a method contains an inner function definition."""
    return any(isinstance(node, ast.FunctionDef) for node in method.body)


def _transform_class_text(
    class_text: str,
    sync_cls: ast.ClassDef,
    is_standard_object: bool = False,
) -> str:
    """Transform sync class source text into async class source text."""
    result = class_text
    sync_name = sync_cls.name
    async_name = _async_class_name(sync_name)

    # --- Class declaration line ---
    result = result.replace(f"class {sync_name}", f"class {async_name}", 1)

    # Replace sync base class with async base class in the class def line
    for sync_base, async_base in SYNC_TO_ASYNC_BASE.items():
        # Handle generic bases: SyncQueryableResource[T] -> AsyncQueryableResource[T]
        result = result.replace(f"({sync_base}[", f"({async_base}[", 1)
        result = result.replace(f"({sync_base},", f"({async_base},", 1)
        result = result.replace(f"({sync_base})", f"({async_base})", 1)

    # Replace "Synchronous" / "(sync)" in the class docstring (first occurrence only)
    result = result.replace("Synchronous", "Asynchronous", 1)
    result = result.replace("(sync)", "(async)", 1)

    # For standard objects, update __init__ parameter type
    if is_standard_object:
        result = result.replace("records: RecordsResource", "records: AsyncRecordsResource")

    # --- Process methods ---
    methods = [n for n in sync_cls.body if isinstance(n, ast.FunctionDef)]
    lines = result.split("\n")
    class_start = sync_cls.lineno  # 1-indexed (first line of class source is line class_start)

    # Process methods from bottom to top so line offsets remain valid
    for method in reversed(methods):
        if _is_paginator_method(method):
            # Paginator methods: update types/inner functions, but do NOT make async
            lines = _transform_paginator_method_lines(
                lines, method, class_start, is_standard_object
            )
        elif _method_has_awaitable_calls(method, is_standard_object):
            lines = _transform_async_method_lines(
                lines, method, class_start, is_standard_object
            )

    return "\n".join(lines)


def _transform_async_method_lines(
    lines: list[str],
    method: ast.FunctionDef,
    class_start: int,
    is_standard_object: bool,
) -> list[str]:
    """Add async/await to a regular method."""
    method_offset = method.lineno - class_start  # 0-indexed in lines

    # Add 'async' to the def line
    def_line = lines[method_offset]
    stripped = def_line.lstrip()
    indent = def_line[:len(def_line) - len(stripped)]
    if stripped.startswith("def "):
        lines[method_offset] = f"{indent}async {stripped}"

    # Add 'await' to all calls that need it
    for node in ast.walk(method):
        if not isinstance(node, ast.Call) or not isinstance(node.func, ast.Attribute):
            continue

        should_await = False
        call_text = None

        # self._http.request(...) / self._http.request_multipart(...)
        if isinstance(node.func.value, ast.Attribute) and isinstance(node.func.value.value, ast.Name):
            if node.func.value.value.id == "self":
                if node.func.value.attr == "_http" and node.func.attr in (
                    "request",
                    "request_multipart",
                    "request_redirect_url",
                ):
                    should_await = True
                    call_text = f"self._http.{node.func.attr}("
                elif is_standard_object and node.func.value.attr == "_records":
                    should_await = True
                    call_text = f"self._records.{node.func.attr}("

        # self._list(...), self._query(...), etc.
        if isinstance(node.func.value, ast.Name) and node.func.value.id == "self":
            candidate = f"self.{node.func.attr}("
            if DELEGATE_AWAIT_RE.match(candidate):
                should_await = True
                call_text = candidate

        if should_await and call_text:
            call_line_offset = node.lineno - class_start
            if 0 <= call_line_offset < len(lines) and call_text in lines[call_line_offset]:
                lines[call_line_offset] = _insert_await(lines[call_line_offset], call_text)

    return lines


def _insert_await(line: str, call_text: str) -> str:
    """Insert 'await' before a call pattern in a line."""
    idx = line.index(call_text)
    before = line[:idx].rstrip()

    if before.endswith("="):
        return f"{before} await {line[idx:]}"
    elif before.endswith("return"):
        return f"{before} await {line[idx:]}"
    else:
        indent = line[:idx]
        return f"{indent}await {line[idx:]}"


def _find_method_end(lines: list[str], method: ast.FunctionDef, class_start: int) -> int:
    """Find the end line (exclusive) of a method in the class text lines.

    Uses AST end_lineno if available, otherwise falls back to indent-based detection.
    """
    method_offset = method.lineno - class_start

    if hasattr(method, "end_lineno") and method.end_lineno is not None:
        return method.end_lineno - class_start + 1

    # Fallback: indent-based detection
    base_indent = len(lines[method_offset]) - len(lines[method_offset].lstrip())
    method_end = method_offset + 1
    while method_end < len(lines):
        line = lines[method_end]
        stripped = line.strip()
        if stripped and (len(line) - len(line.lstrip())) <= base_indent:
            # Don't break on the closing paren of the function signature
            if not (stripped.startswith(")") and stripped.endswith(":")):
                break
        method_end += 1
    return method_end


def _transform_paginator_method_lines(
    lines: list[str],
    method: ast.FunctionDef,
    class_start: int,
    is_standard_object: bool,
) -> list[str]:
    """Transform a query_all or list_all_* method."""
    method_offset = method.lineno - class_start
    method_end = _find_method_end(lines, method, class_start)

    # Process all lines: update return type annotation and docstring
    for i in range(method_offset, method_end):
        line = lines[i]
        for sync_name, async_name in ITERATOR_MAP.items():
            if sync_name in line and async_name not in line:
                lines[i] = line.replace(sync_name, async_name)
                line = lines[i]
        if "Returns an iterator" in line:
            lines[i] = line.replace("Returns an iterator", "Returns an async iterator")

    if is_standard_object:
        return lines

    # Transform inner function: def -> async def, add await to self.xxx() calls
    for node in method.body:
        if isinstance(node, ast.FunctionDef):
            inner_offset = node.lineno - class_start
            inner_line = lines[inner_offset]
            stripped = inner_line.lstrip()
            indent = inner_line[:len(inner_line) - len(stripped)]
            if stripped.startswith("def "):
                lines[inner_offset] = f"{indent}async {stripped}"

            for inner_node in ast.walk(node):
                if isinstance(inner_node, ast.Call) and isinstance(inner_node.func, ast.Attribute):
                    if isinstance(inner_node.func.value, ast.Name) and inner_node.func.value.id == "self":
                        call_text = f"self.{inner_node.func.attr}("
                        call_offset = inner_node.lineno - class_start
                        if 0 <= call_offset < len(lines) and call_text in lines[call_offset]:
                            lines[call_offset] = _insert_await(lines[call_offset], call_text)

        # Note: iterator class names in return statements and local imports are
        # already handled by the general line-scan loop above (lines 329-337),
        # so no separate handler is needed here.

    return lines


# ---------------------------------------------------------------------------
# File processors
# ---------------------------------------------------------------------------


def process_resource_file(filepath: Path) -> bool:
    """Process a resource file with SyncResource or SyncQueryableResource base."""
    source = filepath.read_text()
    all_classes = _find_all_classes(source)

    sync_cls = None
    for cls in all_classes:
        if _is_sync_class(cls):
            sync_cls = cls
            break

    if sync_cls is None:
        return False

    boundary = _find_boundary_after_sync(source, sync_cls, all_classes)
    class_text = _extract_class_text(source, sync_cls, boundary)
    async_text = _transform_class_text(class_text, sync_cls)

    header = _get_header(source, sync_cls, all_classes)
    new_content = f"{header}\n\n\n{MARKER}\n\n\n{async_text}\n"

    if new_content == source:
        return False

    filepath.write_text(new_content)
    return True


def process_standard_object_file(filepath: Path) -> bool:
    """Process _standard_object.py."""
    source = filepath.read_text()
    all_classes = _find_all_classes(source)

    sync_cls = None
    for cls in all_classes:
        if cls.name == "StandardObjectResource":
            sync_cls = cls
            break

    if sync_cls is None:
        return False

    boundary = _find_boundary_after_sync(source, sync_cls, all_classes)
    class_text = _extract_class_text(source, sync_cls, boundary)
    async_text = _transform_class_text(class_text, sync_cls, is_standard_object=True)

    header = _get_header(source, sync_cls, all_classes)
    new_content = f"{header}\n\n\n{MARKER}\n\n\n{async_text}\n"

    if new_content == source:
        return False

    filepath.write_text(new_content)
    return True


def process_queryable_file(filepath: Path) -> bool:
    """Process _queryable.py."""
    source = filepath.read_text()
    all_classes = _find_all_classes(source)

    sync_cls = None
    for cls in all_classes:
        if cls.name == "SyncQueryableResource":
            sync_cls = cls
            break

    if sync_cls is None:
        return False

    boundary = _find_boundary_after_sync(source, sync_cls, all_classes)
    class_text = _extract_class_text(source, sync_cls, boundary)
    async_text = _transform_class_text(class_text, sync_cls)

    # Fix docstring reference to SyncQueryableResource
    async_text = async_text.replace(
        "Mirror of ``SyncQueryableResource``",
        "Mirror of ``SyncQueryableResource``",  # Keep original reference in Mirror text
    )

    header = _get_header(source, sync_cls, all_classes)
    new_content = f"{header}\n\n\n{MARKER}\n\n\n{async_text}\n"

    if new_content == source:
        return False

    filepath.write_text(new_content)
    return True


def process_simple_wrapper(filepath: Path) -> bool:
    """Process simple standard object wrapper files like people.py."""
    source = filepath.read_text()
    all_classes = _find_all_classes(source)

    sync_cls = None
    for cls in all_classes:
        if "StandardObjectResource" in _get_base_names_raw(cls) and not cls.name.startswith("Async"):
            sync_cls = cls
            break

    if sync_cls is None:
        return False

    boundary = _find_boundary_after_sync(source, sync_cls, all_classes)
    class_text = _extract_class_text(source, sync_cls, boundary)

    async_text = class_text.replace(f"class {sync_cls.name}", f"class Async{sync_cls.name}", 1)
    async_text = async_text.replace("StandardObjectResource", "AsyncStandardObjectResource", 1)
    async_text = async_text.replace("Synchronous", "Asynchronous", 1)

    header = _get_header(source, sync_cls, all_classes)
    new_content = f"{header}\n\n\n{MARKER}\n\n\n{async_text}\n"

    if new_content == source:
        return False

    filepath.write_text(new_content)
    return True


def process_file(filepath: Path) -> bool:
    """Route a file to the appropriate processor."""
    if filepath.name in SKIP_FILES:
        return False

    source = filepath.read_text()

    if filepath.name == "_queryable.py":
        return process_queryable_file(filepath)

    if filepath.name == "_standard_object.py":
        return process_standard_object_file(filepath)

    # Simple wrappers (people.py, companies.py, etc.)
    if "StandardObjectResource" in source and "SyncResource" not in source and "SyncQueryableResource" not in source:
        return process_simple_wrapper(filepath)

    # Regular resource files
    if "SyncResource" in source or "SyncQueryableResource" in source:
        return process_resource_file(filepath)

    return False


def main() -> None:
    """Main entry point."""
    if len(sys.argv) > 1:
        targets = []
        for arg in sys.argv[1:]:
            if not arg.endswith(".py"):
                arg = f"{arg}.py"
            target = RESOURCES_DIR / arg
            if not target.exists():
                print(f"Error: {target} does not exist")
                sys.exit(1)
            targets.append(target)
    else:
        targets = sorted(RESOURCES_DIR.glob("*.py"))

    modified = 0
    for filepath in targets:
        if process_file(filepath):
            modified += 1
            print(f"  Updated: {filepath.name}")
        else:
            if filepath.name not in SKIP_FILES:
                print(f"  Skipped: {filepath.name} (no changes)")

    print(f"\nDone. {modified} file(s) updated.")


if __name__ == "__main__":
    main()
