"""Key storage tests use fake strings and never call a provider."""
import importlib.util
import stat
import tempfile
import unittest
from pathlib import Path

SPEC = importlib.util.spec_from_file_location(
    "key_setup", Path(__file__).resolve().parents[1] / "scripts/configure_api_keys.py")
setup = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(setup)


class KeySetupTests(unittest.TestCase):
    def test_new_file_is_private_and_contains_only_recognized_variables(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / ".env.local"
            setup.save_keys(path, {"OPENAI_API_KEY": "fake-key-for-test"})
            self.assertEqual(path.read_text(), "OPENAI_API_KEY=fake-key-for-test\n")
            self.assertEqual(stat.S_IMODE(path.stat().st_mode), 0o600)

    def test_existing_file_is_never_replaced(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / ".env.local"
            path.write_text("existing")
            with self.assertRaises(FileExistsError):
                setup.save_keys(path, {"OPENAI_API_KEY": "fake-key-for-test"})
            self.assertEqual(path.read_text(), "existing")

    def test_invalid_values_cannot_inject_another_variable(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / ".env.local"
            with self.assertRaises(ValueError):
                setup.save_keys(path, {"OPENAI_API_KEY": "fake\nOTHER=value"})
            self.assertFalse(path.exists())

    def test_exact_anthropic_double_paste_is_saved_as_one_copy(self):
        fake_key = "sk-ant-fake-only-ABC123"
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / ".env.local"
            setup.save_keys(path, {"ANTHROPIC_API_KEY": fake_key + fake_key})
            self.assertEqual(path.read_text(), "ANTHROPIC_API_KEY=" + fake_key + "\n")
            self.assertEqual(stat.S_IMODE(path.stat().st_mode), 0o600)

    def test_exact_openai_double_paste_is_saved_as_one_copy(self):
        fake_key = "sk-proj-fake-only-XYZ789"
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / ".env.local"
            setup.save_keys(path, {"OPENAI_API_KEY": fake_key + fake_key})
            self.assertEqual(path.read_text(), "OPENAI_API_KEY=" + fake_key + "\n")
            self.assertEqual(stat.S_IMODE(path.stat().st_mode), 0o600)

    def test_distinct_joined_values_are_not_guessed_or_repaired(self):
        value = "sk-ant-fake-only-FIRSTsk-ant-fake-only-OTHER"
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / ".env.local"
            setup.save_keys(path, {"ANTHROPIC_API_KEY": value})
            self.assertEqual(path.read_text(), "ANTHROPIC_API_KEY=" + value + "\n")

    def test_non_provider_prefix_and_four_copies_are_not_normalized(self):
        cases = (
            ("ANTHROPIC_API_KEY", "fake-only" * 2),
            ("ANTHROPIC_API_KEY", "sk-ant-fake-only" * 4),
            ("ANTHROPIC_API_KEY", "sk-proj-fake-only" * 2),
            ("OPENAI_API_KEY", "sk-proj-fake-only" * 4),
        )
        for name, value in cases:
            with self.subTest(name=name, value_type="synthetic"):
                with tempfile.TemporaryDirectory() as directory:
                    path = Path(directory) / ".env.local"
                    setup.save_keys(path, {name: value})
                    self.assertEqual(path.read_text(), name + "=" + value + "\n")

    def test_normal_provider_keys_are_preserved_without_mutating_input(self):
        keys = {"OPENAI_API_KEY": "sk-proj-fake-only-ABC", "ANTHROPIC_API_KEY": "sk-ant-fake-only-XYZ"}
        original = keys.copy()
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / ".env.local"
            setup.save_keys(path, keys)
            self.assertEqual(path.read_text(), "OPENAI_API_KEY=" + keys["OPENAI_API_KEY"] +
                             "\nANTHROPIC_API_KEY=" + keys["ANTHROPIC_API_KEY"] + "\n")
        self.assertEqual(keys, original)

    def test_double_paste_does_not_allow_replacing_an_existing_file(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / ".env.local"
            path.write_text("existing")
            with self.assertRaises(FileExistsError):
                setup.save_keys(path, {"ANTHROPIC_API_KEY": "sk-ant-fake-only" * 2})
            self.assertEqual(path.read_text(), "existing")


if __name__ == "__main__":
    unittest.main()
