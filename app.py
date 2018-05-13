from flask import Flask
import yaml
from cron import snipe
from notifier import init_notifier

with open('config.yaml') as f:
    config = yaml.load(f)

app = Flask(__name__)
app.config = {**app.config, **config['mail']}

init_notifier(app)
snipe()
