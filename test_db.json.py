from tinydb import TinyDB, Query
db = TinyDB('forms_db.json', ensure_ascii=False, encoding='utf-8')

def find_form_by_fields(fields):
    Form = Query()
    query = None

    for field in fields:
        if query is None:
            query = Form[field].exists()
        else:
            query &= Form[field].exists()

    return db.search(query)


result = find_form_by_fields(['order_date', 'login'])
print(result)