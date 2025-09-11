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
    dev_parser.add_argument("directory", help="Directory to serve")
    dev_parser.add_argument(
        "port",
        nargs="?",
        type=int,
        default=8000,
        help="Port to serve on (default: 8000)",
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
        return

    # Determine config file path
    if args.params:
        # Explicit config file provided
        config_file = args.params
    else:
        # No --params provided, check if default config exists
        default_config = f"_confs/{args.runner_name}.json"

        # Check if default config file exists
        if os.path.exists(default_config):
            # Use default config file
            config_file = default_config
        else:
            # No default config found, show schema
            schema_display = format_runner_schema(args.runner_name)

            if schema_display is None:
                print(f"Unknown runner: {args.runner_name}")
                print("Available runners:")
                for name in list_runners().keys():
                    print(f"  {name}")
                return

            print(schema_display)
            return

    # Execute a runner with config file
    success = execute_runner(
        args.runner_name,
        config_file,
        args.output_dir,
        args.cache_dir,
        args.ignore_cache,
    )
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
