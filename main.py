#!/usr/bin/env python3
import sys
import argparse

from utils.devserver import host_dev_server
from utils.constants import DEFAULT_OUTPUT_DIR, DEFAULT_CACHE_DIR, DEFAULT_DEV_PORT
from config import (
    list_runners,
    format_runner_schema,
    set_cli_context,
    get_runner_default_config,
    execute_runner,
    execute_all_runners,
)

# Import all runner modules to register individual runner functions
import auki.runners  # noqa
import swimmi.runners  # noqa
import tori.runners  # noqa
import leffa.runners  # noqa
import koje.runners  # noqa
import saa.runners  # noqa
import uutta.runners  # noqa


def create_parser():
    """Create the argument parser"""
    parser = argparse.ArgumentParser(description="Salo.fyi ETL pipeline runner")

    subparsers = parser.add_subparsers(dest="subcommand", help="Available subcommands")

    # Runners subcommand
    runners_parser = subparsers.add_parser("runners", help="Manage and execute runners")
    runners_parser.add_argument(
        "runner_name", nargs="?", help="Name of runner to execute or show schema"
    )
    runners_parser.add_argument(
        "--params",
        help="Configuration file to use (default: _confs/{runner_name}.json if exists, otherwise show schema)",
    )
    runners_parser.add_argument(
        "--output-dir",
        default=DEFAULT_OUTPUT_DIR,
        help=f"Base output directory for generated files (default: {DEFAULT_OUTPUT_DIR})",
    )
    runners_parser.add_argument(
        "--cache-dir",
        default=DEFAULT_CACHE_DIR,
        help=f"Cache directory for storing temporary data (default: {DEFAULT_CACHE_DIR})",
    )
    runners_parser.add_argument(
        "--ignore-cache",
        action="store_true",
        help="Force redownload of all data, ignoring existing cache",
    )

    # Dev subcommand
    dev_parser = subparsers.add_parser("dev", help="Start development server")
    dev_parser.add_argument(
        "directory",
        nargs="?",
        default=DEFAULT_OUTPUT_DIR,
        help=f"Directory to serve (if not provided, serves all apps from {DEFAULT_OUTPUT_DIR})",
    )
    dev_parser.add_argument(
        "--port",
        type=int,
        default=DEFAULT_DEV_PORT,
        help=f"Port to serve on (default: {DEFAULT_DEV_PORT})",
    )

    return parser


def handle_runners(args):
    """Handle the runners subcommand"""
    if not args.runner_name:
        # List all available runners
        runners = list_runners()
        if not runners:
            print("No runners registered. Make sure to import all modules.")
            return

        print("Available runners:")
        for name, description in runners.items():
            print(f"  {name:<20} {description}")
        print(f"  {'all':<20} Execute all registered runners")
        return

    # Handle special "all" runner
    if args.runner_name == "all":
        success = execute_all_runners()
        sys.exit(0 if success else 1)

    config_path = args.params or get_runner_default_config(args.runner_name)

    if config_path is None:
        # Check if runner exists
        runners = list_runners()
        if args.runner_name not in runners:
            print(f"Unknown runner: {args.runner_name}")
            print("Available runners:")
            for name in runners.keys():
                print(f"  {name}")
            sys.exit(1)

        # Show schema instead
        schema_display = format_runner_schema(args.runner_name)
        print(schema_display)
        sys.exit(1)

    set_cli_context(args.output_dir, args.cache_dir, args.ignore_cache, config_path)
    success = execute_runner(args.runner_name, config_path)
    sys.exit(0 if success else 1)


def main():
    parser = create_parser()
    args = parser.parse_args()

    if not args.subcommand:
        parser.print_help()
        sys.exit(1)

    if args.subcommand == "runners":
        return handle_runners(args)

    if args.subcommand == "dev":
        return host_dev_server(args.directory, args.port)

    parser.print_help()
    sys.exit(1)


if __name__ == "__main__":
    main()
