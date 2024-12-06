import json
from typing import Callable, Any, Type, Optional

from pydantic import BaseModel, ValidationError, model_validator

from utils.logging import Log
from utils.renderers import render_stdout
from utils.schema import JSONModel

from swimmi import SWIMMI_REGISTRY


FUNCTION_REGISTRY = {
    "swimmi": SWIMMI_REGISTRY,
    "libby": {},
    "utils": {"render": {"stdout": render_stdout}},
    # etc.
}


class AppParamsParsingError(Exception):
    pass


class FuncRegistryResolveError(Exception):
    pass


class ETLConfig(BaseModel):
    fetcher: str
    transformer: str
    renderer: str

    parser: str
    params: dict


def _resolve(config: ETLConfig, func_type: str) -> Callable:
    path = config.model_dump()[func_type]  # Existence of this is already validated

    try:
        app, category, func_name = path.split(".", 2)
        return FUNCTION_REGISTRY[app][category][func_name]
    except Exception:
        raise FuncRegistryResolveError(f"Failed to resolve given `{func_type}`: {path}")


class RunnerConfig(BaseModel):
    name: str

    fetcher: Callable
    transformer: Callable
    renderer: Callable

    parser: Type[JSONModel]
    params: JSONModel

    @model_validator(mode="before")
    def resolve_functions(cls, data: Any):
        """
        Resolve configured function names to actual callables, from our
        pre-defined function registry.
        """

        # Pre-validate the existence of all required config values before turning
        # them into Callables and JSONModels.
        config = ETLConfig(**data)

        try:
            data["fetcher"] = _resolve(config, "fetcher")
            data["transformer"] = _resolve(config, "transformer")
            data["renderer"] = _resolve(config, "renderer")
            parser = _resolve(config, "parser")

            data["parser"] = parser

            data["params"] = parser(**data["params"])

        except FuncRegistryResolveError as err:
            raise err

        except ValidationError as err:
            Log.error("Error parsing application params: %s", err.title)

            for e in err.errors():
                Log.error(
                    "%s: `%s`",
                    e.get("msg"),
                    ".".join(str(p) for p in e.get("loc", [])),
                )

            raise AppParamsParsingError

        return data


def parse_runner_config(path: str) -> Optional[RunnerConfig]:
    try:
        Log.info("Parsing runner config: %s...", path)
        with open(path, "r") as f:
            data = json.load(f)

        return RunnerConfig(**data)

    except AppParamsParsingError as err:
        pass
    except FuncRegistryResolveError as err:
        Log.error(err)
    except ValidationError as err:
        # Missing fields in main config file portion.
        for e in err.errors():
            Log.error(
                "%s: `%s`",
                e.get("msg"),
                ".".join(str(p) for p in e.get("loc", [])),
            )

    Log.error("Failed to parse config file, skipping runner: %s", path)
    return None
