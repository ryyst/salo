"""Path utilities for the Salo.fyi ETL pipeline."""

import os
from pathlib import Path
from typing import Optional

from .constants import (
    DEFAULT_OUTPUT_DIR,
    DEFAULT_CONFIG_DIR,
    CONTENT_TYPES,
    IGNORED_FILE_PATTERNS,
    IGNORED_DIRECTORIES,
)


def get_config_path(runner_name: str, config_dir: str = DEFAULT_CONFIG_DIR) -> str:
    """Get the configuration file path for a runner."""
    return os.path.join(config_dir, f"{runner_name}.json")


def config_exists(runner_name: str, config_dir: str = DEFAULT_CONFIG_DIR) -> bool:
    """Check if a configuration file exists for a runner."""
    return os.path.exists(get_config_path(runner_name, config_dir))


def get_app_index_path(app_name: str, output_dir: str = DEFAULT_OUTPUT_DIR) -> str:
    """Get the index.html path for an app."""
    return os.path.join(output_dir, app_name, "index.html")


def get_koje_static_path(filename: str, output_dir: str = DEFAULT_OUTPUT_DIR) -> str:
    """Get the path to a static file in the koje directory."""
    return os.path.join(output_dir, "koje", filename)


def resolve_app_file_path(
    app_name: str, relative_path: str, output_dir: str = DEFAULT_OUTPUT_DIR
) -> Optional[str]:
    """
    Resolve a file path within an app directory, handling index.html defaults
    and .html extension inference.

    Returns the resolved absolute path if the file exists, None otherwise.
    """
    app_dir = os.path.join(output_dir, app_name)

    if not os.path.isdir(app_dir):
        return None

    # Handle empty path or trailing slash - default to index.html
    if not relative_path or relative_path.endswith("/"):
        file_path = os.path.join(app_dir, relative_path + "index.html")
    else:
        file_path = os.path.join(app_dir, relative_path)

        # If file doesn't exist but .html version does, use that
        if (
            not os.path.exists(file_path)
            and not relative_path.endswith(".html")
            and os.path.exists(file_path + ".html")
        ):
            file_path = file_path + ".html"

    return file_path if os.path.exists(file_path) else None


def get_content_type_from_path(file_path: str) -> str:
    """Get the appropriate content type for a file based on its extension."""

    ext = Path(file_path).suffix.lower()
    return CONTENT_TYPES.get(ext, "application/octet-stream")


def is_ignored_path(file_path: Path) -> bool:
    """Check if a file path should be ignored by the file watcher."""

    # Check if any part of the path is in ignored directories
    for part in file_path.parts:
        if part in IGNORED_DIRECTORIES:
            return True
        if part.startswith("."):  # Hidden files/directories
            return True

    # Check if filename matches ignored patterns
    filename = file_path.name
    for pattern in IGNORED_FILE_PATTERNS:
        if filename.endswith(pattern):
            return True

    return False


def get_module_from_path(file_path: Path, available_modules: set) -> Optional[str]:
    """
    Determine which module a file path belongs to based on directory structure.

    Returns the module name if found, None otherwise.
    """
    for part in file_path.parts:
        if part in available_modules:
            return part
    return None


def is_shared_module_path(file_path: Path) -> bool:
    """Check if a file path is in a shared module directory."""
    from .constants import SHARED_DIRECTORIES

    for part in file_path.parts:
        if part in SHARED_DIRECTORIES:
            return True
    return False
