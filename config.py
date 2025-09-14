import json
from typing import Callable, Type, Optional, Dict, Any, TypeVar
from dataclasses import dataclass
from functools import wraps

from pydantic import ValidationError

from utils.logging import Log
from utils.schema import JSONModel
from utils.schema_formatter import format_schema
from utils.paths import config_exists, get_config_path
from utils.constants import DEFAULT_OUTPUT_DIR, DEFAULT_CACHE_DIR, DEFAULT_CONFIG_DIR


@dataclass
class CliConfig:
    """Global CLI configuration for the current execution."""

    output_dir: str = DEFAULT_OUTPUT_DIR
    cache_dir: str = DEFAULT_CACHE_DIR
    ignore_cache: bool = False
    config_dir: str = DEFAULT_CONFIG_DIR


# Global registry for all runners
RUNNERS_REGISTRY: Dict[str, Dict[str, Any]] = {}

# Global CLI context - holds the current CliConfig instance
CLI_CONTEXT: CliConfig = CliConfig()

# Type variable for JSONModel subclasses
T = TypeVar("T", bound=JSONModel)


class RunnerInfo:
    """Information about a registered runner"""

    def __init__(self, name: str, info: Dict[str, Any]):
        self.name = name
        self.function = info["function"]
        self.config_class = info["config_class"]
        self.description = info["description"]


def set_cli_context(
    output_dir: str,
    cache_dir: str,
    ignore_cache: bool = False,
    config_dir: str = DEFAULT_CONFIG_DIR,
):
    """Set global CLI context parameters."""
    global CLI_CONTEXT
    CLI_CONTEXT = CliConfig(
        output_dir=output_dir,
        cache_dir=cache_dir,
        ignore_cache=ignore_cache,
        config_dir=config_dir,
    )


def get_output_dir() -> str:
    """Get the current output directory."""
    return CLI_CONTEXT.output_dir


def get_cache_dir() -> str:
    """Get the current cache directory."""
    return CLI_CONTEXT.cache_dir


def should_ignore_cache() -> bool:
    """Get whether to ignore cache."""
    return CLI_CONTEXT.ignore_cache


def register_runner(name: str, config_class: Type[T], description: str = ""):
    """
    Decorator to register a runner function with its configuration schema.

    Args:
        name: Unique name for the runner (used in CLI)
        config_class: Pydantic model class for validating parameters
        description: Optional description for the runner
    """

    def decorator(func: Callable[[T], None]):
        if name in RUNNERS_REGISTRY:
            raise ValueError(f"Runner '{name}' is already registered")

        RUNNERS_REGISTRY[name] = {
            "function": func,
            "config_class": config_class,
            "description": description or func.__doc__ or "",
        }

        @wraps(func)
        def wrapper(params: T):
            return func(params)

        return wrapper

    return decorator


def get_runner_default_config(runner_name: str) -> Optional[str]:
    """
    Get the default config path for a runner if it exists.
    Returns None if runner doesn't exist or no config file found.
    """
    if not get_runner_info(runner_name):
        return None

    if config_exists(runner_name, CLI_CONTEXT.config_dir):
        return get_config_path(runner_name, CLI_CONTEXT.config_dir)

    return None


def execute_runner(runner_name: str, config_path: str) -> bool:
    """Execute a single runner with the given configuration. Returns True if successful."""
    runner_info = get_runner_info(runner_name)
    if not runner_info:
        Log.error("Unknown runner: %s", runner_name)
        return False

    try:
        Log.info("---------------")
        Log.info("Loading config file: %s", config_path)

        with open(config_path, "r") as f:
            config_data = json.load(f)

        Log.info("Validating parameters for runner: %s", runner_name)
        params = runner_info.config_class(**config_data)

        Log.info("Executing runner: %s", runner_name)
        runner_info.function(params)

        Log.info("Runner completed successfully: %s", runner_name)
        return True

    except FileNotFoundError:
        Log.info("Config file not found: %s", config_path)
        Log.info("")
        Log.info("To create a config file, see the expected schema:")
        Log.info("  python main.py runners %s", runner_name)
        return False

    except ValidationError as err:
        Log.error("Configuration validation failed for runner '%s':", runner_name)
        for e in err.errors():
            Log.error("  %s: %s", ".".join(str(p) for p in e.get("loc", [])), e.get("msg"))
        return False

    except KeyboardInterrupt:
        Log.warning("Runner '%s' was interrupted", runner_name)
        return False

    except Exception as e:
        Log.exception("Unexpected error in runner '%s': %s", runner_name, e, exc_info=e)
        return False


def execute_all_runners() -> bool:
    """
    Execute all registered runners that have config files.
    Returns True if all successful, False if any failed.
    """
    runners = list_runners()
    if not runners:
        Log.info("No runners registered. Make sure to import all modules.")
        return False

    all_success = True

    for runner_name in runners.keys():
        if not config_exists(runner_name, CLI_CONTEXT.config_dir):
            config_path = get_config_path(runner_name, CLI_CONTEXT.config_dir)
            Log.warning(f"Skipping runner '{runner_name}': config file not found at {config_path}")
            continue

        Log.info(f"Executing runner: {runner_name}")

        config_path = get_config_path(runner_name, CLI_CONTEXT.config_dir)
        success = execute_runner(runner_name, config_path)

        if not success:
            all_success = False
            Log.error(f"Runner '{runner_name}' failed")
        else:
            Log.info(f"Runner '{runner_name}' completed successfully")

    Log.info("All runners execution completed")
    return all_success


def get_runner_info(name: str) -> Optional[RunnerInfo]:
    """Get information about a specific runner"""
    if name not in RUNNERS_REGISTRY:
        return None
    return RunnerInfo(name, RUNNERS_REGISTRY[name])


def list_runners() -> Dict[str, str]:
    """List all registered runners with their descriptions"""
    return {name: info["description"] for name, info in RUNNERS_REGISTRY.items()}


def format_runner_schema(name: str) -> Optional[str]:
    """Transform JSON Schema into a simple human-readable format"""
    runner_info = get_runner_info(name)
    if not runner_info:
        return None

    schema = runner_info.config_class.model_json_schema()
    return format_schema(name, schema)
