FROM alpine:latest

WORKDIR /app

ADD . /app

ADD crontab /etc/cron.d/soc-cron

RUN chmod 0644 /etc/cron.d/soc-cron

RUN touch /var/log/cron.log

RUN apk add --no-cache python3 && \
    python3 -m ensurepip && \
    rm -r /usr/lib/python*/ensurepip && \
    pip3 install --upgrade pip setuptools && \
    if [ ! -e /usr/bin/pip ]; then ln -s pip3 /usr/bin/pip ; fi && \
    if [[ ! -e /usr/bin/python ]]; then ln -sf /usr/bin/python3 /usr/bin/python; fi && \
    rm -r /root/.cache

RUN apk add --no-cache sqlite

RUN pip install --trusted-host pypi.python.org -r pip.req

EXPOSE 80

ENV NAME World

CMD ["python", "app.py"]

CMD cron && tail -f /var/log/cron.log
