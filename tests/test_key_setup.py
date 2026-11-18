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


if __name__ == "__main__":
    unittest.main()
