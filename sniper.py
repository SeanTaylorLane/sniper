import sqlite3 as sqlite

def create_tables():
    with sqlite.connect('sniper.db') as conn:
        c = conn.cursor()
        c.execute('''
        create table if not exists snipes(
            userid integer not null,
            subject integer not null,
            course integer not null,
            section integer not null,
            campus text not null,
            notify_email integer,
            notify_text integer,
            primary key (userid, subject, course, section, campus)
        )
        ''')

        c.execute('''
        create table if not exists users(
            userid integer primary key autoincrement,
            email text not null unique
        )
        ''')
        conn.commit()

def init_sniper():
    create_tables()

def get_userid(email):
    with sqlite.connect('sniper.db') as conn:
        c = conn.cursor()
        query = 'select userid from users where email="%s"' % email
        c.execute(query)
        return c.fetchone()[0]

def insert_snipes(email, subject, course, sections, campus):
    with sqlite.connect('sniper.db') as conn:
        c = conn.cursor()
        insert_user = 'insert or ignore into users (email) values ("%s")' % email
        c.execute(insert_user)
        conn.commit()
    with sqlite.connect('sniper.db') as conn:
        c = conn.cursor()
        userid = get_userid(email)
        snipes = [(userid, subject, course, section, campus) for section in sections]
        insert_snipe_query = 'insert or ignore into snipes (userid, subject, course, section, campus, notify_email, notify_text) values (?, ?, ?, ?, ?, 1, 0)'
        c.executemany(insert_snipe_query, snipes)
        conn.commit()

def get_snipe_targets():
    with sqlite.connect('sniper.db') as conn:
        c = conn.cursor()
        query = "select distinct subject, course, section, campus from snipes"
        c.execute(query)
        return c.fetchall()

init_sniper()
