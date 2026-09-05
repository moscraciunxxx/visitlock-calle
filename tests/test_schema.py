import unittest

from visitlock.schema import (
    RECIPIENT_RESULT_SCHEMA,
    RESULT_SCHEMA,
    VISIT_STATUS_ENUM,
    validate_recipient_result,
)


class TestSchema(unittest.TestCase):
    def test_enum_values(self):
        self.assertEqual(
            set(VISIT_STATUS_ENUM),
            {"yes", "no", "reschedule", "no_answer", "unknown"},
        )

    def test_recipient_schema_shape(self):
        props = RECIPIENT_RESULT_SCHEMA["properties"]
        self.assertIn("visit_status", props)
        self.assertIn("preferred_slot", props)
        self.assertIn("notes", props)
        self.assertEqual(props["visit_status"]["enum"], list(VISIT_STATUS_ENUM))

    def test_result_schema_shape(self):
        props = RESULT_SCHEMA["properties"]
        self.assertIn("completed_count", props)
        self.assertIn("confirmed_count", props)
        self.assertIn("reschedule_count", props)

    def test_validate_ok(self):
        out = validate_recipient_result(
            {"visit_status": "yes", "preferred_slot": "", "notes": "ok"}
        )
        self.assertEqual(out["visit_status"], "yes")

    def test_validate_rejects_bad_status(self):
        with self.assertRaises(ValueError):
            validate_recipient_result(
                {"visit_status": "maybe", "preferred_slot": "", "notes": ""}
            )


if __name__ == "__main__":
    unittest.main()
