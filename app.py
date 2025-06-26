import argparse
import socket
import sys
from datetime import datetime
from enum import Enum
from typing import Dict, Optional, List

from tinydb import TinyDB, Query


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
    domain = re.sub(r'/.*$', '', domain)  # Удаляем путь после /

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
        if username.startswith('.'):
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


def find_form_by_fields(fields: List[str], db: TinyDB) -> List[Dict]:
    """
    Находит формы, содержащие все указанные поля.

    Args:
        fields: Список имен полей для поиска
        db: Экземпляр TinyDB для поиска

    Returns:
        Список словарей с найденными формами
    """
    Form = Query()
    query = None

    # Строим запрос для проверки существования всех полей
    for field in fields:
        if query is None:
            query = Form[field].exists()
        else:
            query &= Form[field].exists()

    # Ищем документы, содержащие все указанные поля
    documents = db.search(query)

    # Фильтруем документы, где количество полей точно совпадает
    # (исключая поле 'name')
    result = []
    for doc in documents:
        # Получаем только пользовательские поля (исключая 'name')
        doc_fields = {k: v for k, v in doc.items() if k != 'name'}
        if len(doc_fields) == len(fields):
            result.append(doc)

    return result


def is_matching_template(form: Dict[str, str], fields: Dict[str, str]) -> bool:
    form_fields = {k: v for k, v in form.items() if k != 'name'}
    for field in form_fields:
        ft = FieldType(form_fields.get(field))
        if not validate_type(ft, fields[field]):
            return False
    return True


def main():
    args = sys.argv
    command = Command.from_command_line(args[1:])
    if command.name != "get_tpl":
        print(f"Неверная команда {command.name}")
        return
    if command.features.items().__len__() == 0:
        print("Отсутствуют поля")

    db = TinyDB('forms_db.json', ensure_ascii=False, encoding='utf-8')
    r = find_form_by_fields(list(command.features.keys()), db)
    for doc in r:
        if (is_matching_template(doc, command.features)):
            print(doc['name'])


if __name__ == '__main__':
    main()
