# coding: utf-8
import smtpd
from datetime import datetime
from email.parser import BytesHeaderParser
from email.header import decode_header
from .settings import conf
from .database import Message, prepare_db
from .log import logger


class DumpingServer(smtpd.SMTPServer):

    def parse_headers(self, rawdata):
        from email.parser import BytesHeaderParser
        parser = BytesHeaderParser()
        msg = parser.parsebytes(rawdata)

        def header(name, default):
            res = msg.get(name)
            if res is None:
                return default
            res = decode_header(res)[0][0]
            if type(res) == bytes:
                res = str(res, 'utf-8', 'ignore')
            return res.strip()

        return {'subject': header('Subject', '<no subject>'),
                'tag':  header('X-Tag', '')}

    def process_message(self, peer, mailfrom, rcpttos, data, **kwargs):
        global pipe_send
        msg = Message()
        msg.time = datetime.now()
        msg.addr_from = mailfrom
        msg.addr_to = ", ".join(rcpttos)
        msg.raw_data = data
        msg.size = len(data)

        headers = self.parse_headers(data)
        msg.subject = headers['subject']
        if headers['tag']:
            msg.add_tag(headers['tag'])
            # msg.raw_tags = headers['tag']

        dblocker.acquire()
        try:
            msg.save()
        finally:
            dblocker.release()
        logger.debug(str(msg))

        pipe_send.send(str(msg.id))
        return None


def run_smtpd(dblock, dbfile, psend):
    '''
    Run SMTP server as daemon

    dblock - database access semaphore
    dbfile - name of sqlite database file
    psend - multiprocessing communication pipe, sender side
    '''
    import asyncore
    global dblocker, pipe_send
    dblocker = dblock
    pipe_send = psend
    dblocker.acquire()
    try:
        prepare_db(dbfile)
    finally:
        dblocker.release()
    logger.info("Starting SMTP server: %s:%s" % (conf.SMTP_ADDRESS, conf.SMTP_PORT))
    srv = DumpingServer(
        (conf.SMTP_ADDRESS, int(conf.SMTP_PORT)),
        None,
        enable_SMTPUTF8=True,
        decode_data=False)
    try:
        asyncore.loop()
    except KeyboardInterrupt:
        pass
    logger.info("Stopping SMTP server")
