FROM python:3.10-slim-bullseye as base
WORKDIR /usr/src/app

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt


FROM base as development

COPY . ./

CMD ["python", "-m", "quote_bot"]


FROM base as production

COPY quote_bot ./quote_bot

CMD ["python", "-m", "quote_bot"]
