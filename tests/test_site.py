import unittest


class TestSiteContent(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open("index.html", "r", encoding="utf-8") as handle:
            cls.html = handle.read()

    def test_has_hero_identity(self):
        self.assertIn("DAVID", self.html)
        self.assertIn("SULITZER", self.html)
        self.assertIn("PRODUCT MANAGEMENT", self.html)

    def test_nav_has_experience_anchor(self):
        self.assertIn('href="#experience"', self.html)
        self.assertIn("EXPERIENCE", self.html)

    def test_has_product_journey_section(self):
        self.assertIn("PRODUCT JOURNEY", self.html)
        self.assertIn("FROM 0→1 TO 100→1000", self.html)
        self.assertIn("A decade of product management", self.html)

    def test_lists_key_pm_roles(self):
        self.assertIn("ATLY · SENIOR PRODUCT MANAGER", self.html)
        self.assertIn("LUMEN · SENIOR PRODUCT MANAGER", self.html)
        self.assertIn("OPTIMOVE · PRODUCT MANAGER", self.html)
        self.assertIn("NASA · PRODUCT MANAGER", self.html)

    def test_has_pm_strength_chips(self):
        self.assertIn("DISCOVERY", self.html)
        self.assertIn("ROADMAPS", self.html)
        self.assertIn("IOS CRAFT", self.html)

    def test_has_contact_details(self):
        self.assertIn("davidsulitzer@icloud.com", self.html)
        self.assertIn("START A CONVERSATION", self.html)


if __name__ == "__main__":
    unittest.main()
