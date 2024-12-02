from typing import Callable

from pydantic import BaseModel

from utils.logging import Log
from utils.renderers import render_stdout

import swimmi


class RunnerConfig(BaseModel):
    fetcher: Callable
    transformer: Callable
    renderer: Callable


debug_swimmi_single = RunnerConfig(
    fetcher=swimmi.offline_fetch_single,
    transformer=swimmi.transform_single,
    renderer=swimmi.render_html_single,
)

debug_swimmi_multi = RunnerConfig(
    fetcher=swimmi.offline_fetch_multi,
    transformer=swimmi.transform_multi,
    renderer=swimmi.render_html_multi,
)

swimmi_multi = RunnerConfig(
    fetcher=swimmi.fetch_multi,
    transformer=swimmi.transform_multi,
    renderer=swimmi.render_html_multi,
    # renderer=render_stdout,
)


# TODO: Some sort of nice cli input arg setup for dynamically choosing enabled jobs.
PIPELINE_CONFIG = [
    # debug_swimmi_single,
    # debug_swimmi_multi,
    swimmi_multi,
    # TODO: RunnerConfig(Swimmi 404 page)
    # TODO: RunnerConfig(Salo tapahtumakalenteri)
    # TODO: RunnerConfig(Kirjasto)
    # TODO: RunnerConfig(etc.)
]


def process_runner(runner: RunnerConfig):
    # 1. Fetch raw data.
    raw = runner.fetcher()

    # 2. Process raw data into renderable form.
    data = runner.transformer(raw)

    # 3. Render to file / wherever.
    runner.renderer(data)


def main():
    for runner in PIPELINE_CONFIG:
        try:
            process_runner(runner)
        except Exception as e:
            Log.exception("Error processing pipeline: %s", e, exc_info=e)
            continue


main()
