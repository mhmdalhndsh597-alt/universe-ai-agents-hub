"""Command-line interface for offline hub validation."""

from __future__ import annotations

import argparse
import sys

from .registry import load_json, validate_policy, validate_registry


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

    errors = validate_registry(registry) + validate_policy(policy)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1

    print("Validation passed: registry and policy are structurally sound.")
    print("Agent execution remains disabled; no network calls were made.")
    return 0
