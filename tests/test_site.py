import unittest


class TestSiteContent(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open("index.html", "r", encoding="utf-8") as handle:
            cls.html = handle.read()

    def test_has_bio_heading(self):
        self.assertIn("Very short bio", self.html)
        self.assertIn("A curious minimalist", self.html)

    def test_has_tech_section(self):
        self.assertIn("My tech self", self.html)
        self.assertIn("Beautiful native bias", self.html)

    def test_has_favourites_section(self):
        self.assertIn("Favourite products", self.html)
        self.assertIn("Notion", self.html)

    def test_has_questions_section(self):
        self.assertIn("Questions for you", self.html)
        self.assertIn("product discovery process", self.html)

    def test_has_contact_details(self):
        self.assertIn("davidsulitzer@icloud.com", self.html)
        self.assertIn("WhatsApp", self.html)


if __name__ == "__main__":
    unittest.main()
