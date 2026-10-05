import unittest

from backend.analysis.recommendations import recommend_companies


class ComparableEmployerTests(unittest.TestCase):
    def test_returns_official_career_sites(self):
        items = recommend_companies(
            "We are hiring a software engineer with Python, cloud and AI experience."
        )
        self.assertTrue(items)
        self.assertLessEqual(len(items), 5)
        for item in items:
            self.assertIn("careers_url", item)
            self.assertTrue(item["careers_url"].startswith("https://"))
            self.assertFalse(item["live_opening"])

    def test_does_not_recommend_the_named_company(self):
        items = recommend_companies(
            "Microsoft is offering a software engineer role."
        )
        self.assertNotIn("Microsoft", {item["company"] for item in items})

    def test_recommendations_do_not_claim_live_vacancies(self):
        items = recommend_companies("Data analyst internship")
        self.assertTrue(all(item["live_opening"] is False for item in items))


if __name__ == "__main__":
    unittest.main()
