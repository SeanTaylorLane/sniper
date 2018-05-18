import yaml
from flask_mail import Mail, Message
from urllib.parse import urlencode
from security import get_new_token
import sqlite3 as sqlite
from multiprocessing import Pool

with open('config.yaml') as f:
    config = yaml.load(f)

mail = Mail()
EMAIL_SENDER = "Course Sniper <sniper@rutgers.io>"
REGISTER_URL = "https://sims.rutgers.edu/webreg/editSchedule.htm?login=cas&semesterSelection=%s&indexList=%%s" % ("%d%d" % (config['term'], config['year']))
register_params = {
}

app = None

def init_notifier(flask_app):
    global app
    app = flask_app
    mail.init_app(app)

def notify(uid, email, subject, course, section_number, index, section_title):
    print("Notifying", email)
    params = {
        "subject": subject,
        "course": course,
        "section_number": section_number,
        "email": email,
        "t": get_new_token()
    }
    resnipe_url = "https://sniper.rutgers.io/snipe?%s" % urlencode(params)
    params['section_number'] = 'all'
    resnipe_all = 'https://sniper.rutgers.io/snipe?%s' % urlencode(params)
    email_text = ("Section No. %s of %s(%s:%s) that you were watching looks open. Its index number is %s. " + \
                 "Click the link below to register for it!\n\n%s \n\nIf you don't get in, " + \
                 "please visit this URL:\n\n%s\n\nto continue watching it.\n\n" + \
                 "If you want to watch for all sections, pleaes visit the following url:\n\n%s\n\nSend any feedback to sniper@rutgers.io") % \
                 (section_number, section_title + " " if section_title != None and len(section_title) > 0 else "",
                  subject, course, index, REGISTER_URL % index, resnipe_url, resnipe_all)
    message = Message('[COURSE SNIPER] %s:%d:%s (Index %s) is open' % (subject, course, section_number, index), sender=EMAIL_SENDER)
    message.body = email_text
    message.add_recipient(email)
    with app.app_context():
        mail.send(message)
        query = 'delete from snipes where userid = %d and subject = %d and course = %d and section = %d or section = -100' % (uid, subject, course, int(section_number))
        print(query)
        with sqlite.connect('sniper.db') as conn:
            c = conn.cursor()
            c.execute(query)
            conn.commit()

def mp_wrapper_notify(args):
    notify(*args)

def notify_all(notify_list, subject, course, section_number, index, section_title):
    pool = Pool(20)
    pool.map(mp_wrapper_notify, [(uid, email, subject, course, section_number, index, section_title) for uid, email in notify_list])
