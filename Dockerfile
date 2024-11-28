FROM python:3.12-alpine AS base

WORKDIR /app

RUN apk add --update --virtual .build-deps \
    build-base \
    postgresql-dev \
    python3-dev \
    libpq

COPY Pipfile Pipfile.lock .
RUN pip install pipenv && pipenv requirements > requirements.txt && pip install -r requirements.txt

FROM python:3.12-alpine

WORKDIR /app
RUN apk add libpq

COPY --from=base /usr/local/lib/python3.12/site-packages/ /usr/local/lib/python3.12/site-packages/
COPY --from=base /usr/local/bin/ /usr/local/bin/
COPY . /app

EXPOSE 8000

CMD fastapi run
