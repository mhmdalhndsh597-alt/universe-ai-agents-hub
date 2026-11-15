"""Offline validation for agent manifests and the hub's default policy."""

from __future__ import annotations

import json
import re
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
REGISTRY_FIELDS = {"$schema", "schema_version", "agents"}
AGENT_FIELDS = {
    "id",
    "name",
    "description",
    "enabled",
    "permissions",
    "requires_human_approval",
}
POLICY_FIELDS = {
    "schema_version",
    "execution_mode",
    "human_approval_required",
    "allowed_capabilities",
    "denied_actions",
}
AGENT_ID_PATTERN = re.compile(r"^[a-z0-9][a-z0-9-]{1,62}$")


def load_json(path: str | Path) -> Any:
    """Load one JSON document from disk."""
    with Path(path).open(encoding="utf-8") as handle:
        return json.load(handle)


def _check_fields(value: dict[str, Any], required: set[str], allowed: set[str], prefix: str) -> list[str]:
    errors = [f"{prefix}.{field} is required" for field in sorted(required - value.keys())]
    errors.extend(f"{prefix} has unsupported field: {field}" for field in sorted(value.keys() - allowed))
    return errors


def _validate_string_list(value: Any, prefix: str) -> list[str]:
    if not isinstance(value, list):
        return [f"{prefix} must be a list"]
    errors: list[str] = []
    if any(not isinstance(item, str) for item in value):
        errors.append(f"{prefix} entries must all be strings")
        return errors
    if len(value) != len(set(value)):
        errors.append(f"{prefix} entries must be unique")
    return errors


def validate_registry(registry: Any) -> list[str]:
    """Validate registry structure and agent manifests against the project contract."""
    if not isinstance(registry, dict):
        return ["registry must be a JSON object"]

    errors = _check_fields(registry, {"schema_version", "agents"}, REGISTRY_FIELDS, "registry")
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

        errors.extend(_check_fields(agent, AGENT_FIELDS, AGENT_FIELDS, prefix))

        agent_id = agent.get("id")
        if isinstance(agent_id, str):
            if not AGENT_ID_PATTERN.fullmatch(agent_id):
                errors.append(f"{prefix}.id must be a lowercase slug of 2-63 letters, digits, or hyphens")
            if agent_id in seen_ids:
                errors.append(f"duplicate agent id: {agent_id}")
            seen_ids.add(agent_id)
        elif "id" in agent:
            errors.append(f"{prefix}.id must be a string")

        name = agent.get("name")
        if not isinstance(name, str) or not 2 <= len(name) <= 100:
            errors.append(f"{prefix}.name must be a string of 2-100 characters")

        description = agent.get("description")
        if not isinstance(description, str) or not 8 <= len(description) <= 1000:
            errors.append(f"{prefix}.description must be a string of 8-1000 characters")

        if not isinstance(agent.get("enabled"), bool):
            errors.append(f"{prefix}.enabled must be a boolean")

        permissions = agent.get("permissions")
        errors.extend(_validate_string_list(permissions, f"{prefix}.permissions"))
        if isinstance(permissions, list):
            for permission in permissions:
                if isinstance(permission, str) and permission not in ALLOWED_CAPABILITIES:
                    errors.append(f"{prefix} has unsupported permission: {permission}")

        if agent.get("requires_human_approval") is not True:
            errors.append(f"{prefix}.requires_human_approval must be true")

    return errors


def validate_policy(policy: Any) -> list[str]:
    """Validate policy structure and ensure the default deny list stays intact."""
    if not isinstance(policy, dict):
        return ["policy must be a JSON object"]

    errors = _check_fields(policy, POLICY_FIELDS, POLICY_FIELDS, "policy")
    if policy.get("schema_version") != "1.0":
        errors.append("policy.schema_version must be '1.0'")
    if policy.get("execution_mode") not in VALID_EXECUTION_MODES:
        errors.append("policy.execution_mode must be disabled or review_only")
    if policy.get("human_approval_required") is not True:
        errors.append("policy.human_approval_required must be true")

    allowed = policy.get("allowed_capabilities")
    errors.extend(_validate_string_list(allowed, "policy.allowed_capabilities"))
    if isinstance(allowed, list):
        unsupported = sorted(
            {item for item in allowed if isinstance(item, str)} - ALLOWED_CAPABILITIES
        )
        if unsupported:
            errors.append(f"policy contains unsupported capabilities: {', '.join(unsupported)}")

    denied = policy.get("denied_actions")
    errors.extend(_validate_string_list(denied, "policy.denied_actions"))
    if isinstance(denied, list):
        denied_strings = {item for item in denied if isinstance(item, str)}
        missing = sorted(REQUIRED_DENIED_ACTIONS - denied_strings)
        if missing:
            errors.append(f"policy is missing required denials: {', '.join(missing)}")
        allowed_strings = {item for item in allowed if isinstance(item, str)} if isinstance(allowed, list) else set()
        overlap = sorted(denied_strings & allowed_strings)
        if overlap:
            errors.append(f"policy allows actions that it also denies: {', '.join(overlap)}")

    return errors


def validate_configuration(registry: Any, policy: Any) -> list[str]:
    """Validate both files and enforce cross-file fail-closed invariants."""
    errors = validate_registry(registry) + validate_policy(policy)
    if not isinstance(registry, dict) or not isinstance(policy, dict):
        return errors

    mode = policy.get("execution_mode")
    allowed = policy.get("allowed_capabilities")
    if not isinstance(allowed, list):
        return errors
    allowed_set = {item for item in allowed if isinstance(item, str)}

    agents = registry.get("agents")
    if not isinstance(agents, list):
        return errors
    for index, agent in enumerate(agents):
        if not isinstance(agent, dict):
            continue
        if mode == "disabled" and agent.get("enabled") is True:
            errors.append(f"agents[{index}].enabled cannot be true while policy.execution_mode is disabled")
        permissions = agent.get("permissions")
        if isinstance(permissions, list):
            outside_policy = sorted(
                {item for item in permissions if isinstance(item, str)} - allowed_set
            )
            if outside_policy:
                errors.append(
                    f"agents[{index}] requests permissions not allowed by policy: "
                    f"{', '.join(outside_policy)}"
                )

    return errors
