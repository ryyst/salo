#!/usr/bin/env python3

import sys

from utils.devserver import host_dev_server
from utils.logging import Log
from config import RunnerConfig, parse_runner_config


def process_runner(runner: RunnerConfig):
    Log.info("Processing runner %s...", runner.name)

    # 1. Fetch raw data.
    Log.info("Running fetcher for %s...", runner.name)
    raw = runner.fetcher(runner.params)

    # 2. Process raw data into renderable form.
    Log.info("Running transformer for %s...", runner.name)
    data = runner.transformer(raw, runner.params)

    # 3. Render to file / wherever.
    Log.info("Running renderer for %s...", runner.name)
    runner.renderer(data, runner.params)


def handle_runners(runner_configs: list[str]):
    for config_file in runner_configs:
        try:
            runner = parse_runner_config(config_file)
            if not runner:
                continue

            process_runner(runner)

        except FileNotFoundError as e:
            Log.error("No runner file found at path: %s", config_file)

        except Exception as e:
            Log.exception("Unexpected error while processing runner: %s", e, exc_info=e)

        except KeyboardInterrupt as e:
            Log.warning(f"Runner {config_file} interrupted, final state unknown.")


def exit(reason: str):
    print(reason)
    sys.exit(1)


def main(args: list[str]):
    if len(args) < 2:
        exit(
            "Usage: python main.py <subcommand> [options]\n"
            "Subcommands:\n"
            "  runners <runner1.json> <runner2.json> ...\n"
            "  dev <output_dir> [port]"
        )

    subcommand, *subargs = args

    if subcommand == "runners":
        return handle_runners(subargs)

    if subcommand == "dev":
        directory = subargs[0]
        port = int(subargs[1]) if len(subargs) > 1 else 8000

        return host_dev_server(directory, port)

    exit(f"Unknown subcommand: {subcommand}")


if __name__ == "__main__":
    main(sys.argv[1:])
