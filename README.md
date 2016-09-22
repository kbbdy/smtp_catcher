# SMTP Catcher

Simple SMTP server catching all incoming emails.

- Catch all kind of emails: txt / html, also with attachments.
- Simple Web interface with email preview.
- Web interface show incoming emails instantly (using web-sockets for notifications).
- Allows download email as .eml file.

## Requirements:

- Python >= 3.5
- peewee
- flask

## Run in docker

Prepared Dockerfile allows to run without any configuration.
Container is created using `python-3.5-alpine` as base image.


docker build --rm=True -t smtpcatcher .

docker run --rm -it smtpcatcher /app/start.py

docker run --rm -it smtpcatcher /bin/bath


