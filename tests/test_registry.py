import copy
import unittest

from ai_agents_hub.registry import (
    load_json,
    validate_configuration,
    validate_policy,
    validate_registry,
)


def valid_agent(**overrides):
    agent = {
        "id": "review-helper",
        "name": "Review Helper",
        "description": "Drafts review notes for human approval.",
        "enabled": False,
        "permissions": ["draft_text"],
        "requires_human_approval": True,
    }
    agent.update(overrides)
    return agent


class RegistryValidationTests(unittest.TestCase):
    def setUp(self):
        self.registry = load_json("agents/registry.json")
        self.policy = load_json("policies/default.json")

    def test_empty_registry_is_valid(self):
        self.assertEqual(validate_registry({"schema_version": "1.0", "agents": []}), [])

    def test_duplicate_agent_ids_are_rejected(self):
        registry = {"schema_version": "1.0", "agents": [valid_agent(), valid_agent()]}
        self.assertTrue(any("duplicate agent id" in e for e in validate_registry(registry)))

    def test_unknown_permission_is_rejected(self):
        registry = {"schema_version": "1.0", "agents": [valid_agent(permissions=["execute_shell"])]}
        self.assertTrue(any("unsupported permission" in e for e in validate_registry(registry)))

    def test_unknown_agent_field_is_rejected(self):
        registry = {"schema_version": "1.0", "agents": [valid_agent(prompt="run this") ]}
        self.assertTrue(any("unsupported field: prompt" in e for e in validate_registry(registry)))

    def test_agent_id_must_match_slug_pattern(self):
        registry = {"schema_version": "1.0", "agents": [valid_agent(id="Bad ID") ]}
        self.assertTrue(any("lowercase slug" in e for e in validate_registry(registry)))

    def test_agent_field_lengths_are_checked(self):
        registry = {
            "schema_version": "1.0",
            "agents": [valid_agent(name="X", description="short")],
        }
        errors = validate_registry(registry)
        self.assertTrue(any("name must be a string" in e for e in errors))
        self.assertTrue(any("description must be a string" in e for e in errors))

    def test_permissions_must_be_unique(self):
        registry = {
            "schema_version": "1.0",
            "agents": [valid_agent(permissions=["draft_text", "draft_text"])],
        }
        self.assertTrue(any("entries must be unique" in e for e in validate_registry(registry)))

    def test_permissions_with_non_string_items_fail_safely(self):
        registry = {"schema_version": "1.0", "agents": [valid_agent(permissions=[None])]}
        errors = validate_registry(registry)
        self.assertTrue(any("entries must all be strings" in e for e in errors))

    def test_human_approval_is_required(self):
        registry = {
            "schema_version": "1.0",
            "agents": [valid_agent(requires_human_approval=False)],
        }
        self.assertTrue(any("requires_human_approval must be true" in e for e in validate_registry(registry)))

    def test_default_policy_is_fail_closed(self):
        self.assertEqual(validate_policy(self.policy), [])
        self.assertEqual(self.policy["execution_mode"], "disabled")
        self.assertTrue(self.policy["human_approval_required"])

    def test_policy_cannot_allow_unsupported_capability(self):
        policy = copy.deepcopy(self.policy)
        policy["allowed_capabilities"].append("execute_shell")
        self.assertTrue(any("unsupported capabilities" in e for e in validate_policy(policy)))

    def test_policy_rejects_non_string_entries_without_crashing(self):
        policy = copy.deepcopy(self.policy)
        policy["allowed_capabilities"].append({"bad": "entry"})
        errors = validate_policy(policy)
        self.assertTrue(any("entries must all be strings" in e for e in errors))

    def test_policy_requires_protected_actions_to_remain_denied(self):
        policy = copy.deepcopy(self.policy)
        policy["denied_actions"].remove("transfer_funds")
        self.assertTrue(any("missing required denials" in e for e in validate_policy(policy)))

    def test_policy_rejects_unknown_field(self):
        policy = copy.deepcopy(self.policy)
        policy["allow_shell"] = True
        self.assertTrue(any("unsupported field: allow_shell" in e for e in validate_policy(policy)))

    def test_enabled_agent_is_rejected_while_execution_is_disabled(self):
        registry = {"schema_version": "1.0", "agents": [valid_agent(enabled=True)]}
        errors = validate_configuration(registry, self.policy)
        self.assertTrue(any("cannot be true while policy.execution_mode is disabled" in e for e in errors))

    def test_agent_cannot_request_capability_outside_policy(self):
        registry = {
            "schema_version": "1.0",
            "agents": [valid_agent(permissions=["read_public_data"])],
        }
        policy = copy.deepcopy(self.policy)
        policy["allowed_capabilities"] = ["draft_text"]
        errors = validate_configuration(registry, policy)
        self.assertTrue(any("not allowed by policy" in e for e in errors))

    def test_default_project_configuration_is_consistent(self):
        self.assertEqual(validate_configuration(self.registry, self.policy), [])


if __name__ == "__main__":
    unittest.main()
