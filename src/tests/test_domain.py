import unittest
from app import DomainValidator


class DomainValidatorTest(unittest.TestCase):
    def setUp(self):
        self.validator = DomainValidator

    def is_domain(self, domain) -> bool:
        return self.validator.validate(domain)[0]

    def test_domain_fail(self):
        self.assertFalse(self.is_domain(None))
        self.assertFalse(self.is_domain(self.generate_long_domain(256, "b")))
        self.assertFalse(self.is_domain("ithub"))
        self.assertFalse(self.is_domain(self.generate_long_domain(64, "b")))
        self.assertFalse(self.is_domain("почта.рф"))
        self.assertFalse(self.is_domain("pochta.r0"))
        self.assertFalse(self.is_domain("pochta.r"))
        self.assertFalse(self.is_domain("pochta.localhost"))


    @staticmethod
    def generate_long_domain(l: int, c: str) -> str:
        return f"{c * l}.com"


if __name__ == '__main__':
    unittest.main()
