import yaml
from flask_mail import Mail, Message
from urllib.parse import urlencode
from security import get_new_token

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

def notify(notify_list, subject, course, section_number, index, section_title):
    print(notify_list, subject, course, section_number, index, section_title)
    for email in notify_list:
        print("Notifying", email)
        params = {
            "subject": subject,
            "course": course,
            "section_number": section_number,
            "email": email,
            "t": get_new_token()
        }
        resnipe_url = "https://sniper.rutgers.io/snipe?%s" % urlencode(params)
        email_text = ("Section %s of %s(%s:%s) that you were watching looks open. Its index number is %s. " + \
                     "Click the link below to register for it!\n\n%s \n\nIf you don't get in, " + \
                     "please visit this URL:\n\n%s\n\nto continue watching it.\n\nSend any feedback to sniper@rutgers.io") % \
                     (section_number, section_title + " " if section_title != None and len(section_title) > 0 else "",
                      subject, course, index, REGISTER_URL % index, resnipe_url)
        message = Message('[COURSE SNIPER] %s:%d:%s (index %s) is open' % (subject, course, section_number, index), sender=EMAIL_SENDER)
        message.body = email_text
        message.add_recipient(email)
        with app.app_context():
            mail.send(message)
