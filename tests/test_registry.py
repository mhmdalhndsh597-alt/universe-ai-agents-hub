import unittest

from ai_agents_hub.registry import load_json, validate_policy, validate_registry


class RegistryValidationTests(unittest.TestCase):
    def test_empty_registry_is_valid(self):
        self.assertEqual(
            validate_registry({"schema_version": "1.0", "agents": []}),
            [],
        )

    def test_duplicate_agent_ids_are_rejected(self):
        base = {
            "id": "review-helper",
            "name": "Review Helper",
            "description": "Drafts review notes for human approval.",
            "enabled": False,
            "permissions": ["draft_text"],
            "requires_human_approval": True,
        }
        registry = {"schema_version": "1.0", "agents": [base, dict(base)]}
        self.assertTrue(any("duplicate agent id" in error for error in validate_registry(registry)))

    def test_unknown_permission_is_rejected(self):
        agent = {
            "id": "test-agent",
            "name": "Test Agent",
            "description": "A test agent manifest.",
            "enabled": False,
            "permissions": ["execute_shell"],
            "requires_human_approval": True,
        }
        errors = validate_registry({"schema_version": "1.0", "agents": [agent]})
        self.assertTrue(any("unsupported permission" in error for error in errors))

    def test_human_approval_is_required(self):
        agent = {
            "id": "test-agent",
            "name": "Test Agent",
            "description": "A test agent manifest.",
            "enabled": False,
            "permissions": [],
            "requires_human_approval": False,
        }
        errors = validate_registry({"schema_version": "1.0", "agents": [agent]})
        self.assertTrue(any("requires_human_approval must be true" in error for error in errors))

    def test_default_policy_is_fail_closed(self):
        policy = load_json("policies/default.json")
        self.assertEqual(validate_policy(policy), [])
        self.assertEqual(policy["execution_mode"], "disabled")
        self.assertTrue(policy["human_approval_required"])

    def test_policy_cannot_allow_a_denied_action(self):
        policy = load_json("policies/default.json")
        policy["allowed_capabilities"].append("execute_shell")
        self.assertTrue(any("unsupported capabilities" in error for error in validate_policy(policy)))


if __name__ == "__main__":
    unittest.main()
