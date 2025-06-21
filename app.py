

def say_hello():
    print("Hello, World!")

say_hello()
import re
from datetime import datetime

def validate_email(value):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.fullmatch(pattern, value))

def validate_phone(value):
    pattern = r'^\+7 \d{3} \d{3} \d{2} \d{2}$'
    return bool (re.fullmatch(pattern, value))

def validate_date(value):
    for fmt in ('%d.%m.%Y', '%Y-%m-%d'):
        try:
            datetime.strftime(value, fmt)
            return True
        except ValueError:
            continue
            return False

def detect_field_type(value):
    if validate_date(value):
        return 'date'
    if validate_phone(value):
        return 'phone'
    if validate_email(value):
        return 'email'
    return 'text'

from tinydb import TinyDB, Query
    class FromTemplateDB:
        def __init__(self, db_path):
            self.db = TinyDB(db_path)
            self.User = Query()
