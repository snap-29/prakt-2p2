import unittest
from app import Command

class TestCommandLineArgs(unittest.TestCase):
    def test_command_line_args(self):
        c = Command.from_command_line([ "get_tpl", "--login=vasya", "--f_name1=27.05.2025","--f_name2=+7 903 123 45 78"])
        self.assertEqual(c.name, "get_tpl")
        self.assertEqual(c.features.get("name1"), "27.05.2025")
        self.assertEqual(c.features.get("name2"), "+7 903 123 45 78")
        self.assertEqual(None, c.features.get("login"))

if __name__ == "__main__":
    unittest.main()