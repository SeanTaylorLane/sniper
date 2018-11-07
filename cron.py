#!/usr/bin/env python
""" This represents the cronjob that runs to check for course openings"""
# from flask_mail import Message

import urllib, requests
from models import db, Snipe
from soc import Soc
from app import mail, app
import datetime
from collections import namedtuple
from utils import get_current_tylc
from flask_mail import Message
import sendgrid
import os
from sendgrid.helpers.mail import *
from secrets import mail_key
#import json

soc = Soc(**get_current_tylc())

EMAIL_SENDER = "Course Sniper <sniper@rutgers.io>"

Section = namedtuple('Section', ['number', 'section'])

def poll(open_sections, section, result=False):
    """ Poll a subject for open courses. """
    app.logger.warning("Polling for %s" % (section))
    if section in open_sections:
        snipes = Snipe.query.filter(Snipe.section==str(section))
        for snipe in snipes:
            notify(snipe, section)

def notify(snipe, section):
    """ Notify this snipe that their course is open"""
    course = '%s' % (snipe.section)

    if snipe.user.email:

        attributes = {
            'email': snipe.user.email,
            'section': snipe.section,
        }

        # build the url for prepopulated form
        url = 'http://sniper.rutgers.io/?%s' % (urllib.parse.urlencode(attributes))
        semester = str(get_current_tylc()["term"]) + str(get_current_tylc()["year"])
        register_url = 'https://sims.rutgers.edu/webreg/editSchedule.htm?login=cas&semesterSelection=' + semester + '&indexList=%s' % (section)

        email_text = 'A course (%s) that you were watching looks open. Its section number is %s. Click the link below to register for it!\n\n %s \n\n If you don\'t get in, visit this URL: \n\n %s \n\n to continue watching it.\n\n Send any feedback to sniper@rutgers.io' % (course, section, register_url, url)

        # send out the email
        from cron import EMAIL_SENDER

        sg = sendgrid.SendGridAPIClient(apikey=mail_key)
        from_email = Email("sniper@rutgers.io", "Course Sniper")
        to_email = Email(snipe.user.email)
        subject = '[Course Sniper](%s) is open' %(course)
        content = Content("text/plain", email_text)
        mail = Mail(from_email, subject, to_email, content)
        response = sg.client.mail.send.post(request_body=mail.get())
        print(response.status_code)
        print(response.body)
        print(response.headers)

    db.session.delete(snipe)
    db.session.commit()

    app.logger.warning('Notified user: %s about snipe %s' % (snipe.user, snipe))



if __name__ == '__main__':
    # get all the courses that should be queried.
    app.logger.warning("----------- Running the Cron %s " % (str(datetime.datetime.now())))
    sections = db.session.query(Snipe.section).distinct().all()
    open_sections = soc.get_sections()
    for section in sections:
        # print(section[0])
        poll(open_sections, section[0])
