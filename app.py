from flask import Flask, request, render_template, make_response

import yaml, json

from wtforms import Form, TextField, SelectField, validators
from wtforms.validators import StopValidation
from werkzeug.contrib.fixers import ProxyFix

import re
import logging

import soc, security
from sniper import insert_snipes
from notifier import init_notifier

print("Starting server...")
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

    def validate_campus(form, field):
        if form.section.data not in soc.get_campuses():
            form.section.data = "NB"
        return True
    
    def save(self):
        insert_snipes(self.email.data, self.subject.data, self.course.data, self.section.data, self.campus.data)

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
    resp = make_response(render_template('home.html', form=form, subjects=soc.get_subjects(), campuses=soc.get_campuses()))
    resp.set_cookie("auth_token", security.get_new_token())
    return resp

@app.route('/snipe', methods=['GET'])
def snipe():
    form = SnipeForm(request.form)
    email = request.args['email']
    subject = request.args['subject']
    course = request.args['course']
    section = request.args['section_number']
    token = request.args['t']
    if security.verify_token(token):
        insert_snipes(email, subject, course, section, "NB")
        return render_template("success.html", form=form)
    return "400: Invalid Token", 400

@app.route('/faq', methods=['GET'])
def faq():
    return render_template('faq.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000)
