import unittest

from backend.api.server import _telugu_fallback


class TeluguFallbackTests(unittest.TestCase):
    def test_fallback_is_telugu_script(self):
        result = _telugu_fallback({"outcome": "RISK_DETECTED", "risk": "HIGH"})
        combined = result["summary"] + " " + " ".join(result["actions"])
        self.assertGreaterEqual(sum("\u0c00" <= ch <= "\u0c7f" for ch in combined), 20)

    def test_fallback_has_required_shape(self):
        result = _telugu_fallback({"outcome": "UNCONFIRMED", "risk": "LOW"})
        self.assertIsInstance(result["summary"], str)
        self.assertEqual(len(result["actions"]), 4)


if __name__ == "__main__":
    unittest.main()
