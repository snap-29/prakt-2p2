import unittest
from app import CommandParser

class TestCommandLineArgs(unittest.TestCase):
    def test_command_line_args(self):
        features = CommandParser.parse([ "get_tpl", "--login=vasya", "--f_name1=27.05.2025","--f_name2=+7 903 123 45 78"])
        self.assertEqual(features.get("name1"), "27.05.2025")
        self.assertEqual(features.get("name2"), "+7 903 123 45 78")
        self.assertEqual(None, features.get("login"))

if __name__ == "__main__":
    unittest.main()