FROM python:3.10-slim-bullseye

WORKDIR /usr/src/app

COPY requirements.txt ./

COPY quote_bot ./quote_bot

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "-m", "quote_bot"]
