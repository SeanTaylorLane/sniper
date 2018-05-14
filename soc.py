import requests as req
import yaml

with open('config.yaml') as f:
    config = yaml.load(f)

params = {
    'term': config['term'],
    'year': config['year'],
    'level': config['level']
}

subjects = None
def get_subjects():
    global subjects
    if not subjects:
        print("Populating subjects")
        r = req.get('%s%s' % (config['base_url'], 'subjects.json'), params=params)
        subjects = [{'code': subject['subject'], 'description': subject['subjectDescription']} for subject in r.json()]
    return subjects

