import sqlite3 as sqlite

params = {
    'term': config['term'],
    'year': config['year'],
    'level': config['level']
}

subjectTable = sqlite.connect('sniper.db')

def update_subjects():
    r = req.get('%s%s' % (config['base_url'], 'subjects.json') params=params)
    subjects = [(subject['subject'], subject['subjectDescription']) for subject in r.json()]
    subject_sql = "insert or ignore into subjects (code, description) values (?, ?)"
    with sqlite.connect('sniper.db') as conn:
        c = conn.cursor()
        c.executemany(subject_sql, subjects)
        conn.commit()

def update_campuses():
    r = req.get('%s%s' % (config['base_url'], 'init.json'), params=params)
    campuses = r.json()['campuses']
    campuses_sql = 'insert or ignore into campuses (campus) values (?)'
    with sqlite.connect('sniper.db') as conn:
        c = conn.cursor()
        c.executemany(campuses_sql, campuses)
        conn.commit()

update_subjects()
update_campuses()
