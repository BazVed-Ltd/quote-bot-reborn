FROM python:3.10-slim-bullseye
WORKDIR /usr/src/app
COPY requirements.txt ./
RUN apt-get update &&\
 apt-get install --no-install-recommends -y gcc libc6-dev &&\
 pip install --no-cache-dir -r requirements.txt &&\
 apt-get purge -y --autoremove gcc libc6-dev &&\
 rm -rf /var/lib/{apt,dpkg,cache,log}/
COPY quote_bot ./quote_bot
CMD ["python", "-m", "quote_bot"]
