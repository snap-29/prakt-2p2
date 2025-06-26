from tinydb import TinyDB

def initialize_test_db():
    db = TinyDB('forms_db.json', ensure_ascii=False, encoding='utf-8')
    db.truncate()

    db.insert({
        "name": "Данные пользователя",
        "login": "email",
        "tel": "phone"
    })

    db.insert({
        "name": "Форма заказа",
        "customer": "text",
        "order_id": "text",
        "order_date": "date",
        "contact": "phone"
    })

    db.insert({
        "name": "Проба",
        "f_name1": "email",
        "f_name2": "date"
    })
    db.insert({
        "name": "Проба2",
        "login": "email",
        "order_date": "date",
    })
    db.insert({
        "name": " Данные пользователя",
        "login": "email",
        "order_id": "text",
        "contact": "phone"
    })

if __name__ == '__main__':
    initialize_test_db()

