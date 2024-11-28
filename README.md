# Secret Santa draw

## TLDR

This repository contains the source code of a RESTFul API which allows the generation of *Secret Santa* draws.

**(This project is in MVP state)**

## How to play with the API

[!NOTE]
You will need [docker](https://www.docker.com) and its
[compose](https://docs.docker.com/compose/) tool to build and run this
API so make sure they are installed on your environment.

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

