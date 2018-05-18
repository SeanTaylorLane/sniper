from cron import snipe
from notifier import init_notifier
from app import app

init_notifier(app)
snipe()
