import os
import unittest
from main import collect_placeholders_for_language, read_txt_file

class TestOfferDocGenerator(unittest.TestCase):
    def setUp(self):
        # Create temporary test files
        self.test_dir = "test_temp"
        os.makedirs(self.test_dir, exist_ok=True)
        with open(os.path.join(self.test_dir, "testEN.txt"), "w", encoding="utf-8") as f:
            f.write("English content")
        with open(os.path.join(self.test_dir, "testDE.txt"), "w", encoding="utf-8") as f:
            f.write("German content")

    def tearDown(self):
        # Clean up temporary test files
        for file in os.listdir(self.test_dir):
            os.remove(os.path.join(self.test_dir, file))
        os.rmdir(self.test_dir)

    def test_read_txt_file(self):
        # Test reading a valid file
        content = read_txt_file(os.path.join(self.test_dir, "testEN.txt"))
        self.assertEqual(content, "English content")

        # Test reading a nonexistent file
        content = read_txt_file("nonexistent.txt")
        self.assertEqual(content, "")

    def test_collect_placeholders_for_language(self):
        # Test collecting placeholders for English
        placeholders = collect_placeholders_for_language(self.test_dir, "EN")
        self.assertIn("test", placeholders)
        self.assertEqual(placeholders["test"], "English content")

        # Test collecting placeholders for German
        placeholders = collect_placeholders_for_language(self.test_dir, "DE")
        self.assertIn("test", placeholders)
        self.assertEqual(placeholders["test"], "German content")

        # Test collecting placeholders for a nonexistent language
        placeholders = collect_placeholders_for_language(self.test_dir, "FR")
        self.assertEqual(placeholders, {})


if __name__ == "__main__":
    unittest.main()
