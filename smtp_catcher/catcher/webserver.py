# coding: utf-8
import os
from flask import Flask, url_for, render_template, redirect, make_response, abort
import peewee as pw
from .database import Message, prepare_db, all_tags
from .settings import conf
from .log import logger
from .email_viewer import EmailViewer


ROOT_PATH = os.path.dirname(os.path.abspath(__file__))
app = Flask("SMTP Mail Catcher",
            template_folder=os.path.join(ROOT_PATH, 'templates'),
            static_folder=os.path.join(ROOT_PATH, 'static'),
            )


def get_message(msgid):
    '''
    Return message object
    '''
    dblocker.acquire()
    try:
        return Message.get(id=msgid)
    except pw.DoesNotExist:
        return None
    finally:
        dblocker.release()


def get_messages():
    '''
    Load messages from DB
    '''
    lst = []
    dblocker.acquire()
    try:
        for m in Message.select().order_by(-Message.time).iterator():
            m.url_eml = url_for('download_eml', msgid=m.id)
            m.url_view = url_for('view_message', msgid=m.id)
            lst.append(m)
    finally:
        dblocker.release()
    return lst


@app.route("/")
def main():
    '''
    Main page with message list
    '''
    lst = get_messages()
    context = {}
    context['title'] = "Messages"
    context['messages'] = lst
    context['count'] = len(lst)
    context['tags'] = all_tags()
    return render_template('index.html', **context)


@app.route("/empty")
def empty():
    '''
    Empty page is used to fill blank message view.
    '''
    context = {}
    return render_template('empty.html', **context)


@app.route("/messages")
def message_list():
    '''
    Message list as table body, used on message list reload
    and on automatic refresh
    '''
    all_tags()
    lst = get_messages()
    context = {}
    context['messages'] = lst
    context['count'] = len(lst)
    context['tags'] = list(all_tags())
    return render_template('message_list.html', **context)


@app.route("/eml/<int:msgid>")
def download_eml(msgid):
    '''
    Download message as eml file
    '''
    dblocker.acquire()
    try:
        msg = Message.get(id=msgid)
    finally:
        dblocker.release()
    response = make_response(msg.raw_data)
    response.headers["Content-Disposition"] = "attachment; filename=message_%i.eml" % msgid
    response.headers["Content-Type"] = "message/rfc822"
    return response


@app.route("/clear")
def clear_messages():
    '''
    Clear database and redirect to main page
    '''
    dblocker.acquire()
    try:
        query = Message.delete()
        query.execute()
    finally:
        dblocker.release()
    return redirect("/")


@app.route("/view/<int:msgid>")
def view_message(msgid):
    '''
    Return message HTML body.
    '''
    msg = get_message(msgid)
    if msg is None:
        abort(404)
    ev = EmailViewer("/view/%i/" % msgid)
    ev.load_from_string(msg.raw_data)
    msg.new = False
    dblocker.acquire()
    try:
        msg.save()
    finally:
        dblocker.release()
    return ev.processed_body()


@app.route("/view/<int:msgid>/<string:filename>")
def view_message_static(msgid, filename):
    '''
    Return image embedded in email message body.
    '''
    msg = get_message(msgid)
    if msg is None:
        abort(404)
    ev = EmailViewer()
    ev.load_from_string(msg.raw_data)
    mime_type, raw_data = ev.media_file(filename)
    response = make_response(raw_data)
    response.headers["Content-Type"] = mime_type
    return response


def run_web_server(dblock, dbfile):
    '''
    Run web interface server daemon

    dblock - database access semaphore
    dbfile - name of sqlite database file
    '''
    global dblocker
    dblocker = dblock
    logger.info("Starting web server")
    dblocker.acquire()
    try:
        prepare_db(dbfile)
    finally:
        dblocker.release()
    try:
        app.run(
            debug=False,
            host=conf.WEB_ADDRESS,
            port=int(conf.WEB_PORT),
        )
    except KeyboardInterrupt:
        pass
    logger.info("Stopping web server")
