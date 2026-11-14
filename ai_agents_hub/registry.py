"""Offline validation for agent manifests and the hub's default policy."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ALLOWED_CAPABILITIES = {
    "read_public_data",
    "read_repository_metadata",
    "draft_text",
    "propose_patch",
}
REQUIRED_DENIED_ACTIONS = {
    "execute_shell",
    "read_secrets",
    "write_secrets",
    "sign_transaction",
    "submit_transaction",
    "transfer_funds",
    "merge_pull_request",
    "delete_repository",
    "deploy_production",
}
VALID_EXECUTION_MODES = {"disabled", "review_only"}


def load_json(path: str | Path) -> Any:
    """Load one JSON document from disk."""
    with Path(path).open(encoding="utf-8") as handle:
        return json.load(handle)


def validate_registry(registry: Any) -> list[str]:
    """Return validation errors for a registry document."""
    errors: list[str] = []
    if not isinstance(registry, dict):
        return ["registry must be a JSON object"]
    if registry.get("schema_version") != "1.0":
        errors.append("registry.schema_version must be '1.0'")
    agents = registry.get("agents")
    if not isinstance(agents, list):
        return errors + ["registry.agents must be a list"]

    seen_ids: set[str] = set()
    for index, agent in enumerate(agents):
        prefix = f"agents[{index}]"
        if not isinstance(agent, dict):
            errors.append(f"{prefix} must be an object")
            continue
        for field in ("id", "name", "description", "enabled", "permissions", "requires_human_approval"):
            if field not in agent:
                errors.append(f"{prefix}.{field} is required")
        agent_id = agent.get("id")
        if isinstance(agent_id, str):
            if agent_id in seen_ids:
                errors.append(f"duplicate agent id: {agent_id}")
            seen_ids.add(agent_id)
            if not agent_id or any(ch not in "abcdefghijklmnopqrstuvwxyz0123456789-" for ch in agent_id):
                errors.append(f"{prefix}.id must be a lowercase slug")
        if not isinstance(agent.get("enabled"), bool):
            errors.append(f"{prefix}.enabled must be a boolean")
        if not isinstance(agent.get("permissions"), list):
            errors.append(f"{prefix}.permissions must be a list")
        else:
            for permission in agent["permissions"]:
                if permission not in ALLOWED_CAPABILITIES:
                    errors.append(f"{prefix} has unsupported permission: {permission}")
        if agent.get("requires_human_approval") is not True:
            errors.append(f"{prefix}.requires_human_approval must be true")

    return errors


def validate_policy(policy: Any) -> list[str]:
    """Return validation errors for the default fail-closed policy."""
    errors: list[str] = []
    if not isinstance(policy, dict):
        return ["policy must be a JSON object"]
    if policy.get("schema_version") != "1.0":
        errors.append("policy.schema_version must be '1.0'")
    if policy.get("execution_mode") not in VALID_EXECUTION_MODES:
        errors.append("policy.execution_mode must be disabled or review_only")
    if policy.get("human_approval_required") is not True:
        errors.append("policy.human_approval_required must be true")

    allowed = policy.get("allowed_capabilities")
    if not isinstance(allowed, list):
        errors.append("policy.allowed_capabilities must be a list")
    else:
        unsupported = sorted(set(allowed) - ALLOWED_CAPABILITIES)
        if unsupported:
            errors.append(f"policy contains unsupported capabilities: {', '.join(unsupported)}")

    denied = policy.get("denied_actions")
    if not isinstance(denied, list):
        errors.append("policy.denied_actions must be a list")
    else:
        missing = sorted(REQUIRED_DENIED_ACTIONS - set(denied))
        if missing:
            errors.append(f"policy is missing required denials: {', '.join(missing)}")
        overlap = sorted(set(denied) & set(allowed or []))
        if overlap:
            errors.append(f"policy allows actions that it also denies: {', '.join(overlap)}")

    return errors
