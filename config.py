import json
from typing import Callable, Type, Optional, Dict, Any, TypeVar
from functools import wraps

from pydantic import ValidationError

from utils.logging import Log
from utils.schema import JSONModel
from utils.schema_formatter import format_schema


# Global registry for all runners
RUNNERS_REGISTRY: Dict[str, Dict[str, Any]] = {}

# Global context for CLI parameters
CLI_CONTEXT = {"output_dir": "_out", "cache_dir": "_cache", "ignore_cache": False}

# Type variable for JSONModel subclasses
T = TypeVar("T", bound=JSONModel)


def set_cli_context(output_dir: str, cache_dir: str, ignore_cache: bool = False):
    """Set global CLI context parameters"""
    CLI_CONTEXT["output_dir"] = output_dir
    CLI_CONTEXT["cache_dir"] = cache_dir
    CLI_CONTEXT["ignore_cache"] = ignore_cache


def get_output_dir() -> str:
    """Get the current output directory"""
    return CLI_CONTEXT["output_dir"]


def get_cache_dir() -> str:
    """Get the current cache directory"""
    return CLI_CONTEXT["cache_dir"]


def should_ignore_cache() -> bool:
    """Get whether to ignore cache"""
    return CLI_CONTEXT["ignore_cache"]


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


class RunnerInfo:
    """Information about a registered runner"""

    def __init__(self, name: str, info: Dict[str, Any]):
        self.name = name
        self.function = info["function"]
        self.config_class = info["config_class"]
        self.description = info["description"]


def get_runner_info(name: str) -> Optional[RunnerInfo]:
    """Get information about a specific runner"""
    if name not in RUNNERS_REGISTRY:
        return None
    return RunnerInfo(name, RUNNERS_REGISTRY[name])


def list_runners() -> Dict[str, str]:
    """List all registered runners with their descriptions"""
    return {name: info["description"] for name, info in RUNNERS_REGISTRY.items()}


def get_runner_schema(name: str) -> Optional[Dict[str, Any]]:
    """Get the JSON schema for a runner's configuration"""
    runner_info = get_runner_info(name)
    if not runner_info:
        return None

    return runner_info.config_class.model_json_schema()


def format_runner_schema(name: str) -> Optional[str]:
    """Transform JSON Schema into a simple human-readable format"""
    runner_info = get_runner_info(name)
    if not runner_info:
        return None

    schema = runner_info.config_class.model_json_schema()
    return format_schema(name, schema)


def execute_runner(
    name: str,
    config_path: str,
    output_dir: str = "_out",
    cache_dir: str = "_cache",
    ignore_cache: bool = False,
) -> bool:
    """
    Execute a runner with the given configuration file.

    Returns True if successful, False otherwise.
    """
    runner_info = get_runner_info(name)
    if not runner_info:
        Log.error("Unknown runner: %s", name)
        return False

    try:
        # Set global CLI context
        set_cli_context(output_dir, cache_dir, ignore_cache)

        Log.info("---------------")
        Log.info("Loading config file: %s", config_path)
        with open(config_path, "r") as f:
            config_data = json.load(f)

        Log.info("Validating parameters for runner: %s", name)
        params = runner_info.config_class(**config_data)

        Log.info("Executing runner: %s", name)
        runner_info.function(params)

        Log.info("Runner completed successfully: %s", name)
        return True

    except FileNotFoundError:
        Log.info("Config file not found: %s", config_path)
        Log.info("")
        Log.info("To create a config file, see the expected schema:")
        Log.info("  python main.py runners %s", name)
        Log.info("")
        Log.info("Then create your config file with the required parameters:")
        Log.info("  echo '{}' > %s", config_path)
        Log.info("  # Edit %s with your actual configuration", config_path)
        return False
    except ValidationError as err:
        Log.error("Configuration validation failed for runner '%s':", name)
        for e in err.errors():
            Log.error("  %s: %s", ".".join(str(p) for p in e.get("loc", [])), e.get("msg"))
        return False
    except KeyboardInterrupt:
        Log.warning("Runner '%s' was interrupted" % name)
        return False
    except Exception as e:
        Log.exception("Unexpected error in runner '%s': %s", name, e, exc_info=e)
        return False
