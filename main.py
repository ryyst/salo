#!/usr/bin/env python3

import sys

from utils.devserver import host_dev_server
from utils.logging import Log
from config import RunnerConfig, parse_runner_config


def process_runner(runner: RunnerConfig):
    """Over-engineered homebrew ETL pipeline."""

    Log.info("Processing runner %s...", runner.name)

    # 1. Fetch raw data.
    Log.info("Running fetcher...")
    raw = runner.fetcher(runner.params)

    # 2. Process raw data into renderable form.
    Log.info("Running transformer...")
    data = runner.transformer(raw, runner.params)

    # 3. Render to file / wherever.
    Log.info("Running renderer...")
    runner.renderer(data, runner.params)

    Log.info("Done!")


def handle_runners(runner_configs: list[str]):
    for config_file in runner_configs:
        try:
            runner = parse_runner_config(config_file)
            if not runner:
                continue

            process_runner(runner)

        except FileNotFoundError as e:
            Log.error("No runner file found at path: %s", config_file)

        except KeyboardInterrupt as e:
            Log.warning(f"Runner {config_file} interrupted, final state unknown.")

        except Exception as e:
            Log.exception("Unexpected error while processing runner: %s", e, exc_info=e)


def exit(reason: str):
    print(reason)
    sys.exit(1)


def main(args: list[str]):
    if len(args) < 2:
        exit(
            "Usage: python main.py <subcommand> [options]\n"
            "\n"
            "Subcommands:\n"
            "  runners <runner1.json> [runner2.json] [runner3.json] ...\n"
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
