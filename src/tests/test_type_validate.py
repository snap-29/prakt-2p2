import unittest
from app import FormFinder, FieldType


class MyTestCase(unittest.TestCase):

    def testDate(self):
        self.assertEqual(FormFinder._validate_field_type(FieldType.DATE, "2023-01-01"), True)
        self.assertEqual(FormFinder._validate_field_type(FieldType.DATE, "202301-01"), False)

    def testPhone(self):
        self.assertEqual(FormFinder._validate_field_type(FieldType.PHONE, "+7 123 456 78 90"), True)
        self.assertEqual(FormFinder._validate_field_type(FieldType.PHONE, "+7 123--- 456 78 90 12"), False)

    def testEmail(self):
        self.assertEqual(FormFinder._validate_field_type(FieldType.EMAIL, "username@example.com"), True)
        self.assertEqual(FormFinder._validate_field_type(FieldType.EMAIL, "...username@example.com"), False)

    def testText(self):
        self.assertEqual(FormFinder._validate_field_type(FieldType.TEXT, "Hello, world!"), True)
        self.assertEqual(FormFinder._validate_field_type(FieldType.TEXT, None), False)

if __name__ == '__main__':
    unittest.main()
