import requests as req
import yaml
import sqlite3 as sqlite

import sniper
import notifier

conn = sqlite.connect("sniper.db")

with open('config.yaml') as f:
    config = yaml.load(f)

params = {
    'term': config['term'],
    'year': config['year'],
    'level': config['level']
}

def get_open_sections(subject, course, campus):
    scc_params = {
        'subject': subject,
        'course': course,
        'campus': campus
    }
    r = req.get('https://nstanlee.rutgers.edu/4/sections.json', params={**params, **scc_params})
    return [(section['number'], section['sectionIndex'], section['openStatus'], section['title']) for section in r.json() if section['openStatus'] == 1]

def snipe():
    targets = sniper.get_snipe_targets()
    sections = {}
    for t in targets:
        try:
            sections[(t[0], t[1], t[3])].append(t[2])
        except KeyError:
            sections[(t[0], t[1], t[3])] = [t[2]]
    open_sections = {ssc: get_open_sections(*ssc) if len(section_list) > 0 else [] for ssc, section_list in sections.items()}
    # print("OS", open_sections)
    c = conn.cursor()
    for ssc, sections in open_sections.items():
        if len(sections) > 0:
            for section in sections:
                # print(section)
                query = '''
                select u.email from users u join snipes s using (userid)
                where s.subject=%d and s.course=%d and s.section=%d or s.section=-100 and s.campus="%s"''' % (ssc[0], ssc[1], int(section[0]), ssc[2])
                print(query)
                # print(ssc, section)
                c.execute(query)
                # print(c.fetchall())
                notifier.notify(set([u[0] for u in c.fetchall()]), ssc[1], ssc[0], section[0], str(section[1]).zfill(5), section[3])
