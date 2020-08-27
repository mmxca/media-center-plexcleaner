FROM alpine:latest

RUN mkdir /app && \
    mkdir /logs && \
    apk add --no-cache git python3 py3-pip 

COPY 'PlexVideoCleaner.py' '/app' 
COPY 'requirements.txt' '/app'

RUN cd /app && \
    pip3 install --upgrade pip && \
    python3 -m pip install --user virtualenv && \
    python3 -m venv env && \
    source env/bin/activate && \
    pip3 install --upgrade pip && \
    pip3 install -r /app/requirements.txt && \
    chmod 755 /app/PlexVideoCleaner.py && \
    mv /etc/inittab /tmp/inittab && \
    sed "s/^tty/#tty/g" /tmp/inittab > /etc/inittab && \
    (crontab -l 2>/dev/null; echo "0 * * * * /app/PlexVideoCleaner.py >> /logs/plexcleaner.log") | crontab -

VOLUME /logs

WORKDIR /app

ENTRYPOINT ["/sbin/init"]
