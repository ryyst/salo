import os
import time
import threading
from pathlib import Path
from typing import Set
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from utils.logging import Log
from config import execute_runner, list_runners


class RunnerFileWatcher(FileSystemEventHandler):
    """File system event handler that triggers appropriate runners on file changes"""

    def __init__(self, debounce_delay: float = 2.0):
        super().__init__()
        self.debounce_delay = debounce_delay
        self.pending_runners: Set[str] = set()
        self.last_change_time = time.time()
        self.debounce_timer = None

        # Get available runners dynamically
        self.available_runners = set(list_runners().keys())

        # Shared directories that affect all runners
        self.shared_dirs = {"utils", "templates", "api"}

    def on_modified(self, event):
        if event.is_directory:
            return

        # Get the module directory from the path
        file_path = Path(event.src_path)

        # Skip cache and output directories
        if "_cache" in file_path.parts or "_out" in file_path.parts:
            return

        # Skip hidden files and temporary files
        if any(part.startswith(".") for part in file_path.parts):
            return
        if file_path.name.endswith((".tmp", ".swp", "~")):
            return

        # Check if this is a change in a shared directory
        shared_change = False
        for part in file_path.parts:
            if part in self.shared_dirs:
                shared_change = True
                break

        if shared_change:
            Log.info(f"Shared file changed: {event.src_path}")
            self.schedule_all_runners()
            return

        # Determine which specific runner to trigger by checking if any directory
        # in the path matches an available runner name
        runner_name = None
        for part in file_path.parts:
            if part in self.available_runners:
                runner_name = part
                break

        if runner_name:
            Log.info(f"File changed in {runner_name}/: {event.src_path}")
            self.schedule_runner(runner_name)
        else:
            # If no specific runner found, check if it's a root level change that should trigger all
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

        for runner_name in sorted(runners_to_execute):
            Log.info(f"Auto-executing runner: {runner_name}")

            # Use default config file
            config_file = f"_confs/{runner_name}.json"

            if os.path.exists(config_file):
                success = execute_runner(
                    runner_name,
                    config_file,
                    "_out",
                    "_cache",
                    False,  # don't ignore cache
                )
                if success:
                    Log.info(f"Runner {runner_name} completed successfully")
                else:
                    Log.error(f"Runner {runner_name} failed")
            else:
                Log.warning(f"Config file not found for runner {runner_name}: {config_file}")


def start_file_watcher(watch_directory: str = ".") -> Observer:
    """Start watching files and return the observer"""
    event_handler = RunnerFileWatcher()
    observer = Observer()
    observer.schedule(event_handler, watch_directory, recursive=True)
    observer.start()

    Log.info(f"Started file watcher on {watch_directory}")
    return observer
