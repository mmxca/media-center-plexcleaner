FROM alpine:latest

RUN mkdir /app && \
    mkdir /logs && \
    apk add --no-cache git python3 py3-pip runit tini

COPY service /app/service

COPY 'PlexVideoCleaner.py' '/app' 
COPY 'requirements.txt' '/app'

RUN chmod 744 /app/service/plexcleaner/run && \
    cd /app && \
    pip3 install --upgrade pip && \
    python3 -m pip install --user virtualenv && \
    python3 -m venv env && \
    source env/bin/activate && \
    pip3 install --upgrade pip && \
    pip3 install plexapi && \
    pip3 install -r /app/requirements.txt && \
    chmod 755 /app/PlexVideoCleaner.py && \
    dos2unix /app/PlexVideoCleaner.py && \
    dos2unix /app/service/plexcleaner/run

VOLUME /logs

WORKDIR /app

ENTRYPOINT ["tini", "--"]
CMD ["runsvdir", "/app/service"]