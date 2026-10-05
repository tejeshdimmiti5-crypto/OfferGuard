import unittest

from backend.api.server import _hindi_fallback


class HindiFallbackTests(unittest.TestCase):
    def test_fallback_is_devanagari(self):
        result = _hindi_fallback({"outcome": "RISK_DETECTED", "risk": "HIGH"})
        combined = result["summary"] + " " + " ".join(result["actions"])
        self.assertGreaterEqual(sum("\u0900" <= ch <= "\u097f" for ch in combined), 20)

    def test_fallback_has_required_shape(self):
        result = _hindi_fallback({"outcome": "UNCONFIRMED", "risk": "LOW"})
        self.assertIsInstance(result["summary"], str)
        self.assertEqual(len(result["actions"]), 4)


if __name__ == "__main__":
    unittest.main()
