#!/usr/bin/env python3

import sys
import json

from utils.devserver import host_dev_server
from utils.logging import Log
from config import list_runners, format_runner_schema, execute_runner


def handle_runners(args: list[str]):
    """Handle the runners subcommand with various modes"""

    if len(args) == 0:
        # List all available runners
        runners = list_runners()
        if not runners:
            print("No runners registered. Make sure to import all modules.")
            return

        print("Available runners:")
        for name, description in runners.items():
            print(f"  {name:<20} {description}")
        return

    if len(args) == 1:
        # Show schema for a specific runner
        runner_name = args[0]
        schema_display = format_runner_schema(runner_name)

        if schema_display is None:
            print(f"Unknown runner: {runner_name}")
            print("Available runners:")
            for name in list_runners().keys():
                print(f"  {name}")
            return

        print(schema_display)
        return

    if len(args) == 2:
        # Execute a runner with config file
        runner_name, config_path = args
        success = execute_runner(runner_name, config_path)
        sys.exit(0 if success else 1)

    # Invalid arguments
    print("Usage for runners subcommand:")
    print("  python main.py runners                    # List all runners")
    print("  python main.py runners <name>             # Show runner config schema")
    print("  python main.py runners <name> <config>    # Execute runner")


def exit_with_usage(reason: str = ""):
    """Exit with usage information"""
    if reason:
        print(f"Error: {reason}\n")

    print("Usage: python main.py <subcommand> [options]")
    print()
    print("Subcommands:")
    print("  runners [name] [config]    Manage and execute runners")
    print("  dev <output_dir> [port]    Start development server")
    print()
    print("Examples:")
    print("  python main.py runners                        # List all available runners")
    print("  python main.py runners auki_all               # Show config schema for auki_all")
    print("  python main.py runners auki_all config.json   # Execute auki_all with config.json")
    print("  python main.py dev _out/auki/combined-salo/    # Start dev server")

    sys.exit(1)


def main(args: list[str]):
    # Import all modules to register runners
    import auki.runners  # noqa
    import swimmi.runners  # noqa
    import tori.runners  # noqa

    if len(args) < 1:
        exit_with_usage("No subcommand provided")

    subcommand, *subargs = args

    if subcommand == "runners":
        return handle_runners(subargs)

    if subcommand == "dev":
        if len(subargs) < 1:
            exit_with_usage("dev subcommand requires output directory")

        directory = subargs[0]
        port = int(subargs[1]) if len(subargs) > 1 else 8000

        return host_dev_server(directory, port)

    exit_with_usage(f"Unknown subcommand: {subcommand}")


if __name__ == "__main__":
    main(sys.argv[1:])
