import unittest
from app import PhoneValidator

class TestPhoneValidator(unittest.TestCase):

    def setUp(self):
        self.phone_validator = PhoneValidator()

    def is_phone(self, number):
        return self.phone_validator.validate(number)

    def test_valid_phone_numbers(self):
        valid_numbers = [
            "+7 123 456 78 90",
            "+7 999 888 77 66",
            "+7 000 000 00 00",
            "+7 987 654 32 10"
        ]

        for number in valid_numbers:
            with self.subTest(number=number):
                self.assertEqual(
                    self.is_phone(number),
                    True,
                    f"Valid phone number {number} was not recognized"
                )

    def test_invalid_phone_numbers(self):
        invalid_numbers = [
            "81234567890",
            "+71234567890",
            "+7 123 456 78",
            "+7 123 456 78 90 12",
            "+8 123 456 78 90",
            "7 123 456 78 90",
            "+7 123 4567890",
            "+7 (123) 456-78-90",
            "phone number",
            "1234567890",
            "",
            None
        ]



        for number in invalid_numbers:
            with self.subTest(number=number):
                self.assertNotEqual(
                    self.is_phone(number),
                    True,
                    f"Invalid phone number {number} was recognized as valid"
                )

if __name__ == '__main__':
    unittest.main()