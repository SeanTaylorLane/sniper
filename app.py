""" This file sets up the Flask Application for sniper.
    Sniper is an application that hits the Rutgers SOC API and notifies users when a class opens up. """

from flask import Flask, render_template, request
from wtforms import Form, TextField, validators
from wtforms.validators import StopValidation
from models import Snipe, db, User
from flask_mail import Mail
from secrets import mail_username, mail_password
from soc import Soc
from werkzeug.contrib.fixers import ProxyFix
import re
import json

import logging
from logging import Formatter, FileHandler
from utils import get_current_tylc
import os

# Set up the Flask application
app = Flask(__name__)

file_path = os.path.abspath(os.getcwd())+"\database.db"

# Set up a file for logging
file_handler = FileHandler('everything.log')
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
app.logger.addHandler(file_handler)

app.wsgi_app = ProxyFix(app.wsgi_app)

app.config['MAIL_SERVER'] = 'smtp.sendgrid.net'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = mail_username
app.config['MAIL_PASSWORD'] = mail_password
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///'+file_path


db.init_app(app)
mail = Mail(app)

class SnipeForm(Form):
    """ Represents the Snipe form on the homepage. """
    email = TextField('Email', [validators.Email(), validators.Required()])
    section = TextField('section')

    def validate_section(form, field):
        if not form.section.data.isdigit():
            m = re.search('(\d+)', form.section.data)
            if m:
                form.section.data = m.group(1)
            else:
                raise StopValidation('Please enter a valid section')
        return True

    def save(self):
        """ Saves to SQLAlchemy User and Snipe models """

        snipe = Snipe.create(self.email.data, self.section.data)

        db.session.add(snipe)
        db.session.commit()


@app.route('/', methods=['GET', 'POST'])
def home():
    """ Handles the home page rendering."""
    soc = Soc(**get_current_tylc())

    form = SnipeForm(request.form)
    if request.method == 'POST' and form.validate():
        form.save()
        return render_template('success.html', form=form)
    if not request.form:
        # this trick allows us to prepopulate entries using links sent out in emails.
        form = SnipeForm(request.args)
    # change to return home.html when active
    return render_template('home.html', form=form)

@app.route('/faq', methods=['GET'])
def faq():
    return render_template('faq.html')

@app.route('/test', methods=['GET', 'POST'])
def ajaxtest():
    result = {
        'success': test(),
    }
    return json.dumps(result)

def test():
    from cron import poll
    soc = Soc(**get_current_tylc())
    return True

if __name__ == '__main__':
    test()
    app.run(host='0.0.0.0', debug=True)
