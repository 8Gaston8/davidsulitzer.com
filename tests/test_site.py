import unittest


class TestSiteContent(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open("index.html", "r", encoding="utf-8") as handle:
            cls.html = handle.read()

    def test_has_hero_heading(self):
        self.assertIn("Turning clear strategy", self.html)

    def test_has_work_section(self):
        self.assertIn("Selected work", self.html)
        self.assertIn("Lumen Analytics", self.html)

    def test_has_services_section(self):
        self.assertIn("Services", self.html)
        self.assertIn("Product strategy", self.html)

    def test_has_about_section(self):
        self.assertIn("About David", self.html)
        self.assertIn("Working style", self.html)

    def test_has_contact_cta(self):
        self.assertIn("Ready to launch something beautiful", self.html)
        self.assertIn("Email David", self.html)


if __name__ == "__main__":
    unittest.main()
