# Secret Santa draw

## Introduction

This repository contains the source code of a RESTFul API which allows the generation of *Secret Santa* draws.

**(This project is in MVP state)**

## How to play with the API

> [!NOTE]
> You will need [docker](https://www.docker.com) and its
> [compose](https://docs.docker.com/compose/) tool to build and run this
> API so make sure they are installed on your environment.

**The first time**, run the following command:

```bash
$ docker compose build
```

It will generate a docker image containing the API code and dependencies.

Then, just run the following command to start everything:

```bash
$ docker compose up
```

Once everything is started, you will be able to access the API documentation at this address:

http://localhost:8000/docs

## Run tests

> [!NOTE]
> You will need pipenv to install required dependencies.

Run the following commands to setup test environment:

```bash
$ pip install pipenv
$ pipenv --python 3.12
$ pipenv install --dev
```

Then, you can run the test suite as follows:

```bash
$ pipenv run pytest secret_santa/tests.py
```
