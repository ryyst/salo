import sys

from utils.logging import Log
from config import RunnerConfig, parse_runner_config


def process_runner(runner: RunnerConfig):
    Log.info("Processing runner %s...", runner.name)

    # 1. Fetch raw data.
    raw = runner.fetcher(runner.params)

    # 2. Process raw data into renderable form.
    data = runner.transformer(raw, runner.params)

    # 3. Render to file / wherever.
    runner.renderer(data, runner.params)


def main(runner_configs: list[str]):
    for config_file in runner_configs:
        try:
            runner = parse_runner_config(config_file)
            if not runner:
                continue

            process_runner(runner)

        except Exception as e:
            Log.exception("Unexpected error while processing runner: %s", e, exc_info=e)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python main.py <runner1.json> <runner2.json> ...")
        sys.exit(1)

    main(sys.argv[1:])
