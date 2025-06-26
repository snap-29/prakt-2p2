import unittest
from app import FormFinder

class TestFindFromDb(unittest.TestCase):
    def test_find_form_by_fields(self):
        formFinder = FormFinder()
        result = formFinder._find_templates_with_fields(['order_date', 'login'])
        self.assertEqual(len(result), 1)
