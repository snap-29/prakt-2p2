import unittest
from unittest.mock import patch
from io import StringIO
from app import start


class IntegrationTest(unittest.TestCase):

    def test_function_printing(self):
        with patch('sys.stdout', new=StringIO()) as fake_out:
            start(list(["get_tpl", "--f_login=george.sagomonmov@gmail.com", "--f_tel=+7 903 123 45 78"]))
            self.assertEqual("Данные пользователя", fake_out.getvalue().strip())

    def test_fail_command(self):
        with self.assertRaisesRegex(ValueError, r"Invalid command"):
            start(list(["got_tpl", "--f_login=george.sagomonmov@gmail.com", "--f_tel=+7 903 123 45 78"]))

    def test_fail_fields(self):
     with self.assertRaisesRegex(ValueError, r"No fields provided"):
            start(list(["get_tpl", "--login=george.sagomonmov@gmail.com", "--tel=+7 903 123 45 78"]))

    def test_template_not_found(self):
        with patch('sys.stdout', new=StringIO()) as fake_out:
            start(list(["get_tpl", "--f_login=george.sagomonmov@gmail.com", "--f_tsl=+7 903 123 45 78"]))
            self.assertEqual("No matching templates found", fake_out.getvalue().strip())

if __name__ == '__main__':
    unittest.main()
