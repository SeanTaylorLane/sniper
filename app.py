from flask import Flask, request, render_template
import yaml
from cron import snipe
import soc
from notifier import init_notifier
from wtforms import Form, TextField, SelectField, validators
from wtforms.validators import StopValidation
from werkzeug.contrib.fixers import ProxyFix
import re
import json

import logging

with open('config.yaml') as f:
    config = yaml.load(f)

app = Flask(__name__)
app.config = {**app.config, **config['mail']}

logfile = logging.FileHandler("sniper.log")
logfile.setLevel(logging.INFO)
logfile.setFormatter(logging.Formatter("%(asctime)s %(levelname)s: %(message)s [in $(mathname)s:$(lineno)d]"))
app.logger.addHandler(logfile)

app.wsgi_app = ProxyFix(app.wsgi_app)

def parse_section(section):
    if re.match('^\d+$', section):
        return int(section)
    if re.match('^\d+-\d+$', section):
        section_start, section_end = section.split('-')
        return list(range(int(section_start), int(section_end)+1))
    return None

class SnipeForm(Form):
    email = TextField("Email", [validators.Email(), validators.Required()])
    subject = SelectField("Subject", choices=[(subject['code'], '%s (%d)' % (subject['description'], subject['code'])) for subject in soc.get_subjects()])
    course = TextField("Course", [validators.Length(min=2, max=4), validators.NumberRange()])
    section = TextField("Section")
    campus = TextField("Campus")

    def validate_subject(form, field):
        if not form.subject.data.isdigit():
            m = re.search('(\d+)', form.subject.data)
            if m:
                form.subject.data = m.group(1)
            else:
                raise StopValidation("Please enter valid subject")
        print("SUBJECT OKAY")
        return True

    def validate_course(form, field):
        if form.course.data.isdigit():
            form.course.data = int(form.course.data)
        print("COURSE OKAY")
        return True

    def validate_section(form, field):
        sections = [ss for ss in form.section.data.split(',') if ss != '']
        print("SECTIONS", sections)
        if len(sections) == 0:
                form.section.data = [-100]
        parsed_sections = []
        for section in sections:
            parsed = parse_section(section)
            if parsed == None:
                raise StopValidation("Please enter valid section or section range. %s is not a valid input." % section)
            try:
                parsed_sections += parsed
            except TypeError:
                parsed_sections.append(parsed)
        form.section.data = parsed_sections
        print("SECTION OKAY")
        return True

    def save(self):
        pass

@app.route('/', methods=['GET', 'POST'])
def home():
    form = SnipeForm(request.form)
    if request.method == 'POST':
        print(form.validate())
    if request.method == 'POST' and form.validate():
        print("SUCCESS")
        form.save()
        return render_template('success.html', form=form)
    form = SnipeForm(request.args)
    return render_template('home.html', form=form, subjects=soc.get_subjects())

@app.route('/snipe', methods=['POST'])
def snipe():
    pass

@app.route('/faq', methods=['GET'])
def faq():
    pass

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
