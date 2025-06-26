import unittest
from tinydb import TinyDB, Query
from app import find_form_by_fields

class TestFindFromDb(unittest.TestCase):
    def test_find_form_by_fields(self):
        db = TinyDB('forms_db.json', ensure_ascii=False, encoding='utf-8')
        result = find_form_by_fields(['order_date', 'login'], db)
        self.assertEqual(len(result), 1)
