import secrets
import sqlite3 as sqlite

conn = sqlite.connect("sniper.db")

def init_secrets():
    c = conn.cursor()
    c.execute('''
    create table if not exists tokens(
        token text not null primary key
    )
    ''')
    conn.commit()

def insert_token(token):
    print(token)
    query = 'insert or ignore into tokens (token) values ("%s")' % token
    c = conn.cursor()
    c.execute(query)
    conn.commit()
    print("INSERT COMMITTED")

def get_new_token():
    token = secrets.token_urlsafe(32)
    insert_token(token)
    return token

def verify_token(token):
    query = 'select * from tokens where token="%s"' % token
    c = conn.cursor()
    c.execute(query)
    return c.fetchone() != None

def remove_token(token):
    if len(token.strip()) > 0:
        query = 'delete from tokens where token="%s"' % token
        c = conn.cursor()
        c.execute(query)
        conn.commit()

def verify_remove_token(token):
    if verify_token(token):
        remove_token(token)
        return True
    return False

init_secrets()
