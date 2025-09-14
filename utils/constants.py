"""Centralized constants for the Salo.fyi ETL pipeline."""

# Default directory structure
DEFAULT_OUTPUT_DIR = "_out"
DEFAULT_CACHE_DIR = "_cache"
DEFAULT_CONFIG_DIR = "_confs"

# Development server settings
DEFAULT_DEV_PORT = 8000
DEFAULT_DEV_HOST = "localhost"

# File watcher settings
DEFAULT_DEBOUNCE_DELAY = 2.0

# Shared directories that affect all runners when changed
SHARED_DIRECTORIES = {"utils", "templates", "api"}

# File extensions and patterns to ignore in file watcher
IGNORED_FILE_PATTERNS = {".tmp", ".swp", "~"}
IGNORED_DIRECTORIES = {"_cache", "_out", ".git", "__pycache__"}

# Static files served from koje directory
KOJE_STATIC_FILES = {
    "manifest.json",
    "icon-192.png",
    "icon-512.png",
    "sw.js",
    "CNAME",
}

# Content types for file serving
CONTENT_TYPES = {
    ".html": "text/html",
    ".css": "text/css",
    ".js": "application/javascript",
    ".json": "application/json",
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".gif": "image/gif",
    ".svg": "image/svg+xml",
}
