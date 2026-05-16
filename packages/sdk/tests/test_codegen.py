"""Regression tests for scripts/generate_async.py.

These tests verify that the async codegen script correctly transforms sync
resource classes into their async equivalents. They test against real resource
files in the codebase, not synthetic ones.
"""

from __future__ import annotations

import ast
import subprocess
import sys
from pathlib import Path

import pytest

# Paths
SDK_ROOT = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = SDK_ROOT / "scripts"
RESOURCES_DIR = SDK_ROOT / "src" / "attio" / "resources"

# Import the codegen module so we can test its internals where needed
sys.path.insert(0, str(SCRIPTS_DIR))
import generate_async  # noqa: E402

MARKER = generate_async.MARKER

# All resource files that should be processed (excludes __init__.py and _base.py)
SKIP_FILES = {"__init__.py", "_base.py"}


def _resource_files() -> list[Path]:
    """Return all resource files that the script processes."""
    return sorted(
        f
        for f in RESOURCES_DIR.glob("*.py")
        if f.name not in SKIP_FILES
    )


def _files_with_marker() -> list[Path]:
    """Return resource files that contain both sync and async classes (have the marker)."""
    result = []
    for f in _resource_files():
        content = f.read_text()
        if MARKER in content:
            result.append(f)
    return result


def _get_all_classes(source: str) -> list[ast.ClassDef]:
    """Parse source and return all top-level class definitions."""
    tree = ast.parse(source)
    return [n for n in ast.iter_child_nodes(tree) if isinstance(n, ast.ClassDef)]


def _get_methods(cls: ast.ClassDef) -> list[ast.FunctionDef | ast.AsyncFunctionDef]:
    """Get all method definitions from a class body."""
    return [
        n for n in cls.body
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
    ]


def _method_names(cls: ast.ClassDef) -> set[str]:
    """Get the set of method names for a class."""
    return {m.name for m in _get_methods(cls)}


def _walk_shallow(node: ast.AST):
    """Walk AST nodes without descending into nested function definitions."""
    yield node
    for child in ast.iter_child_nodes(node):
        if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        yield from _walk_shallow(child)


def _has_direct_await(func_node: ast.FunctionDef | ast.AsyncFunctionDef) -> bool:
    """Check if a function has await expressions in its own body (not in nested functions)."""
    for stmt in func_node.body:
        # Skip nested function definitions entirely -- they have their own scope
        if isinstance(stmt, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        for node in _walk_shallow(stmt):
            if isinstance(node, ast.Await):
                return True
    return False


def _find_sync_async_pairs(
    classes: list[ast.ClassDef],
) -> list[tuple[ast.ClassDef, ast.ClassDef]]:
    """Find (sync_class, async_class) pairs based on naming convention."""
    by_name = {cls.name: cls for cls in classes}
    pairs = []

    for cls in classes:
        name = cls.name
        # Skip classes that are already the async variant
        if name.startswith("Async"):
            continue
        # Skip mixins and private classes
        if name.startswith("_"):
            continue

        # Determine expected async name
        async_name = generate_async._async_class_name(name)
        if async_name in by_name:
            pairs.append((cls, by_name[async_name]))

    return pairs


# ---------------------------------------------------------------------------
# 1. Idempotency -- running the script twice produces no diff
# ---------------------------------------------------------------------------


class TestIdempotency:
    """Running generate_async.py twice should produce no diff."""

    def test_all_files_idempotent(self):
        """Run the codegen script, then run it again -- no file should change."""
        # First run
        result1 = subprocess.run(
            [sys.executable, str(SCRIPTS_DIR / "generate_async.py")],
            capture_output=True,
            text=True,
        )
        assert result1.returncode == 0, f"First run failed: {result1.stderr}"

        # Capture file contents after first run
        snapshots = {}
        for f in _resource_files():
            snapshots[f.name] = f.read_text()

        # Second run
        result2 = subprocess.run(
            [sys.executable, str(SCRIPTS_DIR / "generate_async.py")],
            capture_output=True,
            text=True,
        )
        assert result2.returncode == 0, f"Second run failed: {result2.stderr}"

        # Verify no changes
        for f in _resource_files():
            current = f.read_text()
            assert current == snapshots[f.name], (
                f"{f.name} changed between first and second run of generate_async.py"
            )

    @pytest.mark.parametrize(
        "resource_file",
        _files_with_marker(),
        ids=lambda f: f.name,
    )
    def test_individual_file_idempotent(self, resource_file: Path):
        """Each individual file is idempotent when processed alone."""
        original = resource_file.read_text()

        result = subprocess.run(
            [
                sys.executable,
                str(SCRIPTS_DIR / "generate_async.py"),
                resource_file.stem,
            ],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, f"Run failed for {resource_file.name}: {result.stderr}"

        after = resource_file.read_text()
        assert after == original, (
            f"{resource_file.name} was modified by a regeneration run -- "
            f"this means the current file content is out of sync with the codegen script"
        )


# ---------------------------------------------------------------------------
# 2. Valid Python -- generated async code parses without syntax errors
# ---------------------------------------------------------------------------


class TestValidPython:
    """Generated async code must be valid Python."""

    @pytest.mark.parametrize(
        "resource_file",
        _files_with_marker(),
        ids=lambda f: f.name,
    )
    def test_file_parses(self, resource_file: Path):
        """Each resource file should parse as valid Python after codegen."""
        source = resource_file.read_text()
        try:
            ast.parse(source)
        except SyntaxError as exc:
            pytest.fail(
                f"{resource_file.name} has a syntax error after codegen: {exc}"
            )

    @pytest.mark.parametrize(
        "resource_file",
        _files_with_marker(),
        ids=lambda f: f.name,
    )
    def test_async_section_parses_independently(self, resource_file: Path):
        """The async section alone should be valid Python (modulo imports)."""
        source = resource_file.read_text()
        marker_idx = source.index(MARKER)
        async_section = source[marker_idx + len(MARKER) :]

        # Extract the import block from the header (everything before the first
        # class definition). This handles multi-line imports correctly.
        tree = ast.parse(source)
        first_class_line = None
        for node in ast.iter_child_nodes(tree):
            if isinstance(node, ast.ClassDef):
                first_class_line = node.lineno
                break

        header_lines = source.split("\n")
        if first_class_line is not None:
            header_lines = header_lines[: first_class_line - 1]

        # Keep only import statements and __future__ annotations
        import_block_lines = []
        in_import = False
        for line in header_lines:
            stripped = line.strip()
            if stripped.startswith(("from ", "import ")):
                import_block_lines.append(line)
                in_import = "(" in line and ")" not in line
            elif in_import:
                import_block_lines.append(line)
                if ")" in line:
                    in_import = False
            elif stripped.startswith("if TYPE_CHECKING"):
                # Include TYPE_CHECKING blocks for forward references
                import_block_lines.append(line)
                in_import = True
            elif stripped == "" and import_block_lines:
                import_block_lines.append(line)

        preamble = "\n".join(import_block_lines) + "\n\n"

        try:
            ast.parse(preamble + async_section)
        except SyntaxError as exc:
            pytest.fail(
                f"Async section of {resource_file.name} has syntax error: {exc}"
            )


# ---------------------------------------------------------------------------
# 3. Method signature parity -- async classes have the same methods as sync
# ---------------------------------------------------------------------------


class TestMethodParity:
    """Async classes should have the same methods as their sync counterparts."""

    @pytest.mark.parametrize(
        "resource_file",
        _files_with_marker(),
        ids=lambda f: f.name,
    )
    def test_method_names_match(self, resource_file: Path):
        """Every method in the sync class must exist in the async class."""
        source = resource_file.read_text()
        classes = _get_all_classes(source)
        pairs = _find_sync_async_pairs(classes)

        assert pairs, f"No sync/async pairs found in {resource_file.name}"

        for sync_cls, async_cls in pairs:
            sync_methods = _method_names(sync_cls)
            async_methods = _method_names(async_cls)

            # __init__ may differ for standard objects, so we compare the rest
            sync_public = {m for m in sync_methods if not m.startswith("__")}
            async_public = {m for m in async_methods if not m.startswith("__")}

            missing = sync_public - async_public
            extra = async_public - sync_public

            assert not missing, (
                f"{resource_file.name}: {async_cls.name} is missing methods "
                f"from {sync_cls.name}: {missing}"
            )
            assert not extra, (
                f"{resource_file.name}: {async_cls.name} has extra methods "
                f"not in {sync_cls.name}: {extra}"
            )

    @pytest.mark.parametrize(
        "resource_file",
        _files_with_marker(),
        ids=lambda f: f.name,
    )
    def test_method_parameter_names_match(self, resource_file: Path):
        """Method parameters should match between sync and async versions."""
        source = resource_file.read_text()
        classes = _get_all_classes(source)
        pairs = _find_sync_async_pairs(classes)

        for sync_cls, async_cls in pairs:
            sync_methods = {m.name: m for m in _get_methods(sync_cls)}
            async_methods = {m.name: m for m in _get_methods(async_cls)}

            for method_name, sync_method in sync_methods.items():
                if method_name.startswith("__"):
                    continue
                async_method = async_methods.get(method_name)
                if async_method is None:
                    continue  # Already caught by test_method_names_match

                sync_params = [a.arg for a in sync_method.args.args]
                async_params = [a.arg for a in async_method.args.args]

                assert sync_params == async_params, (
                    f"{resource_file.name}: {async_cls.name}.{method_name} "
                    f"has different parameters than {sync_cls.name}.{method_name}. "
                    f"sync={sync_params}, async={async_params}"
                )

    @pytest.mark.parametrize(
        "resource_file",
        _files_with_marker(),
        ids=lambda f: f.name,
    )
    def test_awaitable_methods_are_async(self, resource_file: Path):
        """Methods that call self._http.request should be async def."""
        source = resource_file.read_text()
        classes = _get_all_classes(source)

        for cls in classes:
            if not cls.name.startswith("Async"):
                continue
            # Skip simple standard object wrappers (e.g., AsyncPeopleResource)
            # that only have class attributes, no methods
            methods = _get_methods(cls)
            if not methods:
                continue

            for method in methods:
                # Check if this method's own body contains await expressions,
                # excluding any nested function definitions (which have their
                # own async scope -- e.g., inner fetch_page in paginator methods)
                has_direct_await = _has_direct_await(method)

                if has_direct_await:
                    assert isinstance(method, ast.AsyncFunctionDef), (
                        f"{cls.name}.{method.name} contains await but is not async def"
                    )


# ---------------------------------------------------------------------------
# 4. Iterator replacement -- CursorIterator -> AsyncCursorIterator, etc.
# ---------------------------------------------------------------------------


class TestIteratorReplacement:
    """Async classes should use async iterator types."""

    @pytest.mark.parametrize(
        "resource_file",
        _files_with_marker(),
        ids=lambda f: f.name,
    )
    def test_no_sync_iterators_in_async_section(self, resource_file: Path):
        """The async section should not reference sync iterator types
        (except in import lines or TYPE_CHECKING blocks)."""
        source = resource_file.read_text()
        if MARKER not in source:
            pytest.skip("No marker in file")

        marker_idx = source.index(MARKER)
        async_section = source[marker_idx:]

        sync_iterators = ["OffsetIterator", "CursorIterator"]

        for line_no, line in enumerate(async_section.split("\n"), start=1):
            stripped = line.strip()
            # Skip import lines and comments
            if stripped.startswith(("from ", "import ", "#")):
                continue
            for sync_iter in sync_iterators:
                if sync_iter in line and f"Async{sync_iter}" not in line:
                    pytest.fail(
                        f"{resource_file.name} async section line {line_no}: "
                        f"found sync iterator '{sync_iter}' without 'Async' prefix: "
                        f"{stripped!r}"
                    )

    def test_views_uses_async_cursor_iterator(self):
        """views.py should use AsyncCursorIterator in its async class."""
        views_path = RESOURCES_DIR / "views.py"
        if not views_path.exists():
            pytest.skip("views.py not found")

        source = views_path.read_text()
        marker_idx = source.index(MARKER)
        async_section = source[marker_idx:]

        assert "AsyncCursorIterator" in async_section, (
            "views.py async section should reference AsyncCursorIterator"
        )

    def test_records_uses_async_offset_iterator(self):
        """records.py should use AsyncOffsetIterator in its async class."""
        records_path = RESOURCES_DIR / "records.py"
        if not records_path.exists():
            pytest.skip("records.py not found")

        source = records_path.read_text()
        marker_idx = source.index(MARKER)
        async_section = source[marker_idx:]

        assert "AsyncOffsetIterator" in async_section, (
            "records.py async section should reference AsyncOffsetIterator"
        )

    def test_queryable_uses_async_offset_iterator(self):
        """_queryable.py should use AsyncOffsetIterator in its async class."""
        queryable_path = RESOURCES_DIR / "_queryable.py"
        if not queryable_path.exists():
            pytest.skip("_queryable.py not found")

        source = queryable_path.read_text()
        marker_idx = source.index(MARKER)
        async_section = source[marker_idx:]

        assert "AsyncOffsetIterator" in async_section, (
            "_queryable.py async section should reference AsyncOffsetIterator"
        )


# ---------------------------------------------------------------------------
# 5. Class name transformation
# ---------------------------------------------------------------------------


class TestClassNameTransformation:
    """Sync class names should be properly transformed to async names."""

    @pytest.mark.parametrize(
        "resource_file",
        _files_with_marker(),
        ids=lambda f: f.name,
    )
    def test_async_class_exists(self, resource_file: Path):
        """Every sync class should have a matching async class after the marker."""
        source = resource_file.read_text()
        classes = _get_all_classes(source)
        pairs = _find_sync_async_pairs(classes)

        assert pairs, f"No sync/async pairs found in {resource_file.name}"

        for sync_cls, async_cls in pairs:
            expected_name = generate_async._async_class_name(sync_cls.name)
            assert async_cls.name == expected_name, (
                f"{resource_file.name}: expected async class named "
                f"'{expected_name}', got '{async_cls.name}'"
            )

    @pytest.mark.parametrize(
        "resource_file",
        _files_with_marker(),
        ids=lambda f: f.name,
    )
    def test_async_class_has_async_base(self, resource_file: Path):
        """Async classes should inherit from async base classes."""
        source = resource_file.read_text()
        classes = _get_all_classes(source)

        for cls in classes:
            if not cls.name.startswith("Async"):
                continue

            base_names = generate_async._get_base_names_raw(cls)

            # Each base should be an async variant or a mixin
            for base_name in base_names:
                is_async_base = base_name.startswith("Async")
                is_mixin = base_name.endswith("Mixin") or base_name.startswith("_")
                is_generic = base_name == "Generic"

                assert is_async_base or is_mixin or is_generic, (
                    f"{resource_file.name}: {cls.name} has non-async base "
                    f"class '{base_name}'"
                )

    def test_sync_to_async_base_mapping(self):
        """Verify the key sync -> async base class mappings."""
        assert generate_async.SYNC_TO_ASYNC_BASE["SyncResource"] == "AsyncResource"
        assert (
            generate_async.SYNC_TO_ASYNC_BASE["SyncQueryableResource"]
            == "AsyncQueryableResource"
        )
        assert (
            generate_async.SYNC_TO_ASYNC_BASE["StandardObjectResource"]
            == "AsyncStandardObjectResource"
        )

    @pytest.mark.parametrize(
        "resource_file",
        _files_with_marker(),
        ids=lambda f: f.name,
    )
    def test_async_docstring_says_asynchronous(self, resource_file: Path):
        """Async classes should have 'Asynchronous' (not 'Synchronous') in their docstring."""
        source = resource_file.read_text()
        classes = _get_all_classes(source)

        for cls in classes:
            if not cls.name.startswith("Async"):
                continue

            docstring = ast.get_docstring(cls)
            if docstring is None:
                continue

            # Some files like simple wrappers may not have "Synchronous" in original
            # but the ones that do should have been transformed
            assert "Synchronous" not in docstring or "Asynchronous" in docstring, (
                f"{resource_file.name}: {cls.name} docstring still says "
                f"'Synchronous': {docstring!r}"
            )


# ---------------------------------------------------------------------------
# 6. Marker presence in all resource files with sync/async pairs
# ---------------------------------------------------------------------------


class TestMarkerPresence:
    """The marker should exist in all resource files that have sync/async classes."""

    @pytest.mark.parametrize(
        "resource_file",
        _resource_files(),
        ids=lambda f: f.name,
    )
    def test_marker_present_if_has_sync_class(self, resource_file: Path):
        """Files with a sync resource class should contain the marker."""
        source = resource_file.read_text()
        classes = _get_all_classes(source)

        has_sync = any(generate_async._is_sync_class(cls) for cls in classes)
        # Also check for StandardObjectResource wrappers
        has_standard_object = any(
            "StandardObjectResource" in [
                b.id if isinstance(b, ast.Name) else
                (b.value.id if isinstance(b, ast.Subscript) and isinstance(b.value, ast.Name) else "")
                for b in cls.bases
            ]
            and not cls.name.startswith("Async")
            for cls in classes
        )

        if has_sync or has_standard_object:
            assert MARKER in source, (
                f"{resource_file.name} has sync resource classes but is missing "
                f"the async code marker: {MARKER!r}"
            )

    def test_marker_format_is_consistent(self):
        """All markers should use the exact same string."""
        for f in _files_with_marker():
            source = f.read_text()
            count = source.count(MARKER)
            assert count == 1, (
                f"{f.name} has {count} occurrences of the marker (expected exactly 1)"
            )

    def test_marker_appears_after_sync_class(self):
        """The marker should appear after the sync class definition, not before it."""
        for f in _files_with_marker():
            source = f.read_text()
            lines = source.split("\n")

            marker_line = None
            for i, line in enumerate(lines):
                if MARKER in line:
                    marker_line = i
                    break

            assert marker_line is not None

            classes = _get_all_classes(source)
            sync_classes = [
                cls for cls in classes
                if generate_async._is_sync_class(cls) or (
                    "StandardObjectResource" in generate_async._get_base_names_raw(cls)
                    and not cls.name.startswith("Async")
                )
            ]

            for sync_cls in sync_classes:
                assert marker_line > sync_cls.lineno, (
                    f"{f.name}: marker at line {marker_line + 1} appears before "
                    f"sync class {sync_cls.name} at line {sync_cls.lineno}"
                )
