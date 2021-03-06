#!/usr/bin/env python3
# coding: utf-8
import os
import multiprocessing
from catcher.settings import Setup
cnf = os.path.abspath(os.path.join(os.path.dirname(__file__), 'settings.conf'))
Setup(cnf)

from catcher.mailcatcher import run_smtpd
from catcher.webserver import run_web_server
from catcher.notifier import run_socket_server


if __name__ == '__main__':
    from catcher.log import logger
    from catcher.settings import conf
    logger.info("Starting email catcher")
    ws = os.environ.get('WEBSOCK', None)
    if ws:
        outer_sock_port = ws
    else:
        outer_sock_port = conf['WEBSOCKET_PORT']

    dblock = multiprocessing.Lock()
    socklock = multiprocessing.Lock()

    # parse input parameters
    import argparse
    parser = argparse.ArgumentParser(description='SMTP mail catcher')
    parser.add_argument('-f', action='store', dest='dbfile', default=None, help='Database file name')
    args = parser.parse_args()

    # setup communication pipe
    conn_recv, conn_send = multiprocessing.Pipe()

    # set database file
    if args.dbfile:
        dbfile = args.dbfile
    else:
        from catcher.settings import conf
        dbfile = conf['DATABASE_FILE']

    # create and run process
    smtp_proc = multiprocessing.Process(
        target=run_smtpd,
        name='SMTP',
        kwargs={'dblock': dblock, 'dbfile': dbfile, 'psend': conn_send}
        )
    web_server = multiprocessing.Process(
        target=run_web_server,
        name='web',
        kwargs={'dblock': dblock, 'dbfile': dbfile, 'outer_sock_port': outer_sock_port}
        )
    socketio_server = multiprocessing.Process(
        target=run_socket_server,
        name='sock',
        kwargs={'socklock': socklock, 'pipe_recv': conn_recv}
        )

    socketio_server.start()
    smtp_proc.start()
    web_server.start()
