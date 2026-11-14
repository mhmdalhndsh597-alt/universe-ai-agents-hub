"""Command-line interface for offline hub validation."""

from __future__ import annotations

import argparse
import sys

from .registry import load_json, validate_configuration


def main() -> int:
    parser = argparse.ArgumentParser(prog="universe-ai-agents-hub")
    subparsers = parser.add_subparsers(dest="command")
    validate = subparsers.add_parser("validate", help="validate the registry and default policy")
    validate.add_argument("--registry", default="agents/registry.json")
    validate.add_argument("--policy", default="policies/default.json")
    args = parser.parse_args()

    if args.command != "validate":
        parser.print_help()
        return 2

    try:
        registry = load_json(args.registry)
        policy = load_json(args.policy)
    except (OSError, ValueError) as exc:
        print(f"Validation failed: {exc}", file=sys.stderr)
        return 1

    errors = validate_configuration(registry, policy)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1

    print("Validation passed: registry, policy, and cross-file permissions are consistent.")
    print(f"Execution mode: {policy['execution_mode']}; no network calls were made.")
    return 0
