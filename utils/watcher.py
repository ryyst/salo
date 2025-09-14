import time
import threading
from pathlib import Path
from typing import Set
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from utils.logging import Log
from config import execute_runner
from utils.paths import (
    is_ignored_path,
    get_module_from_path,
    is_shared_module_path,
    get_config_path,
    config_exists,
)
from utils.constants import (
    DEFAULT_DEBOUNCE_DELAY,
    DEFAULT_OUTPUT_DIR,
    DEFAULT_CACHE_DIR,
)
from config import list_runners


class RunnerFileWatcher(FileSystemEventHandler):
    """File system event handler that triggers appropriate runners on file changes"""

    def __init__(self, debounce_delay: float = DEFAULT_DEBOUNCE_DELAY):
        super().__init__()
        self.debounce_delay = debounce_delay
        self.pending_runners: Set[str] = set()
        self.last_change_time = time.time()
        self.debounce_timer = None

        # Get available runners dynamically
        self.available_runners = set(list_runners().keys())

    def on_modified(self, event):
        if event.is_directory:
            return

        file_path = Path(event.src_path)

        # Skip ignored paths (cache, output, hidden files, etc.)
        if is_ignored_path(file_path):
            return

        # Check if this is a change in a shared directory
        if is_shared_module_path(file_path):
            Log.info(f"Shared file changed: {event.src_path}")
            self.schedule_all_runners()
            return

        # Determine which specific runner to trigger
        runner_name = get_module_from_path(file_path, self.available_runners)

        if runner_name:
            Log.info(f"File changed in {runner_name}/: {event.src_path}")
            self.schedule_runner(runner_name)
        else:
            # If no specific runner found, it's a root level change that should trigger all
            Log.info(f"Root level file changed: {event.src_path}")
            self.schedule_all_runners()

    def schedule_runner(self, runner_name: str):
        """Schedule a runner to execute after debounce delay"""
        self.pending_runners.add(runner_name)
        self.last_change_time = time.time()

        # Cancel existing timer
        if self.debounce_timer:
            self.debounce_timer.cancel()

        # Start new timer
        self.debounce_timer = threading.Timer(self.debounce_delay, self.execute_pending_runners)
        self.debounce_timer.start()

    def schedule_all_runners(self):
        """Schedule all available runners to execute after debounce delay"""
        for runner_name in self.available_runners:
            self.pending_runners.add(runner_name)

        self.last_change_time = time.time()

        # Cancel existing timer
        if self.debounce_timer:
            self.debounce_timer.cancel()

        # Start new timer
        self.debounce_timer = threading.Timer(self.debounce_delay, self.execute_pending_runners)
        self.debounce_timer.start()

    def execute_pending_runners(self):
        """Execute all pending runners"""
        if not self.pending_runners:
            return

        runners_to_execute = self.pending_runners.copy()
        self.pending_runners.clear()

        from config import CLI_CONTEXT

        for runner_name in sorted(runners_to_execute):
            config_path = get_config_path(runner_name, CLI_CONTEXT.config_dir)

            if config_exists(runner_name, CLI_CONTEXT.config_dir):
                Log.info(f"Auto-executing runner: {runner_name}")
                success = execute_runner(runner_name, config_path)

                if success:
                    Log.info(f"Runner {runner_name} completed successfully")
                else:
                    Log.error(f"Runner {runner_name} failed")
            else:
                Log.warning(f"Config file not found for runner {runner_name}: {config_path}")


def start_file_watcher(watch_directory: str = ".") -> Observer:
    """Start watching files and return the observer"""
    event_handler = RunnerFileWatcher()
    observer = Observer()
    observer.schedule(event_handler, watch_directory, recursive=True)
    observer.start()

    Log.info(f"Started file watcher on {watch_directory}")
    return observer
