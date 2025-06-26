import unittest
from app import EmailValidator

class TestEmailValidator(unittest.TestCase):
    def setUp(self):
        self.email_validator = EmailValidator()

    def is_email(self, email):
        return self.email_validator.validate(email)

    def test_valid_emails(self):
        valid_emails = [
            "user@example.com",
            "firstname.lastname@example.com",
            "email@subdomain.example.com",
            "firstname+lastname@example.com",
            "email@123.123.123.123",
            "1234567890@example.com",
            "email@example-one.com",
            "_______@example.com",
            "email@example.name",
            "email@example.museum",
            "email@example.co.jp",
            "firstname-lastname@example.com"
        ]

        for email in valid_emails:
            with self.subTest(email=email):
                self.assertEqual(
                    self.is_email(email),
                    True,
                    f"Valid email {email or 'None'} was not recognized"
                )

    def test_invalid_emails(self):
        invalid_emails = [
            "plainaddress",
            "@missingusername.com",
            "username@.com",
            ".username@example.com",
            "username@example..com",
            "username@example.com.",
            "username@example_com",
            "user name@example.com",
            "username@example.c",
            "username@.org",
            "username@111.222.333.44444",
            "username@111.222.333.444",
            "",
            None,
            "username@example..com",
            "username@-example.com",
            "username@example.",
            "username@.example.com"
        ]

        for email in invalid_emails:
            with self.subTest(email=email):
                self.assertEqual(
                    self.is_email(email),
                    False,
                    f"Invalid email {email or 'None'} was recognized as valid"
                )


if __name__ == '__main__':
    unittest.main()