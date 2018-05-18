from flask import Flask, request, render_template, make_response
import yaml
import soc
from sniper import insert_snipes
from notifier import init_notifier
import security
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
    subject = TextField("Subject")
    course = TextField("Course", [validators.Length(min=1, max=5), validators.NumberRange()])
    section = TextField("Section")
    
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
                return True
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
        insert_snipes(self.email.data, self.subject.data, self.course.data, self.section.data, "NB")

@app.route('/', methods=['GET', 'POST'])
def home():
    form = SnipeForm(request.form)
    if request.method == 'POST' and form.validate():
        try:
            token = request.cookies['auth_token']
            print("T", token)
            if security.verify_remove_token(token):
                form.save()
                return render_template('success.html', form=form)
        except KeyError:
            pass
    form = SnipeForm(request.args)
    resp = make_response(render_template('home.html', form=form, subjects=soc.get_subjects()))
    resp.set_cookie("auth_token", security.get_new_token())
    return resp

@app.route('/snipe', methods=['POST'])
def snipe():
    print(request.args)

@app.route('/faq', methods=['GET'])
def faq():
    pass

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
