# SMTP Catcher

Simple tool I wrote to catch emails, whit live update and email download/preview.

## Simple:

- Deployable using docker or in virtualenv with minimal requirements.
- Catching all kind of emails: txt / html, also with attachments.
- Simple Web interface with email preview.
- Live update on incomig emails (using web-sockets for notifications).
- Allows download email as `.eml` file.

## Requirements:

Only required if You want to run catcher in virtualenv, not in docker.
- Python 3.5 (or higher)
- peewee
- flask

## Run in docker

Ready `Dockerfile` is ready to use and run Catcher without any modification.
Two scripts are provided to allow easy run SMTP Catcher in docker:
- `run.sh` - which build and run SMTP Cather in console with logging
- `run_as_daemon.sh` - which start and detach, to allow it to work in background.

After starting go to: [http://127.0.0.1:8026/]

## Using

Without any changes web interface is running on port: 8025, SMTP server on port 1025. Additionally web socket server is running on 8026.

Port numbers used by `run.sh` and `run_as_daemon.sh` are defined in `ports.sh` file. You can change it freely, but remember that port 25 used by regular SMTP servers can be used only with root privileges.

### SimpleWebSocket library

SMTP Catcher is using web socket server library grabbed from here:
[github](https://github.com/dpallot/simple-websocket-server/blob/master/SimpleWebSocketServer/SimpleWebSocketServer.py)
I modified code code of this library, to allow it to work with Python 3.5,
and to make it little more readable (PEP 8).

