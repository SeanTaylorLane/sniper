import requests

def get_current_tylc():
    try:
        initJson = requests.get('https://nstanlee.rutgers.edu/4/init.json').json()
        term, year = [v for k, v in initJson['semesters'][0].items()]
        level = 'u'
        campus = 'nb'
        return {'term': term, 'year': year, 'level': level, 'campus': campus}
    except JSONDecodeError:
        print("Cannot pull init.json")
