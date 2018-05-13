class SniperCron:
    def __init__(self, config, fetch, notify):
        self.config = self.config
        self.fetch = fetch
        self.notify = notify

    def cron(self):
        self.notify(self.fetch(self.config))
