import argparse
import re
import socket
import sys
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Tuple

from tinydb import TinyDB, Query


class FieldType(Enum):
    """Supported field types for form validation"""
    TEXT = "text"
    EMAIL = "email"
    PHONE = "phone"
    DATE = "date"


class FormFinder:
    """Handles form template matching and validation"""

    def __init__(self, db_path: str = 'forms_db.json'):
        self.db = TinyDB(db_path, ensure_ascii=False, encoding='utf-8')

    def find_matching_templates(self, fields: Dict[str, str]) -> List[str]:
        """Find all templates that match the provided fields"""
        potential_templates = self._find_templates_with_fields(list(fields.keys()))
        return [
            template['name'] for template in potential_templates
            if self._validate_template(template, fields)
        ]

    def _find_templates_with_fields(self, fields: List[str]) -> List[Dict]:
        Form = Query()
        query = None
        # Строим запрос для проверки существования всех полей
        for field in fields:
            if query is None:
                query = Form[field].exists()
            else:
                query &= Form[field].exists()

        # Ищем документы, содержащие все указанные поля
        documents = self.db.search(query)

        # Фильтруем документы, где количество полей точно совпадает
        # (исключая поле 'name')
        result = []
        for doc in documents:
            # Получаем только пользовательские поля (исключая 'name')
            doc_fields = {k: v for k, v in doc.items() if k != 'name'}
            if len(doc_fields) == len(fields):
                result.append(doc)

        return result


    def _validate_template(self, template: Dict[str, str], fields: Dict[str, str]) -> bool:
        """Validate if template matches the field types"""
        template_fields = {k: v for k, v in template.items() if k != 'name'}
        return all(
            self._validate_field_type(
                FieldType(template_fields[field]),
                fields[field]
            )
            for field in template_fields
        )

    @staticmethod
    def _validate_field_type(field_type: FieldType, value: str) -> bool:
        """Validate a single field against its type"""
        validators = {
            FieldType.EMAIL: EmailValidator.validate,
            FieldType.PHONE: PhoneValidator.validate,
            FieldType.DATE: DateValidator.validate,
            FieldType.TEXT: lambda x: isinstance(x, str)
        }
        return validators[field_type](value)


class EmailValidator:
    """Email validation utilities"""

    EMAIL_PATTERN = re.compile(
        r'^[a-zA-Z0-9._%+-]+@'
        r'([a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        r'|(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}))$'
    )

    @classmethod
    def validate(cls, email) -> bool:
        """Validate email format and domain"""
        if not email or not isinstance(email, str):
            return False

        if not cls.EMAIL_PATTERN.match(email):
            return False

        username, domain = email.split('@', 1)
        if username.startswith('.'):
            return False

        if domain.replace('.', '').isdigit():
            try:
                socket.inet_aton(domain)
                return True
            except socket.error:
                return False

        return DomainValidator.validate(domain)[0]


class PhoneValidator:
    """Phone number validation utilities"""

    PHONE_PATTERN = re.compile(r'^\+7 \d{3} \d{3} \d{2} \d{2}$')

    @classmethod
    def validate(cls, phone: str) -> bool:
        """Validate phone number format"""
        return isinstance(phone, str) and bool(cls.PHONE_PATTERN.match(phone))


class DateValidator:
    """Date validation utilities"""

    DATE_FORMATS = [
        (r'^(\d{2})\.(\d{2})\.(\d{4})$', '%d.%m.%Y'),
        (r'^(\d{4})-(\d{2})-(\d{2})$', '%Y-%m-%d')
    ]

    @classmethod
    def validate(cls, date_str: str) -> bool:
        """Validate date format"""
        if not date_str or not isinstance(date_str, str):
            return False

        for pattern, date_format in cls.DATE_FORMATS:
            if re.fullmatch(pattern, date_str):
                try:
                    datetime.strptime(date_str, date_format)
                    return True
                except ValueError:
                    continue
        return False


class DomainValidator:
    """Domain validation utilities"""

    @classmethod
    def validate(cls, domain) -> Tuple[bool, Optional[str]]:
        """Validate domain name format"""
        if not domain:
            return False, "Domain cannot be empty"
        domain = domain.strip().lower()

        if len(domain) > 253:
            return False, "Domain exceeds maximum length (253 chars)"

        subdomains = domain.split('.')
        if len(subdomains) < 2:
            return False, "Domain must have at least one subdomain and TLD"

        for part in subdomains:
            if not part:
                return False, "Empty subdomain (consecutive dots)"

            if len(part) > 63:
                return False, f"Subdomain '{part}' exceeds maximum length (63 chars)"

            if not re.match(r'^[a-z0-9-]+$', part):
                return False, f"Subdomain '{part}' contains invalid characters"

            if part.startswith('-') or part.endswith('-'):
                return False, f"Subdomain '{part}' cannot start/end with hyphen"

        tld = subdomains[-1]
        if not re.match(r'^[a-z]+$', tld):
            return False, "TLD must contain only letters"

        if len(tld) < 2:
            return False, "TLD must be at least 2 characters"

        if tld in ('test', 'localhost', 'example'):
            return False, f"Reserved TLD: {tld}"

        return True, None


class CommandParser:
    """Command line argument parser"""

    @staticmethod
    def parse(args: List[str]) -> Dict[str, str]:
        """Parse command line arguments into field dictionary"""
        parser = argparse.ArgumentParser()
        parser.add_argument("command_name")
        parsed_args, unknown = parser.parse_known_args(args)

        if parsed_args.command_name != "get_tpl":
            raise ValueError(f"Invalid command: {parsed_args.command_name}")

        features = {}
        for arg in unknown:
            if arg.startswith("--f_"):
                key_value = arg[4:].split("=", 1)
                if len(key_value) == 2:
                    features[key_value[0]] = key_value[1]

        if not features:
            raise ValueError("No fields provided")

        return features


def start(args: list[str]):

        fields = CommandParser.parse(args)
        form_finder = FormFinder()

        matching_templates = form_finder.find_matching_templates(fields)

        if matching_templates:
            print("\n".join(matching_templates))
        else:
            print("No matching templates found")

if __name__ == '__main__':
    try:
        start(sys.argv[1:])
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)
