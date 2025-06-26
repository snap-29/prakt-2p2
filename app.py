import re
import socket
import argparse
from tinydb import TinyDB, Query
from typing import Dict, Optional
from datetime import datetime
from typing import Union, Optional
from typing import Dict, Optional, List
import argparse
from enum import Enum

class FieldType(Enum):
    """Типы данных для валидации параметров"""
    TEXT = "text"
    EMAIL = "email"
    PHONE = "phone"
    DATE = "date"

class Command:
    def __init__(self, name: str, params: Optional[Dict[str, str]] = None):
        """
        :param name: Название команды
        :param params: Параметры в формате {ключ: значение}
        """
        self.name = name
        self.features = params or {}

    def add_feature(self, key: str, value: str):
        """Добавить параметр"""
        self.features[key] = value

    def get_feature(self, key: str) -> Optional[str]:
        """Получить значение параметра"""
        return self.features.get(key)

    @classmethod
    def from_command_line(cls, args: List[str]):
        """
        Создает команду из аргументов командной строки
        Формат: command_name --key1=value1 --key2=value2
        """
        parser = argparse.ArgumentParser()
        parser.add_argument("command_name")
        args, unknown = parser.parse_known_args(args)

        features = {}
        for arg in unknown:
            if arg.startswith("--"):
                key_value = arg[2:].split("=", 1)
                if len(key_value) == 2 and key_value[0].startswith("f_"):
                    features[key_value[0][2:]] = key_value[1]

        return cls(args.command_name, features)

    def __str__(self):
        features_str = " ".join(f"--{k}={v}" for k, v in self.features.items())
        return f"{self.name} {features_str}".strip()



def validate_type(vallue_type: FieldType, value) -> bool:
    if vallue_type == FieldType.EMAIL:
        return is_email(value)
    elif vallue_type == FieldType.PHONE:
        return is_phone(value)
    elif vallue_type == FieldType.DATE:
        return is_date(value)
    return isinstance(value, str)


def is_date(date_str: str) -> bool:

    if match := re.fullmatch(r'^(\d{2})\.(\d{2})\.(\d{4})$', date_str):
        day, month, year = match.groups()
        sep = '.'
    elif match := re.fullmatch(r'^(\d{4})-(\d{2})-(\d{2})$', date_str):
        year, month, day = match.groups()
        sep = '-'
    else:
        return False

    try:
        datetime.strptime(f"{year}{sep}{month}{sep}{day}", f"%Y{sep}%m{sep}%d")
        return True
    except ValueError:
        return False



def is_phone(value: str) -> bool:
    if not isinstance(value, str):
       return False
    phone_pattern = r'^\+7 \d{3} \d{3} \d{2} \d{2}$'
    return re.fullmatch(phone_pattern, value) is not None

import re
from typing import Optional

def validate_domain(domain: str) -> tuple[bool, Optional[str]]:

    domain = domain.strip().lower()
    domain = re.sub(r'^https?://', '', domain)
    domain = re.sub(r'^ftp://', '', domain)
    domain = re.sub(r'/.*$', '', domain)        # Удаляем путь после /

    if not domain:
        return False, "Домен не может быть пустым"

    if len(domain) > 253:
        return False, "Длина домена превышает 253 символа"

    subdomains = domain.split('.')
    if len(subdomains) < 2:
        return False, "Должен быть хотя бы один поддомен и TLD"

    for part in subdomains:
        if not part:
            return False, "Поддомен не может быть пустым (две точки подряд)"

        if len(part) > 63:
            return False, f"Поддомен '{part}' превышает 63 символа"

        if not re.match(r'^[a-z0-9-]+$', part):
            return False, f"Поддомен '{part}' содержит недопустимые символы"

        if part.startswith('-') or part.endswith('-'):
            return False, f"Поддомен '{part}' не может начинаться/заканчиваться дефисом"

    tld = subdomains[-1]
    if not re.match(r'^[a-z]+$', tld):
        return False, "TLD должен содержать только буквы"

    if len(tld) < 2:
        return False, "TLD должен быть минимум 2 символа"

    if tld in ('test', 'localhost', 'example'):
        return False, f"Зарезервированный TLD: {tld}"

    return True, None


def is_email(email):
    if not email or not isinstance(email, str):
        return False

    email_pattern = re.compile(
        r'^[a-zA-Z0-9._%+-]+@'
        r'([a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        r'|(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}))$'
    )

    if not email_pattern.match(email):
        return False

    if '@' in email:
        username = email.split('@')[0]
        if username.startswith('.') :
            return False
        domain = email.split('@')[1]
        if domain.replace('.', '').isdigit():
            try:
                socket.inet_aton(domain)  # Проверка валидности IPv4
                return True
            except socket.error:
                return False
        else:
            return validate_domain(domain)[0]

    return True


def determine_field_type(value: str) -> str:
    if is_date(value):
        return "date"
    if is_phone(value):
        return "phone"
    if is_email(value):
        return "email"
    return "text"

def find_matching_template(input_fields: Dict[str, str], db: TinyDB) -> Optional[Dict]:
    Form = Query()

    for template in db.all():
        template_fields = {k: v for k, v in template.items() if k != "name"}
        match = True

        for field_name, field_type in template_fields.items():
            if field_name not in input_fields:
                match = False
                break
            if input_fields[field_name] != field_type:
                match = False
                break

        if match:
            return template

    return None

def main():
    parser = argparse.ArgumentParser(description='Сопоставитель шаблонов форм')
    parser.add_argument('command', type=str, help='Команда для выполнения (get_tpl)')
    parser.add_argument('fields', nargs='*', help='Входные поля в формате --имя=значение')

    args = parser.parse_args()

    if args.command != 'get_tpl':
        print("Неизвестная команда")
        return

    input_fields = {}
    field_types = {}

    for field in args.fields:
        if field.startswith('--'):
            field = field[2:]
            if '=' in field:
                name, value = field.split('=', 1)
                field_type = determine_field_type(value)
                input_fields[name] = field_type
                field_types[name] = field_type

    db = TinyDB('forms_db.json')

    template = find_matching_template(input_fields, db)

    if template:
        print(template['name'])
    else:
        print('{')
        for i, (name, type_) in enumerate(field_types.items()):
            print(f'  {name}: {type_}' + (',' if i < len(field_types) - 1 else ''))
        print('}')

if __name__ == '__main__':
    main()