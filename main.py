#!/usr/bin/env python3
import os
import sys
import argparse

from utils.devserver import host_dev_server
from config import list_runners, format_runner_schema, execute_runner

# Import all runner modules to register individual runner functions
import auki.runners  # noqa
import swimmi.runners  # noqa
import tori.runners  # noqa
import leffa.runners  # noqa
import koje.runners  # noqa
import saa.runners  # noqa


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
        default="_out",
        help="Base output directory for generated files (default: _out)",
    )
    runners_parser.add_argument(
        "--cache-dir",
        default="_cache",
        help="Cache directory for storing temporary data (default: _cache)",
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
        default="_out",
        help="Directory to serve (if not provided, serves all apps from _out)",
    )
    dev_parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port to serve on (default: 8000)",
    )

    return parser


def execute_single_runner(runner_name, args):
    """Execute a single runner with config resolution"""
    # Determine config file path
    if args.params:
        # Explicit config file provided
        config_file = args.params
    else:
        # No --params provided, check if default config exists
        default_config = f"_confs/{runner_name}.json"

        # Check if default config file exists
        if os.path.exists(default_config):
            # Use default config file
            config_file = default_config
        else:
            # No default config found, show schema
            schema_display = format_runner_schema(runner_name)

            if schema_display is None:
                print(f"Unknown runner: {runner_name}")
                print("Available runners:")
                for name in list_runners().keys():
                    print(f"  {name}")
                return False

            print(schema_display)
            return False

    # Execute the runner with config file
    return execute_runner(
        runner_name,
        config_file,
        args.output_dir,
        args.cache_dir,
        args.ignore_cache,
    )


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
        runners = list_runners()
        if not runners:
            print("No runners registered. Make sure to import all modules.")
            sys.exit(1)

        all_success = True
        for runner_name in runners.keys():
            print(f"\n{'='*50}")
            print(f"Executing runner: {runner_name}")
            print(f"{'='*50}")

            # Create a copy of args but override params to None for default config resolution
            runner_args = argparse.Namespace(**vars(args))
            runner_args.params = None

            success = execute_single_runner(runner_name, runner_args)
            if not success:
                all_success = False
                print(f"Runner '{runner_name}' failed or skipped")
            else:
                print(f"Runner '{runner_name}' completed successfully")

        print(f"\n{'='*50}")
        print("All runners execution summary completed")
        print(f"{'='*50}")

        sys.exit(0 if all_success else 1)

    # Execute single runner
    success = execute_single_runner(args.runner_name, args)
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
