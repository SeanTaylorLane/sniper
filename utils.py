import requests

def get_current_tylc():
    try:
        term, year = 9, 2018
        level = 'u'
        campus = 'nb'
        return {'term': term, 'year': year, 'level': level, 'campus': campus}
    except JSONDecodeError:
        print("Cannot pull init.json")
